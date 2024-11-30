# -*- coding: utf-8 -*-

#    Copyright (C) 2019-2024  Marcus Rickert
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
import time
import unittest

import selenium
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from little_brother import app, token_handler
from little_brother import client_process_handler
from little_brother import constants
from little_brother import dependency_injection
from little_brother.admin_data_handler import AdminDataHandler
from little_brother.api import master_connector, api_view_handler
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
from little_brother.web.web_server import StatusServer
from python_base_app import locale_helper
from python_base_app.base_user_handler import BaseUserHandler
from python_base_app.test import base_test
from python_base_app.test import test_unix_user_handler

DEFAULT_ANGULAR_RENDERING_TIMEOUT = 5  # seconds

XPATH_EMPTY_USER_LIST = "//FORM/DIV/DIV[DIV[1] = 'User' and DIV[2] = '']"
XPATH_EMPTY_DEVICE_LIST = "//FORM/DIV/DIV[DIV[1] = 'Device' and DIV[2] = '']"


class BaseTestStatusServerAngular(base_test.BaseTestCase):

    def setUp(self):

        dependency_injection.reset()
        self._status_server: StatusServer | None = None
        self._driver: WebDriver | None = None

    def tearDown(self) -> None:

        if self._status_server is not None:
            self._status_server.stop_server()
            self._status_server.destroy()
            self._status_server = None

        if self._driver is not None:
            self._driver.close()
            self._driver.quit()
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

    def create_dummy_status_server(self, p_process_handlers=None, p_create_complex_handlers=False):

        if p_process_handlers is None:
            p_process_handlers = {}

        test_persistence.TestPersistence.create_dummy_persistence(self._logger)
        self._persistence = dependency_injection.container[Persistence]

        self._rule_handler = test_rule_handler.TestRuleHandler.create_dummy_rule_handler(
            p_persistence=self._persistence, p_create_complex_handlers=p_create_complex_handlers)
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

        status_server_config.port = self.get_status_server_port()

        status_server_config.angular_gui_base_url = "/AngularLittleBrother"
        status_server_config.angular_api_base_url = "/AngularLittleBrother/angular-api"
        status_server_config.angular_gui_active = True

        version_checker_config = VersionCheckerConfigModel()
        version_checker = VersionChecker(p_config=version_checker_config, p_channel_infos=SOURCEFORGE_CHANNEL_INFOS)
        dependency_injection.container[VersionChecker] = version_checker
        configs = {
            web_server.SECTION_NAME: status_server_config,
            api_view_handler.SECTION_NAME: api_view_handler.ApiViewHandlerConfigModel(),
            token_handler.SECTION_NAME: token_handler.BaseTokenHandlerConfigModel()
        }

        self._status_server = web_server.StatusServer(
            p_configs=configs,
            p_package_name=app.PACKAGE_NAME,
            p_app_control=self._app_control,
            p_master_connector=self._master_connector,
            p_is_master=True,
            p_user_handler=self._user_handler,
            p_locale_helper=locale_helper.LocaleHelper(),
            p_languages=constants.LANGUAGES)

    def create_selenium_driver(self):

        options = selenium.webdriver.ChromeOptions()

        if os.getenv("NEW_CHROME"):
            options.add_argument(f"--explicitly-allowed-ports={self._status_server.get_port()}")
            # https://stackoverflow.com/questions/77585943/selenium-headless-chrome-empty-page-source-not-ua-issue
            options.add_argument('--headless=new')

        else:
            options.add_argument('--headless')

        # See https://stackoverflow.com/questions/50642308
        options.add_argument('no-sandbox')
        options.add_argument('disable-dev-shm-usage')
        options.add_argument("--incognito")

        chrome_binary = os.getenv("CHROME_BINARY")

        if chrome_binary:
            self._logger.info(f"Using Chrome binary at {chrome_binary}.")
            options.binary_location = os.getenv(chrome_binary)

        self._driver = selenium.webdriver.Chrome(options=options)

    def create_status_server_using_ruleset_configs(self, p_ruleset_configs, p_create_complex_handlers=False):

        process_handlers = self.get_dummy_process_handlers()

        self.create_dummy_status_server(p_process_handlers=process_handlers,
                                        p_create_complex_handlers=p_create_complex_handlers)
        self._status_server.start_server()

        user_manager = dependency_injection.container[UserManager]

        user_manager.retrieve_user_mappings()
        self._app_control.start()
        self._app_control._process_handler_manager.scan_processes(
            p_process_handler=process_handlers[client_process_handler.ClientProcessHandler.__name__])
        self._app_control.check()
        self._app_control.stop()

    # Wait for Angular to finish rendering
    def wait_for_angular(self):
        WebDriverWait(self._driver, DEFAULT_ANGULAR_RENDERING_TIMEOUT).until(
            lambda d: d.execute_script(
                'return window.getAllAngularTestabilities().findIndex(x=>!x.isStable()) === -1;'
            )
        )

    def check_empty_device_list(self):
        self._driver.find_element(By.XPATH, XPATH_EMPTY_DEVICE_LIST)

    def login(self):
        login_title = self.retrieve_element_by_id_with_timeout(p_id="login-title")
        assert "Little Brother Login" == login_title.text

        elem = self._driver.find_element(By.NAME, "username")
        elem.clear()
        elem.send_keys(test_unix_user_handler.ADMIN_USER)

        elem = self._driver.find_element(By.NAME, "password")
        elem.clear()
        elem.send_keys(test_unix_user_handler.ADMIN_PASSWORD)
        elem.send_keys(Keys.RETURN)

    def initial_login(self):
        self.select_angular_page("")
        self.login()
        self.wait_until_page_ready()
        assert constants.APPLICATION_NAME in self._driver.title

    def click(self, p_elem):
        # See https://stackoverflow.com/questions/56194094/how-to-fix-this-issue-element-not-interactable-selenium-python
        self._driver.execute_script("arguments[0].click();", p_elem)

    def set_value(self, p_elem, p_value):

        self.assertIsInstance(p_elem, WebElement)
        # See https://stackoverflow.com/questions/22528456/how-to-replace-default-values-in-the-text-field-using-selenium-python/33361371
        self._driver.execute_script("arguments[0].value = '{value}'".format(value=p_value), p_elem)

    def select_angular_page(self, p_rel_url: str | None = None) -> None:
        url = self._status_server.get_angular_url(p_rel_url=p_rel_url)

        self._logger.info(f"Downloading Angular page at {url}...")
        self._driver.get(url)

    def retrieve_element_by_id_with_timeout(self, p_id):
        return WebDriverWait(self._driver, DEFAULT_ANGULAR_RENDERING_TIMEOUT).until(
            ec.presence_of_element_located((By.ID, p_id))
        )

    def wait_until_page_ready(self):
        self.retrieve_element_by_id_with_timeout(p_id="page-ready")

    def switch_to_angular_page(self, p_button_id: str):

        button = self.retrieve_element_by_id_with_timeout(p_id=p_button_id)
        self.click(p_elem=button)
        self.wait_until_page_ready()

    def add_class_to_element(self, p_elem, p_class):
        self._driver.execute_script("arguments[0].classList.add(arguments[1]);", p_elem, p_class)

    def check_validation_error(self, p_validation_message):
        elem = self._driver.find_element(By.CLASS_NAME, "alert-danger")
        assert p_validation_message in elem.text

    def open_accordion(self, p_accordion_id):
        elem = self._driver.find_element(By.ID, p_accordion_id)
        # TODO: Hack: Open the accordion, better: check it is open and click on it if not...
        self.add_class_to_element(p_elem=elem, p_class="show")

    @staticmethod
    def wait_for_data_to_be_saved():
        # TODO: Hack!
        time.sleep(1)

    def add_new_user(self, p_user_entity_manager: UserEntityManager) -> int:
        with SessionContext(self._persistence) as session_context:
            user_id = p_user_entity_manager.add_new_user(
                p_session_context=session_context, p_username=self.get_new_user_name(), p_locale="en")

        session = session_context.get_session()
        user = p_user_entity_manager.get_by_id(p_session_context=session_context, p_id=user_id)
        # activate monitoring of user so that it will show up on the admin page
        user.active = True
        session.commit()

        user_manager: UserManager = dependency_injection.container[UserManager]

        user_manager.add_monitored_user(p_username=self.get_new_user_name())
        user_manager.retrieve_user_mappings()

        return user_id

    @staticmethod
    def get_new_user_name():
        return test_unix_user_handler.USER_2_UID

    def count_user_rows(self):
        return len(self._driver.find_elements(By.CLASS_NAME, 'user-row'))


if __name__ == "__main__":
    unittest.main()
