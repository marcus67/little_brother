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

from little_brother import app
from little_brother import app_control
from little_brother import client_process_handler
from little_brother import constants
from little_brother import dependency_injection
from little_brother import master_connector
from little_brother import status_server
from little_brother.test import test_client_process_handler
from little_brother.test import test_data
from little_brother.test import test_rule_handler
from little_brother.test.persistence import test_persistence
from python_base_app import locale_helper
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

        self._persistence = test_persistence.TestPersistence.create_dummy_persistence(self._logger)
        self._rule_handler = test_rule_handler.TestRuleHandler.create_dummy_rule_handler(
            p_persistence=self._persistence)

        master_connector_config = master_connector.MasterConnectorConfigModel()
        self._master_connector = master_connector.MasterConnector(p_config=master_connector_config)

        self._user_handler = test_unix_user_handler.TestUnixUserHandler.create_dummy_unix_user_handler()

        app_control_config = app_control.AppControlConfigModel()
        self._app_control = app_control.AppControl(
            p_config=app_control_config,
            p_debug_mode=False,
            p_process_handlers=p_process_handlers,
            p_device_handler=None,
            p_prometheus_client=None,
            p_persistence=self._persistence,
            p_rule_handler=self._rule_handler,
            p_notification_handlers=[],
            p_master_connector=self._master_connector,
            p_login_mapping=test_data.LOGIN_MAPPING,
            p_locale_helper=locale_helper.LocaleHelper(),
            p_user_handler=self._user_handler)

        status_server_config = status_server.StatusServerConfigModel()
        status_server_config.app_secret = "123456"

        status_server_config.port = int(os.getenv("STATUS_SERVER_PORT", "5555"))

        self._status_server = status_server.StatusServer(
            p_config=status_server_config,
            p_package_name=app.PACKAGE_NAME,
            p_app_control=self._app_control,
            p_master_connector=self._master_connector,
            p_persistence=self._persistence,
            p_is_master=True,
            p_user_handler=self._user_handler,
            p_locale_helper=locale_helper.LocaleHelper())

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

        self._app_control.retrieve_user_mappings()
        self._app_control.start()
        self._app_control.scan_processes(
            p_process_handler=process_handlers[client_process_handler.ClientProcessHandler.__name__])
        self._app_control.check()
        self._app_control.stop()


    def login_users(self):

        # When we load the admin page the first time...
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=status_server.USERS_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        # ...we end up on the login page.
        self.login()
        # After logging in we are on the users page
        assert "User Configuration" in self._driver.title
        self.check_empty_user_list()

    def login_devices(self):

        # When we load the admin page the first time...
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=status_server.DEVICES_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        # ...we end up on the login page.
        self.login()
        # After logging in we are on the devices page
        assert "Device Configuration" in self._driver.title
        self.check_empty_device_list()


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


if __name__ == "__main__":
    unittest.main()
