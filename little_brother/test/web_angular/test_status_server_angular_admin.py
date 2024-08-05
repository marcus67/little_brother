# -*- coding: utf-8 -*-
import time
import unittest
from typing import List

from selenium.webdriver.common.by import By

from little_brother import dependency_injection
from little_brother.persistence.persistent_rule_override import RuleOverride
from little_brother.persistence.persistent_rule_override_entity_manager import RuleOverrideEntityManager
from little_brother.persistence.persistent_time_extension import TimeExtension
from little_brother.persistence.persistent_time_extension_entity_manager import TimeExtensionEntityManager
from little_brother.persistence.persistent_user_entity_manager import UserEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.test import test_data
from little_brother.test.web_angular.base_test_status_server_angular import BaseTestStatusServerAngular
from python_base_app import tools
from python_base_app.test import base_test
from python_base_app.tools import wrap_retry_until_expected_result

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


class TestStatusServerAngularAdmin(BaseTestStatusServerAngular):

    @base_test.skip_if_env("NO_SELENIUM_TESTS_ANGULAR")
    def test_page_admin_without_process(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        self.initial_login()

        self.switch_to_angular_page(p_button_id="button-admin")
        self.wait_until_page_ready()

        # The admin page is empty...
        assert 0 == self.count_user_rows()

    @base_test.skip_if_env("NO_SELENIUM_TESTS_ANGULAR")
    def test_page_admin_with_process(self):
        ruleset_configs = test_data.get_dummy_ruleset_configs(
            p_ruleset_config=test_data.RULESET_CONFIGS_USER1_ALL_RESTRICTIONS)
        self.create_status_server_using_ruleset_configs(ruleset_configs)

        self.create_selenium_driver()

        self.initial_login()

        self.switch_to_angular_page(p_button_id="button-admin")

        # we are on the admin page right away...
        assert 0 == self.count_user_rows()

    @base_test.skip_if_env("NO_SELENIUM_TESTS_ANGULAR")
    def test_page_admin_edit(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        reference_date = tools.get_current_time().date()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]
        rule_override_entity_manager: RuleOverrideEntityManager = \
            dependency_injection.container[RuleOverrideEntityManager]

        user_id = self.add_new_user(user_entity_manager)

        self.initial_login()

        # Go to the admin overview page
        self.switch_to_angular_page(p_button_id="button-admin")

        # There is one user row
        assert 1 == self.count_user_rows()

        # Click the button of this user to go to the details
        self.switch_to_angular_page(p_button_id=f"button-detail-{user_id}")

        # TODO: Hack: Open the first accordion
        self.open_accordion("adminDetailAccordionItem0")

        elem_name_prefix = self.get_admin_elem_name_prefix(p_reference_date=reference_date)

        # Fill the overrides with predefined data...
        elem = self._driver.find_element(By.CLASS_NAME, elem_name_prefix + "min-time-of-day")
        elem.clear()
        elem.send_keys(NEW_MIN_TIME_OF_DAY)

        elem = self._driver.find_element(By.CLASS_NAME, elem_name_prefix + "max-time-of-day")
        elem.clear()
        elem.send_keys(NEW_MAX_TIME_OF_DAY)

        elem = self._driver.find_element(By.CLASS_NAME, elem_name_prefix + "max-time-per-day")
        elem.clear()
        elem.send_keys(NEW_MAX_TIME_PER_DAY)

        elem = self._driver.find_element(By.CLASS_NAME, elem_name_prefix + "max-activity-duration")
        elem.clear()
        elem.send_keys(NEW_MAX_ACTIVITY_DURATION)

        elem = self._driver.find_element(By.CLASS_NAME, elem_name_prefix + "min-break")
        elem.clear()
        elem.send_keys(NEW_MIN_BREAK)

        elem = self._driver.find_element(By.CLASS_NAME, elem_name_prefix + "free-play")
        self.click(elem)

        save_button = self._driver.find_element(By.CLASS_NAME, elem_name_prefix + "save")
        self.click(save_button)

        self.wait_for_data_to_be_saved()

        wrapped_get_rule_override_by_username_and_date = wrap_retry_until_expected_result(
            rule_override_entity_manager.get_rule_override_by_username_and_date, p_logger=self._logger)

        with SessionContext(self._persistence) as session_context:
            rule_override = wrapped_get_rule_override_by_username_and_date(
                p_session_context=session_context, p_username=self.get_new_user_name(), p_date=reference_date)

            self.assertEqual(rule_override.reference_date, reference_date)
            self.assertEqual(rule_override.username, self.get_new_user_name())

            self.assertEqual(rule_override.min_break, tools.get_string_as_duration(NEW_MIN_BREAK))
            self.assertEqual(rule_override.max_activity_duration,
                             tools.get_string_as_duration(NEW_MAX_ACTIVITY_DURATION))
            self.assertEqual(rule_override.max_time_per_day, tools.get_string_as_duration(NEW_MAX_TIME_PER_DAY))
            self.assertEqual(rule_override.min_time_of_day, tools.get_string_as_time(NEW_MIN_TIME_OF_DAY))
            self.assertEqual(rule_override.max_time_of_day, tools.get_string_as_time(NEW_MAX_TIME_OF_DAY))
            self.assertEqual(rule_override.free_play, NEW_FREE_PLAY)

    @staticmethod
    def get_admin_elem_name_prefix(p_reference_date):
        return f"input-{tools.get_simple_date_as_string(p_reference_date)}-"

    @base_test.skip_if_env("NO_SELENIUM_TESTS_ANGULAR")
    def test_page_add_time_extension(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]
        time_extension_entity_manager: TimeExtensionEntityManager = \
            dependency_injection.container[TimeExtensionEntityManager]

        user_id = self.add_new_user(user_entity_manager)

        self.initial_login()
        # Go to the admin overview page
        self.switch_to_angular_page(p_button_id="button-admin")

        # There is one user row
        assert 1 == self.count_user_rows()

        # Click the button of this user to go to the details
        self.switch_to_angular_page(p_button_id=f"button-detail-{user_id}")

        elem_name = f"time_extension_{EXTENSION_IN_MINUTES}"

        elem = self._driver.find_element(By.ID, elem_name)
        self.click(elem)

        self.wait_for_data_to_be_saved()

        get_active_time_extensions = wrap_retry_until_expected_result(
            time_extension_entity_manager.get_active_time_extensions, p_logger=self._logger,
            p_check_expected_result=lambda x: x is not None and len(x) == 1
        )

        with SessionContext(self._persistence) as session_context:
            time_extensions: List[TimeExtension] = get_active_time_extensions(
                p_session_context=session_context, p_reference_datetime=tools.get_current_time())

            self.assertIn(self.get_new_user_name(), time_extensions)

            time_extension: TimeExtension = time_extensions[self.get_new_user_name()]
            self.assertEqual(EXTENSION_IN_MINUTES, time_extension.get_length_in_minutes())

    @base_test.skip_if_env("NO_SELENIUM_TESTS_ANGULAR")
    def test_page_delete_time_extension(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]
        time_extension_entity_manager: TimeExtensionEntityManager = \
            dependency_injection.container[TimeExtensionEntityManager]

        user_id = self.add_new_user(user_entity_manager)

        reference_datetime = tools.get_current_time()

        with SessionContext(self._persistence) as session_context:
            time_extension_entity_manager.set_time_extension(p_session_context=session_context,
                                                             p_username=self.get_new_user_name(),
                                                             p_reference_datetime=reference_datetime,
                                                             p_time_delta=EXTENSION_IN_MINUTES,
                                                             p_start_datetime=reference_datetime)

        self.initial_login()

        # Go to the admin overview page
        self.switch_to_angular_page(p_button_id="button-admin")

        # There is one user row
        assert 1 == self.count_user_rows()

        # Click the button of this user to go to the details
        self.switch_to_angular_page(p_button_id=f"button-detail-{user_id}")

        button_name = "time_extension_0".format(username=self.get_new_user_name())

        button = self._driver.find_element(By.ID, button_name)
        self.click(button)

        self.wait_for_data_to_be_saved()

        get_active_time_extensions = wrap_retry_until_expected_result(
            time_extension_entity_manager.get_active_time_extensions, p_logger=self._logger,
            p_check_expected_result=lambda x: x is not None and len(x) == 0
        )

        with SessionContext(self._persistence) as session_context:
            get_active_time_extensions(
                p_session_context=session_context, p_reference_datetime=tools.get_current_time())

    @base_test.skip_if_env("NO_SELENIUM_TESTS_ANGULAR")
    def test_page_extend_time_extension(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]
        time_extension_entity_manager: TimeExtensionEntityManager = \
            dependency_injection.container[TimeExtensionEntityManager]

        user_id = self.add_new_user(user_entity_manager)

        reference_datetime = tools.get_current_time()

        with SessionContext(self._persistence) as session_context:
            time_extension_entity_manager.set_time_extension(p_session_context=session_context,
                                                             p_username=self.get_new_user_name(),
                                                             p_reference_datetime=reference_datetime,
                                                             p_time_delta=EXTENSION_IN_MINUTES,
                                                             p_start_datetime=reference_datetime)

        self.initial_login()

        # Go to the admin overview page
        self.switch_to_angular_page(p_button_id="button-admin")

        # There is one user row
        assert 1 == self.count_user_rows()

        # Click the button of this user to go to the details
        self.switch_to_angular_page(p_button_id=f"button-detail-{user_id}")

        button_name = f"time_extension_{SECOND_EXTENSION_IN_MINUTES}"

        button = self._driver.find_element(By.ID, button_name)
        self.click(button)

        self.wait_for_data_to_be_saved()

        get_active_time_extensions = wrap_retry_until_expected_result(
            time_extension_entity_manager.get_active_time_extensions, p_logger=self._logger,
            p_check_expected_result=lambda time_extensions: (
                    time_extensions is not None and
                    len(time_extensions) == 1 and
                    self.get_new_user_name() in time_extensions and
                    EXTENSION_IN_MINUTES + SECOND_EXTENSION_IN_MINUTES ==
                    time_extensions[self.get_new_user_name()].get_length_in_minutes())
        )

        with SessionContext(self._persistence) as session_context:
            time_extensions: List[TimeExtension] = get_active_time_extensions(
                p_session_context=session_context, p_reference_datetime=tools.get_current_time())

    def _test_page_admin_edit_invalid_data(self, p_elem_name: str, p_invalid_data: str, p_validation_message: str):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        reference_date = tools.get_current_time().date()

        user_entity_manager: UserEntityManager = dependency_injection.container[UserEntityManager]
        rule_override_entity_manager: RuleOverrideEntityManager = \
            dependency_injection.container[RuleOverrideEntityManager]

        user_id = self.add_new_user(user_entity_manager)

        self.initial_login()

        # Go to the admin overview page
        self.switch_to_angular_page(p_button_id="button-admin")

        # There is one user row
        assert 1 == self.count_user_rows()

        # Click the button of this user to go to the details
        self.switch_to_angular_page(p_button_id=f"button-detail-{user_id}")

        # TODO: Hack: Open the first accordion
        self.open_accordion(p_accordion_id="adminDetailAccordionItem0")

        elem_name_prefix = self.get_admin_elem_name_prefix(p_reference_date=reference_date)

        elem_name = elem_name_prefix + p_elem_name
        elem = self._driver.find_element(By.CLASS_NAME, elem_name)

        elem.clear()
        elem.send_keys(p_invalid_data)

        time.sleep(1)
        self.check_validation_error(p_validation_message=p_validation_message)

        save_button = self._driver.find_element(By.CLASS_NAME, elem_name_prefix + "save")

        # Make sure the button is disabled
        assert save_button.get_attribute("disabled") is not None

        # Try to click it anyway...
        self.click(save_button)

        # Data was not saved!
        with SessionContext(self._persistence) as session_context:
            rule_override: RuleOverride = rule_override_entity_manager.get_rule_override_by_username_and_date(
                p_session_context=session_context, p_username=self.get_new_user_name(), p_date=reference_date)
            self.assertIsNone(rule_override)

    @base_test.skip_if_env("NO_SELENIUM_TESTS_ANGULAR")
    def test_page_admin_edit_invalid_min_time_of_day(self):
        self._test_page_admin_edit_invalid_data(
            p_elem_name="min-time-of-day", p_invalid_data=NEW_INVALID_TIME_OF_DAY,
            p_validation_message="Time must be given as HH:MM!")

    @base_test.skip_if_env("NO_SELENIUM_TESTS_ANGULAR")
    def test_page_admin_edit_invalid_max_time_of_day(self):
        self._test_page_admin_edit_invalid_data(
            p_elem_name="max-time-of-day", p_invalid_data=NEW_INVALID_TIME_OF_DAY,
            p_validation_message="Time must be given as HH:MM!")

    @base_test.skip_if_env("NO_SELENIUM_TESTS_ANGULAR")
    def test_page_admin_edit_invalid_max_time_per_day(self):
        self._test_page_admin_edit_invalid_data(
            p_elem_name="max-time-per-day", p_invalid_data=NEW_INVALID_DURATION,
            p_validation_message="Duration must be given as NNhNNm!")

    @base_test.skip_if_env("NO_SELENIUM_TESTS_ANGULAR")
    def test_page_admin_edit_invalid_min_break(self):
        self._test_page_admin_edit_invalid_data(
            p_elem_name="min-break", p_invalid_data=NEW_INVALID_DURATION,
            p_validation_message="Duration must be given as NNhNNm!")

    @base_test.skip_if_env("NO_SELENIUM_TESTS_ANGULAR")
    def test_page_admin_edit_invalid_max_activity_duration(self):
        self._test_page_admin_edit_invalid_data(
            p_elem_name="max-activity-duration", p_invalid_data=NEW_INVALID_DURATION,
            p_validation_message="Duration must be given as NNhNNm!")


if __name__ == "__main__":
    unittest.main()
