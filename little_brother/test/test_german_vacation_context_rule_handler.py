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

from little_brother import german_vacation_context_rule_handler
from python_base_app import configuration
from python_base_app.test import base_test

INVALID_STATE_NAME = "INVALID_STATE_NAME"

VALID_STATE_NAME = "Nordrhein-Westfalen"

class TestGermanVacationContextRuleHandler(base_test.BaseTestCase):

    @base_test.skip_if_env("NO_GERMAN_VACATION_CALENDAR")
    def test_import_federal_states(self):

        rule_handler = german_vacation_context_rule_handler.GermanVacationContextRuleHandler()

        rule_handler.check_data()

        self.assertIsNotNone(rule_handler._federal_state_map)
        self.assertEqual(len(rule_handler._federal_state_map), 16)
        self.assertIn(VALID_STATE_NAME, rule_handler._federal_state_map)

    @base_test.skip_if_env("NO_GERMAN_VACATION_CALENDAR")
    def test_invalid_state_name(self):

        rule_handler = german_vacation_context_rule_handler.GermanVacationContextRuleHandler()

        with self.assertRaises(configuration.ConfigurationException):
            rule_handler.is_active(p_reference_date=datetime.datetime.now().date(), p_details=INVALID_STATE_NAME)

    def test_is_not_active_last_day_before_vacation(self):

        rule_handler = german_vacation_context_rule_handler.GermanVacationContextRuleHandler()

        self.assertFalse(rule_handler.is_active(p_reference_date=datetime.datetime.strptime("11.10.2020", "%d.%m.%Y").date(), p_details=VALID_STATE_NAME))

    @base_test.skip_if_env("NO_GERMAN_VACATION_CALENDAR")
    def test_is_active_first_day_of_vacation(self):

        rule_handler = german_vacation_context_rule_handler.GermanVacationContextRuleHandler()

        self.assertTrue(rule_handler.is_active(p_reference_date=datetime.datetime.strptime("12.10.2020", "%d.%m.%Y").date(), p_details=VALID_STATE_NAME))

    @base_test.skip_if_env("NO_GERMAN_VACATION_CALENDAR")
    def test_is_active_last_day_of_vacation(self):

        rule_handler = german_vacation_context_rule_handler.GermanVacationContextRuleHandler()

        self.assertTrue(rule_handler.is_active(p_reference_date=datetime.datetime.strptime("24.10.2020", "%d.%m.%Y").date(), p_details=VALID_STATE_NAME))

    def test_is_not_active_first_day_after_vacation(self):

        rule_handler = german_vacation_context_rule_handler.GermanVacationContextRuleHandler()

        self.assertFalse(rule_handler.is_active(p_reference_date=datetime.datetime.strptime("25.10.2020", "%d.%m.%Y").date(), p_details=VALID_STATE_NAME))


    def test_exception_when_invalid_federal_state_url(self):

        rule_handler = german_vacation_context_rule_handler.GermanVacationContextRuleHandler()

        config = german_vacation_context_rule_handler.GermanVacationContextRuleHandlerConfig()
        config.locations_url= "INVALID"

        rule_handler._config = config

        with self.assertRaises(Exception):
            rule_handler.check_data()

    def test_exception_when_invalid_vacation_data_url(self):

        rule_handler = german_vacation_context_rule_handler.GermanVacationContextRuleHandler()

        config = german_vacation_context_rule_handler.GermanVacationContextRuleHandlerConfig()
        config.vacation_data_url="INVALID"

        rule_handler._config = config

        with self.assertRaises(Exception):
            rule_handler.check_data()
