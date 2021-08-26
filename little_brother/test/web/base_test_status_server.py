# -*- coding: utf-8 -*-

#    Copyright (C) 2019-2021  Marcus Rickert
#
#    See https://github.com/marcus67/little_brother
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import datetime
import os
import unittest

import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from little_brother import app
from little_brother import client_process_handler
from little_brother import constants
from little_brother import dependency_injection
from little_brother.admin_data_handler import AdminDataHandler
from little_brother.api import master_connector
from little_brother.api.master_connector import MasterConnector
from little_brother.api.version_checker import VersionCheckerConfigModel, VersionChecker, SOURCEFORGE_CHANNEL_INFOS
from little_brother.app_control import AppControl, AppControlConfigModel
from little_brother.persistence.persistence import Persistence
from little_brother.persistence.persistent_user_entity_manager import UserEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.prometheus import PrometheusClient
from little_brother.rule_handler import RuleHandler
from little_brother.test import test_client_process_handler
from little_brother.test import test_data
from little_brother.test import test_rule_handler
from little_brother.test.persistence import test_persistence
from little_brother.user_manager import UserManager
from little_brother.web import web_server
from python_base_app import locale_helper
from python_base_app.base_user_handler import BaseUserHandler
from python_base_app.test import base_test
from python_base_app.test import test_unix_user_handler

XPATH_EMPTY_USER_LIST = "//FORM/DIV/DIV[DIV[1] = 'User' and DIV[2] = '']"
XPATH_EMPTY_DEVICE_LIST = "//FORM/DIV/DIV[DIV[1] = 'Device' and DIV[2] = '']"


class BaseTestStatusServer(base_test.BaseTestCase):

    def setUp(self):

        dependency_injection.reset()
        self._status_server = None
        self._driver = None

    def tearDown(self) -> None:

        if self._status_server is not None:
            self._status_server.stop_server()
            self._status_server.destroy()
            self._status_server = None

        if self._driver is not None:
            self._driver.close()
            self._driver = None

    @staticmethod
    def get_dummy_process_handlers():

        now = datetime.datetime.now()
        process_start_time = now + datetime.timedelta(seconds=-1)

        process_handler = test_client_process_handler.TestClientProcessHandler.get_dummy_process_handler(
            p_reference_time=now, p_processes=test_data.get_active_processes(p_start_time=process_start_time))

        process_handlers = {
            process_handler.id: process_handler
        }

        return process_handlers

    def create_dummy_status_server(self, p_process_handlers=None):

        # TODO: Add rule set configs as parameters again and migrate them into the datamodel

        if p_process_handlers is None:
            p_process_handlers = {}

        test_persistence.TestPersistence.create_dummy_persistence(self._logger)
        self._persistence = dependency_injection.container[Persistence]

        self._rule_handler = test_rule_handler.TestRuleHandler.create_dummy_rule_handler(
            p_persistence=self._persistence)
        dependency_injection.container[RuleHandler] = self._rule_handler

        master_connector_config = master_connector.MasterConnectorConfigModel()
        self._master_connector = master_connector.MasterConnector(p_config=master_connector_config)
        dependency_injection.container[MasterConnector] = self._master_connector

        dependency_injection.container[PrometheusClient] = None

        self._user_handler = test_unix_user_handler.TestUnixUserHandler.create_dummy_unix_user_handler()
        dependency_injection.container[BaseUserHandler] = self._user_handler

        app_control_config = AppControlConfigModel()
        self._admin_data_handler = AdminDataHandler(p_config=app_control_config)
        dependency_injection.container[AdminDataHandler] = self._admin_data_handler

        self._app_control = AppControl(
            p_config=app_control_config,
            p_debug_mode=False,
            p_process_handlers=p_process_handlers,
            p_device_handler=None,
            p_notification_handlers=[],
            p_login_mapping=test_data.LOGIN_MAPPING,
            p_locale_helper=locale_helper.LocaleHelper())

        dependency_injection.container[AppControl] = self._app_control

        status_server_config = web_server.StatusServerConfigModel()
        status_server_config.app_secret = "123456"

        status_server_config.port = int(os.getenv("STATUS_SERVER_PORT", "5555"))

        version_checker_config = VersionCheckerConfigModel()
        version_checker = VersionChecker(p_config=version_checker_config, p_channel_infos=SOURCEFORGE_CHANNEL_INFOS)
        dependency_injection.container[VersionChecker] = version_checker

        self._status_server = web_server.StatusServer(
            p_config=status_server_config,
            p_package_name=app.PACKAGE_NAME,
            p_app_control=self._app_control,
            p_master_connector=self._master_connector,
            p_is_master=True,
            p_user_handler=self._user_handler,
            p_locale_helper=locale_helper.LocaleHelper(),
            p_languages=constants.LANGUAGES)

    def create_selenium_driver(self):

        if os.getenv("SELENIUM_CHROME_DRIVER") is not None:
            options = selenium.webdriver.ChromeOptions()
            options.add_argument('headless')

            # See https://stackoverflow.com/questions/50642308
            options.add_argument('no-sandbox')
            options.add_argument('disable-dev-shm-usage')

            self._driver = selenium.webdriver.Chrome(options=options)

        else:
            self._driver = selenium.webdriver.PhantomJS()

    def create_status_server_using_ruleset_configs(self, p_ruleset_configs):

        process_handlers = self.get_dummy_process_handlers()

        self.create_dummy_status_server(p_process_handlers=process_handlers)
        self._status_server.start_server()

        user_manager = dependency_injection.container[UserManager]

        user_manager.retrieve_user_mappings()
        self._app_control.start()
        self._app_control._process_handler_manager.scan_processes(
            p_process_handler=process_handlers[client_process_handler.ClientProcessHandler.__name__])
        self._app_control.check()
        self._app_control.stop()

    def login_users(self):

        # When we load the admin page the first time...
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=constants.USERS_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        # ...we end up on the login page.
        self.login()
        # After logging in we are on the users page
        assert "User Configuration" in self._driver.title
        self.check_empty_user_list()

    def login_devices(self):

        # When we load the admin page the first time...
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=constants.DEVICES_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        # ...we end up on the login page.
        self.login()
        # After logging in we are on the devices page
        assert "Device Configuration" in self._driver.title
        self.check_empty_device_list()

    def login_admin(self):

        # When we load the admin page the first time...
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=constants.ADMIN_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        # ...we end up on the login page.
        self.login()
        # After logging in we are on the devices page
        assert "Administration" in self._driver.title

    def check_empty_user_list(self):
        self._driver.find_element_by_xpath(XPATH_EMPTY_USER_LIST)

    def check_empty_device_list(self):
        self._driver.find_element_by_xpath(XPATH_EMPTY_DEVICE_LIST)

    def login(self):
        elem = self._driver.find_element_by_name("username")
        elem.clear()
        elem.send_keys(test_unix_user_handler.ADMIN_USER)

        elem = self._driver.find_element_by_name("password")
        elem.clear()
        elem.send_keys(test_unix_user_handler.ADMIN_PASSWORD)
        elem.send_keys(Keys.RETURN)

    def click(self, p_elem):
        # See https://stackoverflow.com/questions/56194094/how-to-fix-this-issue-element-not-interactable-selenium-python
        self._driver.execute_script("arguments[0].click();", p_elem)

    def set_value(self, p_elem, p_value):

        self.assertIsInstance(p_elem, WebElement)
        # See https://stackoverflow.com/questions/22528456/how-to-replace-default-values-in-the-text-field-using-selenium-python/33361371
        self._driver.execute_script("arguments[0].value = '{value}'".format(value=p_value), p_elem)

    def add_new_user(self, p_user_entity_manager: UserEntityManager) -> int:
        with SessionContext(self._persistence) as session_context:
            user_id = p_user_entity_manager.add_new_user(
                p_session_context=session_context, p_username=self.get_new_user_name(), p_locale="en")

        session = session_context.get_session()
        user = p_user_entity_manager.get_by_id(p_session_context=session_context, p_id=user_id)
        # activate monitoring of user so that it will show up on the admin page
        user.active = True
        session.commit()

        user_manager : UserManager = dependency_injection.container[UserManager]

        user_manager.add_monitored_user(p_username=self.get_new_user_name())
        user_manager.retrieve_user_mappings()

        return user_id

    def get_new_user_name(self):
        return test_unix_user_handler.USER_2_UID


if __name__ == "__main__":
    unittest.main()
