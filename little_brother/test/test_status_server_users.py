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
from little_brother.persistence.persistent_rule_set import RuleSet
from little_brother.persistence.persistent_rule_set_entity_manager import RuleSetEntityManager
from little_brother.persistence.persistent_user import User
from little_brother.persistence.persistent_user_entity_manager import UserEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.test.base_test_status_server import BaseTestStatusServer
from python_base_app.test import base_test
from python_base_app.test import test_unix_user_handler

NEW_USER_FIRST_NAME = "Micky"
NEW_USER_LAST_NAME = "Mouse"
NEW_USER_LOCALE = "de"
NEW_USER_ACTIVE = True
NEW_USER_PROCESS_NAME_PATTERN = "bash"

class TestStatusServerUsers(BaseTestStatusServer):

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
        self.click(delete_button)

        delete_button = self._driver.find_element_by_id("delete_user_1-modal-confirm")
        self.click(delete_button)

        with SessionContext(self._persistence) as session_context:
            user = user_entity_manager.get_by_id(
                p_session_context=session_context, p_id=user_id)
            self.assertIsNone(user)

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_users_edit_user(self):

        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]

        user_id = self.add_new_user(user_entity_manager)

        self.login_users()
        
        elem_prefix = "user_{id}_".format(id=user_id)

        elem = self._driver.find_element_by_id(elem_prefix + "first_name")
        self.set_value(p_elem=elem, p_value=NEW_USER_FIRST_NAME)

        elem = self._driver.find_element_by_id(elem_prefix + "last_name")
        self.set_value(p_elem=elem, p_value=NEW_USER_LAST_NAME)

        elem = self._driver.find_element_by_id(elem_prefix + "process_name_pattern")
        self.set_value(p_elem=elem, p_value=NEW_USER_PROCESS_NAME_PATTERN)

        elem = self._driver.find_element_by_id(elem_prefix + "locale")
        self.set_value(p_elem=elem, p_value=NEW_USER_LOCALE)

        check_box = self._driver.find_element_by_id(elem_prefix + "active")
        self.click(check_box)

        save_button = self._driver.find_element_by_id("save")
        self.click(save_button)

        with SessionContext(self._persistence) as session_context:
            user: User = user_entity_manager.get_by_username(
                p_session_context=session_context, p_username=test_unix_user_handler.USER_2_UID)
            self.assertEqual(test_unix_user_handler.USER_2_UID, user.username)
            self.assertEqual(NEW_USER_FIRST_NAME, user.first_name)
            self.assertEqual(NEW_USER_LAST_NAME, user.last_name)
            self.assertEqual(NEW_USER_PROCESS_NAME_PATTERN, user.process_name_pattern)
            self.assertEqual(NEW_USER_ACTIVE, user.active)
            self.assertEqual(NEW_USER_LOCALE, user.locale)

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_users_assign_rule_set(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]

        user_id = self.add_new_user(user_entity_manager)

        self.login_users()

        elem_name = "new_ruleset_user_{id}".format(id=user_id)
        add_button = self._driver.find_element_by_id(elem_name)
        self.click(add_button)

        with SessionContext(self._persistence) as session_context:
            user: User = user_entity_manager.get_by_id(p_session_context=session_context, p_id=user_id)

            self.assertIsNotNone(user)
            self.assertEqual(self.get_new_user_name(), user.username)
            self.assertEqual(2, len(user.rulesets))


    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_users_unassign_rule_set(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]

        user_id = self.add_new_user(user_entity_manager)

        with SessionContext(self._persistence) as session_context:
            rule_set_id = user_entity_manager.assign_ruleset(p_session_context=session_context, p_username=self.get_new_user_name())

        self.login_users()

        elem_name = "delete_ruleset_{id}".format(id=rule_set_id)
        add_button = self._driver.find_element_by_id(elem_name)
        self.click(add_button)

        confirm_button = self._driver.find_element_by_id(elem_name + "-modal-confirm")
        self.click(confirm_button)

        with SessionContext(self._persistence) as session_context:
            user: User = user_entity_manager.get_by_id(p_session_context=session_context, p_id=user_id)

            self.assertIsNotNone(user)
            self.assertEqual(self.get_new_user_name(), user.username)
            self.assertEqual(1, len(user.rulesets))

            rule_set = user.rulesets[0]
            self.assertNotEqual(rule_set_id, rule_set.id)

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_users_move_rule_set_down(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]
        rule_set_entity_manager: RuleSetEntityManager = dependency_injection.container[RuleSetEntityManager]

        self.add_new_user(user_entity_manager)

        with SessionContext(self._persistence) as session_context:
            rule_set_1_id = user_entity_manager.assign_ruleset(
                p_session_context=session_context, p_username=self.get_new_user_name())
            rule_set_2_id = user_entity_manager.assign_ruleset(
                p_session_context=session_context, p_username=self.get_new_user_name())

            rule_set_1:RuleSet = rule_set_entity_manager.get_by_id(
                p_session_context=session_context, p_id=rule_set_1_id)
            rule_set_2:RuleSet = rule_set_entity_manager.get_by_id(
                p_session_context=session_context, p_id=rule_set_2_id)

            self.assertGreater(rule_set_2.priority, rule_set_1.priority)


        self.login_users()

        elem_name = "move_down_ruleset_{id}".format(id=rule_set_2_id)
        add_button = self._driver.find_element_by_id(elem_name)
        self.click(add_button)

        with SessionContext(self._persistence) as session_context:
            rule_set_1:RuleSet = rule_set_entity_manager.get_by_id(
                p_session_context=session_context, p_id=rule_set_1_id)
            rule_set_2:RuleSet = rule_set_entity_manager.get_by_id(
                p_session_context=session_context, p_id=rule_set_2_id)

            self.assertLess(rule_set_2.priority, rule_set_1.priority)

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_users_move_rule_set_up(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]
        rule_set_entity_manager: RuleSetEntityManager = dependency_injection.container[RuleSetEntityManager]

        self.add_new_user(user_entity_manager)

        with SessionContext(self._persistence) as session_context:
            rule_set_1_id = user_entity_manager.assign_ruleset(
                p_session_context=session_context, p_username=self.get_new_user_name())
            rule_set_2_id = user_entity_manager.assign_ruleset(
                p_session_context=session_context, p_username=self.get_new_user_name())

            rule_set_1:RuleSet = rule_set_entity_manager.get_by_id(
                p_session_context=session_context, p_id=rule_set_1_id)
            rule_set_2:RuleSet = rule_set_entity_manager.get_by_id(
                p_session_context=session_context, p_id=rule_set_2_id)

            self.assertGreater(rule_set_2.priority, rule_set_1.priority)

        self.login_users()

        elem_name = "move_up_ruleset_{id}".format(id=rule_set_1_id)
        add_button = self._driver.find_element_by_id(elem_name)
        self.click(add_button)

        with SessionContext(self._persistence) as session_context:
            rule_set_1:RuleSet = rule_set_entity_manager.get_by_id(
                p_session_context=session_context, p_id=rule_set_1_id)
            rule_set_2:RuleSet = rule_set_entity_manager.get_by_id(
                p_session_context=session_context, p_id=rule_set_2_id)

            self.assertLess(rule_set_2.priority, rule_set_1.priority)




if __name__ == "__main__":
    unittest.main()
