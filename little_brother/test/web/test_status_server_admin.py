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
from typing import List

from little_brother import constants
from little_brother import dependency_injection
from little_brother.persistence.persistent_rule_override import RuleOverride
from little_brother.persistence.persistent_rule_override_entity_manager import RuleOverrideEntityManager
from little_brother.persistence.persistent_time_extension import TimeExtension
from little_brother.persistence.persistent_time_extension_entity_manager import TimeExtensionEntityManager
from little_brother.persistence.persistent_user_entity_manager import UserEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.test import test_data
from little_brother.test.web.base_test_status_server import BaseTestStatusServer
from python_base_app import tools
from python_base_app.test import base_test

NEW_MAX_TIME_PER_DAY = "2h34m"
NEW_MIN_TIME_OF_DAY = "12:34"
NEW_MAX_TIME_OF_DAY = "13:45"
NEW_MIN_BREAK = "12m"
NEW_FREE_PLAY = True
NEW_MAX_ACTIVITY_DURATION = "1h23m"

NEW_INVALID_DURATION = "1h23"
NEW_INVALID_TIME_OF_DAY = "13:455"

EXTENSION_IN_MINUTES = 30
SECOND_EXTENSION_IN_MINUTES = 30


class TestStatusServerAdmin(BaseTestStatusServer):

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_admin_without_process(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        # When we load the admin page the first time...
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=constants.ADMIN_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        # ...we end up on the login page.
        self.login()

        # The second time we call the admin page.
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=constants.ADMIN_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title
        assert "Administration" in self._driver.title

        # we are on the admin page right away...
        self.check_empty_user_list()

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_admin_with_process(self):
        ruleset_configs = test_data.get_dummy_ruleset_configs(
            p_ruleset_config=test_data.RULESET_CONFIGS_USER1_ALL_RESTRICTIONS)
        self.create_status_server_using_ruleset_configs(ruleset_configs)

        self.create_selenium_driver()

        # When we load the admin page the first time...
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=constants.ADMIN_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        # ...we end up on the login page.
        self.login()

        # The second we call the admin page.
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=constants.ADMIN_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        # we are on the admin page right away...
        self.check_empty_user_list()

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_admin_edit(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        reference_date = tools.get_current_time().date()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]
        rule_override_entity_manager: RuleOverrideEntityManager = \
            dependency_injection.container[RuleOverrideEntityManager]

        self.add_new_user(user_entity_manager)

        self.login_admin()

        elem_name_prefix = self.get_admin_elem_name_prefix(p_reference_date=reference_date)

        elem = self._driver.find_element_by_id(elem_name_prefix + "min_time_of_day")
        self.set_value(p_value=NEW_MIN_TIME_OF_DAY, p_elem=elem)

        elem = self._driver.find_element_by_id(elem_name_prefix + "max_time_of_day")
        self.set_value(p_value=NEW_MAX_TIME_OF_DAY, p_elem=elem)

        elem = self._driver.find_element_by_id(elem_name_prefix + "max_time_per_day")
        self.set_value(p_value=NEW_MAX_TIME_PER_DAY, p_elem=elem)

        elem = self._driver.find_element_by_id(elem_name_prefix + "max_activity_duration")
        self.set_value(p_value=NEW_MAX_ACTIVITY_DURATION, p_elem=elem)

        elem = self._driver.find_element_by_id(elem_name_prefix + "min_break")
        self.set_value(p_value=NEW_MIN_BREAK, p_elem=elem)

        elem = self._driver.find_element_by_id(elem_name_prefix + "free_play")
        self.click(elem)

        save_button = self._driver.find_element_by_id("save")
        self.click(save_button)

        with SessionContext(self._persistence) as session_context:
            rule_override: RuleOverride = rule_override_entity_manager.get_rule_override_by_username_and_date(
                p_session_context=session_context, p_username=self.get_new_user_name(), p_date=reference_date)
            self.assertIsNotNone(rule_override)
            self.assertEqual(rule_override.reference_date, reference_date)
            self.assertEqual(rule_override.username, self.get_new_user_name())

            self.assertEqual(rule_override.min_break, tools.get_string_as_duration(NEW_MIN_BREAK))
            self.assertEqual(rule_override.max_activity_duration,
                             tools.get_string_as_duration(NEW_MAX_ACTIVITY_DURATION))
            self.assertEqual(rule_override.max_time_per_day, tools.get_string_as_duration(NEW_MAX_TIME_PER_DAY))
            self.assertEqual(rule_override.min_time_of_day, tools.get_string_as_time(NEW_MIN_TIME_OF_DAY))
            self.assertEqual(rule_override.max_time_of_day, tools.get_string_as_time(NEW_MAX_TIME_OF_DAY))
            self.assertEqual(rule_override.free_play, NEW_FREE_PLAY)

    def get_admin_elem_name_prefix(self, p_reference_date):
        elem_name_prefix = tools.get_safe_attribute_name(
            "{username}_{date_string}_".format(username=self.get_new_user_name(),
                                               date_string=tools.get_simple_date_as_string(p_reference_date)))
        return elem_name_prefix

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_add_time_extension(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]
        time_extension_entity_manager: TimeExtensionEntityManager = \
            dependency_injection.container[TimeExtensionEntityManager]

        self.add_new_user(user_entity_manager)

        self.login_admin()

        elem_name = "time_extension_{username}_{extension}".format(
            username=self.get_new_user_name(), extension=EXTENSION_IN_MINUTES)

        elem = self._driver.find_element_by_id(elem_name)
        self.click(elem)

        with SessionContext(self._persistence) as session_context:
            time_extensions: List[TimeExtension] = time_extension_entity_manager.get_active_time_extensions(
                p_session_context=session_context, p_reference_datetime=tools.get_current_time())
            self.assertIsNotNone(time_extensions)
            self.assertEqual(1, len(time_extensions))
            self.assertIn(self.get_new_user_name(), time_extensions)

            time_extension: TimeExtension = time_extensions[self.get_new_user_name()]
            self.assertEqual(EXTENSION_IN_MINUTES, time_extension.get_length_in_minutes())

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_delete_time_extension(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]
        time_extension_entity_manager: TimeExtensionEntityManager = \
            dependency_injection.container[TimeExtensionEntityManager]

        self.add_new_user(user_entity_manager)

        reference_datetime = tools.get_current_time()

        with SessionContext(self._persistence) as session_context:
            time_extension_entity_manager.set_time_extension(p_session_context=session_context,
                                                             p_username=self.get_new_user_name(),
                                                             p_reference_datetime=reference_datetime,
                                                             p_time_delta=EXTENSION_IN_MINUTES,
                                                             p_start_datetime=reference_datetime)

        self.login_admin()

        elem_name = "time_extension_{username}_0".format(username=self.get_new_user_name())

        elem = self._driver.find_element_by_id(elem_name)
        self.click(elem)

        with SessionContext(self._persistence) as session_context:
            time_extensions: List[TimeExtension] = time_extension_entity_manager.get_active_time_extensions(
                p_session_context=session_context, p_reference_datetime=tools.get_current_time())
            self.assertIsNotNone(time_extensions)
            self.assertEqual(0, len(time_extensions))

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_extend_time_extension(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]
        time_extension_entity_manager: TimeExtensionEntityManager = \
            dependency_injection.container[TimeExtensionEntityManager]

        self.add_new_user(user_entity_manager)

        reference_datetime = tools.get_current_time()

        with SessionContext(self._persistence) as session_context:
            time_extension_entity_manager.set_time_extension(p_session_context=session_context,
                                                             p_username=self.get_new_user_name(),
                                                             p_reference_datetime=reference_datetime,
                                                             p_time_delta=EXTENSION_IN_MINUTES,
                                                             p_start_datetime=reference_datetime)

        self.login_admin()

        elem_name = "time_extension_{username}_{extension}".format(username=self.get_new_user_name(),
                                                                   extension=SECOND_EXTENSION_IN_MINUTES)

        elem = self._driver.find_element_by_id(elem_name)
        self.click(elem)

        with SessionContext(self._persistence) as session_context:
            time_extensions: List[TimeExtension] = time_extension_entity_manager.get_active_time_extensions(
                p_session_context=session_context, p_reference_datetime=tools.get_current_time())
            self.assertIsNotNone(time_extensions)
            self.assertEqual(1, len(time_extensions))
            self.assertIn(self.get_new_user_name(), time_extensions)

            time_extension: TimeExtension = time_extensions[self.get_new_user_name()]
            self.assertEqual(EXTENSION_IN_MINUTES + SECOND_EXTENSION_IN_MINUTES, time_extension.get_length_in_minutes())

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_admin_edit_invalid_duration_format(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        reference_date = tools.get_current_time().date()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]
        rule_override_entity_manager: RuleOverrideEntityManager = \
            dependency_injection.container[RuleOverrideEntityManager]

        self.add_new_user(user_entity_manager)

        self.login_admin()

        elem_name_prefix = self.get_admin_elem_name_prefix(p_reference_date=reference_date)

        elem_name = elem_name_prefix + "max_activity_duration"
        elem = self._driver.find_element_by_id(elem_name)
        self.set_value(p_value=NEW_INVALID_DURATION, p_elem=elem)

        save_button = self._driver.find_element_by_id("save")
        self.click(save_button)

        xpath = "//LABEL[@CLASS = 'error-label' and @FOR = '{elem_name}']".format(elem_name=elem_name)
        self._driver.find_element_by_xpath(xpath)

        # Data was not saved!
        with SessionContext(self._persistence) as session_context:
            rule_override: RuleOverride = rule_override_entity_manager.get_rule_override_by_username_and_date(
                p_session_context=session_context, p_username=self.get_new_user_name(), p_date=reference_date)
            self.assertIsNone(rule_override)

    def _test_page_admin_edit_invalid_data(self, p_elem_name: str, p_invalid_data: str):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        reference_date = tools.get_current_time().date()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]
        rule_override_entity_manager: RuleOverrideEntityManager = \
            dependency_injection.container[RuleOverrideEntityManager]

        self.add_new_user(user_entity_manager)

        self.login_admin()

        elem_name_prefix = self.get_admin_elem_name_prefix(p_reference_date=reference_date)

        elem_name = elem_name_prefix + p_elem_name
        elem = self._driver.find_element_by_id(elem_name)
        self.set_value(p_value=p_invalid_data, p_elem=elem)

        save_button = self._driver.find_element_by_id("save")
        self.click(save_button)

        xpath = "//LABEL[@CLASS = 'error-label' and @FOR = '{elem_name}']".format(elem_name=elem_name)
        self._driver.find_element_by_xpath(xpath)

        # Data was not saved!
        with SessionContext(self._persistence) as session_context:
            rule_override: RuleOverride = rule_override_entity_manager.get_rule_override_by_username_and_date(
                p_session_context=session_context, p_username=self.get_new_user_name(), p_date=reference_date)
            self.assertIsNone(rule_override)

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_admin_edit_invalid_min_time_of_day(self):
        self._test_page_admin_edit_invalid_data(
            p_elem_name="min_time_of_day", p_invalid_data=NEW_INVALID_TIME_OF_DAY)

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_admin_edit_invalid_max_time_of_day(self):
        self._test_page_admin_edit_invalid_data(
            p_elem_name="max_time_of_day", p_invalid_data=NEW_INVALID_TIME_OF_DAY)

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_admin_edit_invalid_max_time_per_day(self):
        self._test_page_admin_edit_invalid_data(
            p_elem_name="max_time_per_day", p_invalid_data=NEW_INVALID_DURATION)

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_admin_edit_invalid_min_break(self):
        self._test_page_admin_edit_invalid_data(
            p_elem_name="min_break", p_invalid_data=NEW_INVALID_DURATION)

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_admin_edit_invalid_max_activity_duration(self):
        self._test_page_admin_edit_invalid_data(
            p_elem_name="max_activity_duration", p_invalid_data=NEW_INVALID_DURATION)


if __name__ == "__main__":
    unittest.main()
