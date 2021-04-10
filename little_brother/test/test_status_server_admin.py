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

from little_brother import constants
from little_brother import dependency_injection
from little_brother import status_server
from little_brother.persistence.persistent_rule_override import RuleOverride
from little_brother.persistence.persistent_rule_override_entity_manager import RuleOverrideEntityManager
from little_brother.persistence.persistent_user_entity_manager import UserEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.test import test_data
from little_brother.test.base_test_status_server import BaseTestStatusServer
from python_base_app import tools
from python_base_app.test import base_test

NEW_MAX_TIME_PER_DAY = "2h34m"
NEW_MIN_TIME_OF_DAY = "12:34"
NEW_MAX_TIME_OF_DAY = "13:45"
NEW_MIN_BREAK = "12m"
NEW_FREE_PLAY = True
NEW_MAX_ACTIVITY_DURATION = "1h23m"

class TestStatusServerAdmin(BaseTestStatusServer):

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_admin_without_process(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        # When we load the admin page the first time...
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=status_server.ADMIN_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        # ...we end up on the login page.
        self.login()

        # The second time we call the admin page.
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=status_server.ADMIN_REL_URL))
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
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=status_server.ADMIN_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        # ...we end up on the login page.
        self.login()

        # The second we call the admin page.
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=status_server.ADMIN_REL_URL))
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

        elem_name_prefix = tools.get_safe_attribute_name(
            "{username}_{date_string}_".format(username=self.get_new_user_name(),
                                               date_string=tools.get_simple_date_as_string(reference_date)))

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
            rule_override:RuleOverride = rule_override_entity_manager.get_rule_override_by_username_and_date(
                p_session_context=session_context, p_username=self.get_new_user_name(), p_date=reference_date)
            self.assertIsNotNone(rule_override)
            self.assertEqual(rule_override.reference_date, reference_date)
            self.assertEqual(rule_override.username, self.get_new_user_name())

            self.assertEqual(rule_override.min_break, tools.get_string_as_duration(NEW_MIN_BREAK))
            self.assertEqual(rule_override.max_activity_duration, tools.get_string_as_duration(NEW_MAX_ACTIVITY_DURATION))
            self.assertEqual(rule_override.max_time_per_day, tools.get_string_as_duration(NEW_MAX_TIME_PER_DAY))
            self.assertEqual(rule_override.min_time_of_day, tools.get_string_as_time(NEW_MIN_TIME_OF_DAY))
            self.assertEqual(rule_override.max_time_of_day, tools.get_string_as_time(NEW_MAX_TIME_OF_DAY))
            self.assertEqual(rule_override.free_play, NEW_FREE_PLAY)


if __name__ == "__main__":
    unittest.main()
