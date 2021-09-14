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

from wtforms import ValidationError

from little_brother import simple_context_rule_handlers
from python_base_app import configuration, tools
from python_base_app.test import base_test

ONE_DAY = datetime.timedelta(hours=24)


MONDAY = datetime.datetime.strptime('28.01.2019', '%d.%m.%Y')
TUESDAY = MONDAY + ONE_DAY
WEDNESDAY = TUESDAY + ONE_DAY
THURSDAY = WEDNESDAY + ONE_DAY
FRIDAY = THURSDAY + ONE_DAY
SATURDAY = FRIDAY + ONE_DAY
SUNDAY = SATURDAY + ONE_DAY

DAYS = [ MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY ]

PREDEFINED_SELECTORS = [ "MONDAYS", "TUESDAYS", "WEDNESDAYS", "THURSDAYS", "FRIDAYS", "SATURDAYS", "SUNDAYS" ]

class TestWeekDayContextRuleHandler(base_test.BaseTestCase):

    def test_single_days(self):

        rule_handler = simple_context_rule_handlers.WeekplanContextRuleHandler()

        for day in range (0,7):
            for selector in range(0,7):

                self.assertEqual(rule_handler.is_active(p_reference_date=DAYS[day],
                                                        p_details=PREDEFINED_SELECTORS[selector]),
                                 day == selector)

    def test_invalid_selector_length(self):

        rule_handler = simple_context_rule_handlers.WeekplanContextRuleHandler()

        with self.assertRaises(configuration.ConfigurationException):
            self.assertFalse(rule_handler.is_active(p_reference_date=MONDAY, p_details="X-----"))

        with self.assertRaises(configuration.ConfigurationException):
            self.assertFalse(rule_handler.is_active(p_reference_date=MONDAY, p_details="X-------"))

    def test_invalid_selector_character(self):

        rule_handler = simple_context_rule_handlers.WeekplanContextRuleHandler()

        with self.assertRaises(configuration.ConfigurationException):
            self.assertTrue(rule_handler.is_active(p_reference_date=MONDAY, p_details="X-------"))

        with self.assertRaises(configuration.ConfigurationException):
            self.assertTrue(rule_handler.is_active(p_reference_date=MONDAY, p_details="1-------"))

        with self.assertRaises(configuration.ConfigurationException):
            self.assertTrue(rule_handler.is_active(p_reference_date=MONDAY, p_details="Y-------"))

        with self.assertRaises(configuration.ConfigurationException):
            self.assertFalse(rule_handler.is_active(p_reference_date=MONDAY, p_details="#-------"))

    def test_weekend(self):

        rule_handler = simple_context_rule_handlers.WeekplanContextRuleHandler()

        self.assertFalse(rule_handler.is_active(p_reference_date=MONDAY, p_details="WEEKEND"))
        self.assertFalse(rule_handler.is_active(p_reference_date=TUESDAY, p_details="WEEKEND"))
        self.assertFalse(rule_handler.is_active(p_reference_date=WEDNESDAY, p_details="WEEKEND"))
        self.assertFalse(rule_handler.is_active(p_reference_date=THURSDAY, p_details="WEEKEND"))
        self.assertFalse(rule_handler.is_active(p_reference_date=FRIDAY, p_details="WEEKEND"))
        self.assertTrue(rule_handler.is_active(p_reference_date=SUNDAY, p_details="WEEKEND"))
        self.assertTrue(rule_handler.is_active(p_reference_date=SATURDAY, p_details="WEEKEND"))

    def test_weekdays(self):

        rule_handler = simple_context_rule_handlers.WeekplanContextRuleHandler()

        self.assertTrue(rule_handler.is_active(p_reference_date=MONDAY, p_details="WEEKDAYS"))
        self.assertTrue(rule_handler.is_active(p_reference_date=TUESDAY, p_details="WEEKDAYS"))
        self.assertTrue(rule_handler.is_active(p_reference_date=WEDNESDAY, p_details="WEEKDAYS"))
        self.assertTrue(rule_handler.is_active(p_reference_date=THURSDAY, p_details="WEEKDAYS"))
        self.assertTrue(rule_handler.is_active(p_reference_date=FRIDAY, p_details="WEEKDAYS"))
        self.assertFalse(rule_handler.is_active(p_reference_date=SUNDAY, p_details="WEEKDAYS"))
        self.assertFalse(rule_handler.is_active(p_reference_date=SATURDAY, p_details="WEEKDAYS"))

    def test_is_active_without_details(self):

        rule_handler = simple_context_rule_handlers.WeekplanContextRuleHandler()

        with self.assertRaises(configuration.ConfigurationException) as e:
            rule_handler.is_active(p_reference_date=tools.get_current_time(), p_details=None)
            self.assertIn("context without context details", str(e))

    def test_validate(self):
        rule_handler = simple_context_rule_handlers.WeekplanContextRuleHandler()
        rule_handler.validate_context_details(p_context_detail="weekend")
        rule_handler.validate_context_details(p_context_detail="weekdays")
        rule_handler.validate_context_details(p_context_detail="mondays")
        rule_handler.validate_context_details(p_context_detail="tuesdays")
        rule_handler.validate_context_details(p_context_detail="wednesdays")
        rule_handler.validate_context_details(p_context_detail="thursdays")
        rule_handler.validate_context_details(p_context_detail="fridays")
        rule_handler.validate_context_details(p_context_detail="saturdays")
        rule_handler.validate_context_details(p_context_detail="sundays")

        rule_handler.validate_context_details(p_context_detail="1yx0n--")
        rule_handler.validate_context_details(p_context_detail="1YX0N--")

        with self.assertRaises(ValidationError):
            rule_handler.validate_context_details(p_context_detail="xxxxxx")

        with self.assertRaises(ValidationError):
            rule_handler.validate_context_details(p_context_detail="xxxxxxxx")

        with self.assertRaises(ValidationError):
            rule_handler.validate_context_details(p_context_detail="abcdefg")
