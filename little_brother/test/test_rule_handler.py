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

from python_base_app.test import base_test
from little_brother import rule_handler
from little_brother import german_vacation_context_rule_handler

TEST_USER = "user1"

NORMAL_DAY_1 = datetime.datetime.strptime("12.04.2019", "%d.%m.%Y").date()
WEEKEND_DAY_1 = datetime.datetime.strptime("13.04.2019", "%d.%m.%Y").date()
WEEKEND_DAY_2 = datetime.datetime.strptime("14.04.2019", "%d.%m.%Y").date()
VACATION_DAY_1 = datetime.datetime.strptime("15.04.2019", "%d.%m.%Y").date()
VACATION_DAY_2 = datetime.datetime.strptime("26.04.2019", "%d.%m.%Y").date()
WEEKEND_DAY_3 = datetime.datetime.strptime("27.04.2019", "%d.%m.%Y").date()

from little_brother import simple_context_rule_handlers

class TestRuleHandler(base_test.BaseTestCase):

    def test_priority(self):

        a_rule_handler = self.create_dummy_rule_handler()

        active_rule_set = a_rule_handler.get_active_ruleset_config(p_username=TEST_USER, p_reference_date=NORMAL_DAY_1)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context, simple_context_rule_handlers.DEFAULT_CONTEXT_RULE_HANDLER_NAME)

        active_rule_set = a_rule_handler.get_active_ruleset_config(p_username=TEST_USER, p_reference_date=WEEKEND_DAY_1)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context, simple_context_rule_handlers.WEEKDAY_CONTEXT_RULE_HANDLER_NAME)

        active_rule_set = a_rule_handler.get_active_ruleset_config(p_username=TEST_USER, p_reference_date=WEEKEND_DAY_2)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context, simple_context_rule_handlers.WEEKDAY_CONTEXT_RULE_HANDLER_NAME)

        active_rule_set = a_rule_handler.get_active_ruleset_config(p_username=TEST_USER, p_reference_date=VACATION_DAY_1)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context, german_vacation_context_rule_handler.CALENDAR_CONTEXT_RULE_HANDLER_NAME)

        active_rule_set = a_rule_handler.get_active_ruleset_config(p_username=TEST_USER, p_reference_date=VACATION_DAY_2)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context, german_vacation_context_rule_handler.CALENDAR_CONTEXT_RULE_HANDLER_NAME)

        active_rule_set = a_rule_handler.get_active_ruleset_config(p_username=TEST_USER, p_reference_date=WEEKEND_DAY_3)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context, simple_context_rule_handlers.WEEKDAY_CONTEXT_RULE_HANDLER_NAME)

    @staticmethod
    def create_dummy_rule_handler():

        default_context_rule_handler = simple_context_rule_handlers.DefaultContextRuleHandler()
        weekend_context_rule_handler = simple_context_rule_handlers.WeekdayContextRuleHandler()
        vacation_context_rule_handler = german_vacation_context_rule_handler.GermanVacationContextRuleHandler()
        rulehandler_config = rule_handler.RuleHandlerConfigModel()

        # DEFAULT
        default_config = rule_handler.RuleSetConfigModel()
        default_config.username = TEST_USER
        default_config.context = default_context_rule_handler.context_name

        # VACATION
        vacation_config = rule_handler.RuleSetConfigModel()
        vacation_config.username = TEST_USER
        vacation_config.priority = 2
        vacation_config.context = vacation_context_rule_handler.context_name
        vacation_config.context_details = "Nordrhein-Westfalen"

        # WEEKEND
        weekend_config = rule_handler.RuleSetConfigModel()
        weekend_config.username = TEST_USER
        weekend_config.priority = 3
        weekend_config.context = weekend_context_rule_handler.context_name
        weekend_config.context_details = simple_context_rule_handlers.WEEKDAY_PREDEFINED_DETAILS["weekend"]
        ruleset_configs = {TEST_USER: [default_config, weekend_config, vacation_config]}

        a_rule_handler = rule_handler.RuleHandler(p_config=rulehandler_config, p_rule_set_configs=ruleset_configs)
        a_rule_handler.register_context_rule_handler(p_context_rule_handler=default_context_rule_handler,
                                                     p_default=True)
        a_rule_handler.register_context_rule_handler(p_context_rule_handler=weekend_context_rule_handler)
        a_rule_handler.register_context_rule_handler(p_context_rule_handler=vacation_context_rule_handler)

        return a_rule_handler

