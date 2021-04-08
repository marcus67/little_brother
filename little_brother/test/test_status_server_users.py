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

import unittest

import selenium.webdriver.support.ui

from little_brother import dependency_injection
from little_brother import status_server
from little_brother.persistence.persistent_user import User
from little_brother.persistence.persistent_user_entity_manager import UserEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.test.base_test_status_server import BaseTestStatusServer
from python_base_app.test import base_test
from python_base_app.test import test_unix_user_handler


class TestStatusServerUsers(BaseTestStatusServer):

    def call_user_page(self, p_driver):
        # When we load the admin page the first time...
        p_driver.get(self._status_server.get_url(p_internal=False, p_rel_url=status_server.USERS_REL_URL))
        assert "LittleBrother" in self._driver.title

        # ...we end up on the login page.
        self.login()

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_users(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        self.login_users()

        # The second time we call the users page.
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=status_server.USERS_REL_URL))
        assert "LittleBrother" in self._driver.title
        assert "User Configuration" in self._driver.title

        # we are on the users page right away...
        self.check_empty_user_list()

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_users_add_and_delete_user(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        self.login_users()

        elem = self._driver.find_element_by_id("username")
        dropdown = selenium.webdriver.support.ui.Select(elem)
        dropdown.select_by_value(test_unix_user_handler.USER_2_UID)

        add_button = self._driver.find_element_by_id("add_user")
        add_button.click()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]

        with SessionContext(self._persistence) as session_context:
            user = user_entity_manager.get_by_username(
                p_session_context=session_context, p_username=test_unix_user_handler.USER_2_UID)
            self.assertEqual(test_unix_user_handler.USER_2_UID, user.username)

        user_id = user.id

        xpath = "//DIV/A[@aria-controls='detailsuser_1']"
        self._driver.find_element_by_xpath(xpath)

        delete_button = self._driver.find_element_by_id("delete_user_1")
        delete_button.click()

        delete_button = self._driver.find_element_by_id("delete_user_1-modal-confirm")
        # See https://stackoverflow.com/questions/56194094/how-to-fix-this-issue-element-not-interactable-selenium-python
        self._driver.execute_script("arguments[0].click();", delete_button)

        with SessionContext(self._persistence) as session_context:
            user = user_entity_manager.get_by_id(
                p_session_context=session_context, p_id=user_id)
            self.assertIsNone(user)

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_users_edit_user(self):
        NEW_USER_FIRST_NAME = "Micky"
        NEW_USER_LAST_NAME = "Mouse"
        NEW_USER_LOCALE = "de"
        NEW_USER_ACTIVE = True
        NEW_USER_PROCESS_NAME_PATTERN = "bash"

        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]

        with SessionContext(self._persistence) as session_context:
            user_entity_manager.add_new_user(
                p_session_context=session_context, p_username=test_unix_user_handler.USER_2_UID, p_locale="en")

        self.login_users()

        elem = self._driver.find_element_by_id("user_1_first_name")
        # See https://stackoverflow.com/questions/22528456/how-to-replace-default-values-in-the-text-field-using-selenium-python/33361371
        self._driver.execute_script("arguments[0].value = '{value}'".format(value=NEW_USER_FIRST_NAME), elem)

        elem = self._driver.find_element_by_id("user_1_last_name")
        self._driver.execute_script("arguments[0].value = '{value}'".format(value=NEW_USER_LAST_NAME), elem)

        elem = self._driver.find_element_by_id("user_1_process_name_pattern")
        self._driver.execute_script("arguments[0].value = '{value}'".format(value=NEW_USER_PROCESS_NAME_PATTERN), elem)

        elem = self._driver.find_element_by_id("user_1_locale")
        self._driver.execute_script("arguments[0].value = '{value}'".format(value=NEW_USER_LOCALE), elem)

        check_box = self._driver.find_element_by_id("user_1_active")
        self._driver.execute_script("arguments[0].click();", check_box)

        save_button = self._driver.find_element_by_id("save")
        self._driver.execute_script("arguments[0].click();", save_button)

        with SessionContext(self._persistence) as session_context:
            user: User = user_entity_manager.get_by_username(
                p_session_context=session_context, p_username=test_unix_user_handler.USER_2_UID)
            self.assertEqual(test_unix_user_handler.USER_2_UID, user.username)
            self.assertEqual(NEW_USER_FIRST_NAME, user.first_name)
            self.assertEqual(NEW_USER_LAST_NAME, user.last_name)
            self.assertEqual(NEW_USER_PROCESS_NAME_PATTERN, user.process_name_pattern)
            self.assertEqual(NEW_USER_ACTIVE, user.active)
            self.assertEqual(NEW_USER_LOCALE, user.locale)


if __name__ == "__main__":
    unittest.main()
