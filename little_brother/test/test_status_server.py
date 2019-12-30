# -*- coding: utf-8 -*-

#    Copyright (C) 2019  Marcus Rickert
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
from little_brother import master_connector
from little_brother import settings
from little_brother import status_server
from little_brother.test import test_client_process_handler
from little_brother.test import test_data
from little_brother.test import test_persistence
from little_brother.test import test_rule_handler
from python_base_app.test import base_test

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "hello!"


class TestStatusServer(base_test.BaseTestCase):

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

    @staticmethod
    def create_dummy_status_server(p_process_handlers=None, p_ruleset_configs=None):

        if p_process_handlers is None:
            p_process_handlers = {}

        if p_ruleset_configs is None:
            p_ruleset_configs = {}

        _persistence = test_persistence.TestPersistence.create_dummy_persistence()
        _rule_handler = test_rule_handler.TestRuleHandler.create_dummy_rule_handler(p_ruleset_configs=p_ruleset_configs)

        master_connector_config = master_connector.MasterConnectorConfigModel()
        _master_connector = master_connector.MasterConnector(p_config=master_connector_config)

        app_control_config = app_control.AppControlConfigModel()
        _app_control = app_control.AppControl(
            p_config=app_control_config,
            p_debug_mode=False,
            p_process_handlers=p_process_handlers,
            p_persistence=_persistence,
            p_rule_handler=_rule_handler,
            p_notification_handlers=[],
            p_rule_set_configs=p_ruleset_configs,
            p_master_connector=_master_connector,
            p_login_mapping=test_data.LOGIN_MAPPING)

        status_server_config = status_server.StatusServerConfigModel()
        status_server_config.admin_username = ADMIN_USERNAME
        status_server_config.admin_password = ADMIN_PASSWORD
        status_server_config.app_secret = "secret!"

        status_server_config.port = int(os.getenv("STATUS_SERVER_PORT", "5555"))

        _status_server = status_server.StatusServer(
            p_config=status_server_config,
            p_package_name=app.PACKAGE_NAME,
            p_app_control=_app_control,
            p_master_connector=_master_connector,
            p_is_master=True)

        return _status_server

    @staticmethod
    def get_selenium_driver():

        if os.getenv("SELENIUM_CHROME_DRIVER") is not None:
            options = selenium.webdriver.ChromeOptions()
            options.add_argument('headless')

            # See https://stackoverflow.com/questions/50642308
            options.add_argument('no-sandbox')
            options.add_argument('disable-dev-shm-usage')

            return selenium.webdriver.Chrome(chrome_options=options)

        else:
            return selenium.webdriver.PhantomJS()

    def test_start_and_stop(self):

        _status_server = self.create_dummy_status_server()
        _status_server.start_server()
        _status_server.stop_server()
        _status_server.destroy()

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_about(self):

        _status_server = None

        try:
            _status_server = self.create_dummy_status_server()
            _status_server.start_server()

            driver = self.get_selenium_driver()
            driver.get(_status_server.get_url(p_internal=False, p_rel_url=status_server.ABOUT_REL_URL))
            assert "LittleBrother" in driver.title

            xpath = "//DIV[DIV[1] = 'Version' and DIV[2] = '{version}']"
            driver.find_element_by_xpath(xpath.format(version=settings.settings['version']))

            xpath = "//DIV[DIV[1] = 'Debian Package Revision' and DIV[2] = '{debian_package_revision}']"
            driver.find_element_by_xpath(
                xpath.format(debian_package_revision=settings.settings['debian_package_revision']))

            driver.close()

        except Exception as e:
            raise e

        finally:
            if _status_server is not None:
                _status_server.stop_server()
                _status_server.destroy()

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_index_without_process(self):

        _status_server = None

        try:
            _status_server = self.create_dummy_status_server()
            _status_server.start_server()

            driver = self.get_selenium_driver()

            driver.get(_status_server.get_url(p_internal=False, p_rel_url=status_server.INDEX_REL_URL))
            assert "LittleBrother" in driver.title

            xpath = "//DIV[DIV[1] = 'User' and DIV[2] = 'Context' and DIV[12] = 'Reasons']"
            driver.find_element_by_xpath(xpath)

            driver.close()

        except Exception as e:
            raise e

        finally:
            _status_server.stop_server()
            _status_server.destroy()

    def get_status_server_using_ruleset_configs(self, p_ruleset_configs):

        process_handlers = self.get_dummy_process_handlers()

        _status_server = self.create_dummy_status_server(
            p_process_handlers=process_handlers, p_ruleset_configs=p_ruleset_configs)
        _status_server.start_server()

        _appcontrol = _status_server._appcontrol

        _appcontrol.retrieve_user_mappings()
        _appcontrol.start()
        _appcontrol.scan_processes(
            p_process_handler=process_handlers[client_process_handler.ClientProcessHandler.__name__])
        _appcontrol.check()
        _appcontrol.stop()

        return _status_server

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_index_with_process_no_restrictions(self):

        _status_server = None

        try:

            ruleset_configs = test_data.get_dummy_ruleset_configs(
                p_ruleset_config=test_data.RULESET_CONFIGS_USER1_NO_RESTRICTIONS)
            _status_server = self.get_status_server_using_ruleset_configs(ruleset_configs)

            driver = self.get_selenium_driver()

            driver.get(_status_server.get_url(p_internal=False, p_rel_url=status_server.INDEX_REL_URL))
            assert "LittleBrother" in driver.title

            xpath = "//DIV[DIV[1] = 'User' and DIV[2] = 'Context' and DIV[12] = 'Reasons']"
            driver.find_element_by_xpath(xpath)

            driver.close()

        except Exception as e:
            raise e

        finally:
            _status_server.stop_server()
            _status_server.destroy()

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_index_with_process_all_restrictions(self):

        _status_server = None

        try:

            ruleset_configs = test_data.get_dummy_ruleset_configs(
                p_ruleset_config=test_data.RULESET_CONFIGS_USER1_ALL_RESTRICTIONS)
            _status_server = self.get_status_server_using_ruleset_configs(ruleset_configs)

            driver = self.get_selenium_driver()

            driver.get(_status_server.get_url(p_internal=False, p_rel_url=status_server.INDEX_REL_URL))
            assert "LittleBrother" in driver.title

            xpath = "//DIV[DIV[1] = 'User' and DIV[2] = 'Context' and DIV[12] = 'Reasons']"
            driver.find_element_by_xpath(xpath)

            driver.close()

        except Exception as e:
            raise e

        finally:
            _status_server.stop_server()
            _status_server.destroy()

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_admin_without_process(self):

        _status_server = None

        try:
            _status_server = self.create_dummy_status_server()
            _status_server.start_server()

            driver = self.get_selenium_driver()

            # When we load the admin page the first time...
            driver.get(_status_server.get_url(p_internal=False, p_rel_url=status_server.ADMIN_REL_URL))
            assert "LittleBrother" in driver.title

            # ...we end up on the login page.
            elem = driver.find_element_by_name("username")
            elem.clear()
            elem.send_keys(ADMIN_USERNAME)

            elem = driver.find_element_by_name("password")
            elem.clear()
            elem.send_keys(ADMIN_PASSWORD)
            elem.send_keys(Keys.RETURN)

            # After logging in we are on the admin page
            xpath = "//FORM/DIV/DIV[DIV[1] = 'User' and DIV[2] = '']"
            driver.find_element_by_xpath(xpath)

            # The second we call the admin page.
            driver.get(_status_server.get_url(p_internal=False, p_rel_url=status_server.ADMIN_REL_URL))
            assert "LittleBrother" in driver.title

            # we are on the admin page right away...
            xpath = "//FORM/DIV/DIV[DIV[1] = 'User' and DIV[2] = '']"
            driver.find_element_by_xpath(xpath)

            driver.close()

        except Exception as e:
            raise e

        finally:
            _status_server.stop_server()
            _status_server.destroy()

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_admin_with_process(self):

        _status_server = None

        try:
            ruleset_configs = test_data.get_dummy_ruleset_configs(
                p_ruleset_config=test_data.RULESET_CONFIGS_USER1_ALL_RESTRICTIONS)
            _status_server = self.get_status_server_using_ruleset_configs(ruleset_configs)

            driver = self.get_selenium_driver()

            # When we load the admin page the first time...
            driver.get(_status_server.get_url(p_internal=False, p_rel_url=status_server.ADMIN_REL_URL))
            assert "LittleBrother" in driver.title

            # ...we end up on the login page.
            elem = driver.find_element_by_name("username")
            elem.clear()
            elem.send_keys(ADMIN_USERNAME)

            elem = driver.find_element_by_name("password")
            elem.clear()
            elem.send_keys(ADMIN_PASSWORD)
            elem.send_keys(Keys.RETURN)

            # After logging in we are on the admin page
            xpath = "//FORM/DIV/DIV[DIV[1] = 'User' and DIV[2] = '']"
            driver.find_element_by_xpath(xpath)

            # The second we call the admin page.
            driver.get(_status_server.get_url(p_internal=False, p_rel_url=status_server.ADMIN_REL_URL))
            assert "LittleBrother" in driver.title

            # we are on the admin page right away...
            xpath = "//FORM/DIV/DIV[DIV[1] = 'User' and DIV[2] = '']"
            driver.find_element_by_xpath(xpath)

            driver.close()

        except Exception as e:
            raise e

        finally:
            _status_server.stop_server()
            _status_server.destroy()


if __name__ == "__main__":
    unittest.main()
