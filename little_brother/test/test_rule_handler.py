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
import os.path

from little_brother import german_vacation_context_rule_handler
from little_brother import rule_handler
from little_brother import rule_override
from little_brother import simple_context_rule_handlers
from python_base_app import configuration
from python_base_app.test import base_test

TEST_USER = "user1"

NORMAL_DAY_1 = datetime.datetime.strptime("09.09.2020", "%d.%m.%Y").date()
WEEKEND_DAY_1 = datetime.datetime.strptime("12.09.2020", "%d.%m.%Y").date()
WEEKEND_DAY_2 = datetime.datetime.strptime("13.09.2020", "%d.%m.%Y").date()
VACATION_DAY_1 = datetime.datetime.strptime("14.10.2020", "%d.%m.%Y").date()
VACATION_DAY_2 = datetime.datetime.strptime("16.10.2020", "%d.%m.%Y").date()
WEEKEND_DAY_3 = datetime.datetime.strptime("07.11.2020", "%d.%m.%Y").date()

LABEL_1 = "LABEL1"
LABEL_2 = "LABEL2"
LABEL_3 = "LABEL3"


class TestRuleHandler(base_test.BaseTestCase):

    def test_priority(self):
        a_rule_handler = self.create_dummy_rule_handler(p_ruleset_configs=self.create_dummy_ruleset_configs())

        active_rule_set = a_rule_handler.get_active_ruleset_config(p_username=TEST_USER, p_reference_date=NORMAL_DAY_1)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context, simple_context_rule_handlers.DEFAULT_CONTEXT_RULE_HANDLER_NAME)

        active_rule_set = a_rule_handler.get_active_ruleset_config(p_username=TEST_USER, p_reference_date=WEEKEND_DAY_1)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context, simple_context_rule_handlers.WEEKDAY_CONTEXT_RULE_HANDLER_NAME)

        active_rule_set = a_rule_handler.get_active_ruleset_config(p_username=TEST_USER, p_reference_date=WEEKEND_DAY_2)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context, simple_context_rule_handlers.WEEKDAY_CONTEXT_RULE_HANDLER_NAME)

        active_rule_set = a_rule_handler.get_active_ruleset_config(p_username=TEST_USER,
                                                                   p_reference_date=VACATION_DAY_1)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context,
                         german_vacation_context_rule_handler.CALENDAR_CONTEXT_RULE_HANDLER_NAME)

        active_rule_set = a_rule_handler.get_active_ruleset_config(p_username=TEST_USER,
                                                                   p_reference_date=VACATION_DAY_2)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context,
                         german_vacation_context_rule_handler.CALENDAR_CONTEXT_RULE_HANDLER_NAME)

        active_rule_set = a_rule_handler.get_active_ruleset_config(p_username=TEST_USER, p_reference_date=WEEKEND_DAY_3)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context, simple_context_rule_handlers.WEEKDAY_CONTEXT_RULE_HANDLER_NAME)

    @staticmethod
    def create_dummy_ruleset_configs():
        # DEFAULT
        default_config = rule_handler.RuleSetConfigModel()
        default_config.username = TEST_USER
        default_config.context = simple_context_rule_handlers.DEFAULT_CONTEXT_RULE_HANDLER_NAME

        # VACATION
        vacation_config = rule_handler.RuleSetConfigModel()
        vacation_config.username = TEST_USER
        vacation_config.priority = 2
        vacation_config.context = german_vacation_context_rule_handler.CALENDAR_CONTEXT_RULE_HANDLER_NAME
        vacation_config.context_details = "Nordrhein-Westfalen"

        # WEEKEND
        weekend_config = rule_handler.RuleSetConfigModel()
        weekend_config.username = TEST_USER
        weekend_config.priority = 3
        weekend_config.context = simple_context_rule_handlers.WEEKDAY_CONTEXT_RULE_HANDLER_NAME
        weekend_config.context_details = simple_context_rule_handlers.WEEKDAY_PREDEFINED_DETAILS["weekend"]

        return {TEST_USER: [default_config, weekend_config, vacation_config]}

    @staticmethod
    def create_dummy_rule_handler(p_ruleset_configs):
        default_context_rule_handler = simple_context_rule_handlers.DefaultContextRuleHandler()
        weekend_context_rule_handler = simple_context_rule_handlers.WeekdayContextRuleHandler()
        vacation_context_rule_handler = german_vacation_context_rule_handler.GermanVacationContextRuleHandler()
        rulehandler_config = rule_handler.RuleHandlerConfigModel()

        a_rule_handler = rule_handler.RuleHandler(p_config=rulehandler_config, p_rule_set_configs=p_ruleset_configs)
        a_rule_handler.register_context_rule_handler(p_context_rule_handler=default_context_rule_handler,
                                                     p_default=True)
        a_rule_handler.register_context_rule_handler(p_context_rule_handler=weekend_context_rule_handler)
        a_rule_handler.register_context_rule_handler(p_context_rule_handler=vacation_context_rule_handler)

        return a_rule_handler


class TestRuleOverride(base_test.BaseTestCase):

    def test_str(self):
        override = rule_override.RuleOverride(p_username=TEST_USER, p_reference_date=NORMAL_DAY_1,
                                              p_max_time_per_day=100,
                                              p_min_time_of_day=datetime.time(hour=12, minute=34),
                                              p_max_time_of_day=datetime.time(hour=23, minute=45),
                                              p_min_break=10, p_free_play=False)

        self._logger.info(str(override))


class TestRuleSetConfigModel(base_test.BaseTestCase):

    def test_str(self):
        config = rule_handler.RuleSetConfigModel()
        self._logger.info(str(config))

    def test_init(self):
        a_config_model = rule_handler.RuleSetConfigModel()
        self.assertIsNotNone(a_config_model)

    def test_label(self):
        a_config_model = rule_handler.RuleSetConfigModel()
        self.assertIsNotNone(a_config_model)

        self.assertEqual(a_config_model.label, rule_handler.DEFAULT_RULESET_LABEL)

        a_config_model = rule_handler.RuleSetConfigModel()
        self.assertIsNotNone(a_config_model)
        a_config_model.context = LABEL_1
        self.assertEqual(a_config_model.label, LABEL_1)

        a_config_model = rule_handler.RuleSetConfigModel()
        self.assertIsNotNone(a_config_model)
        a_config_model.context_label = LABEL_1
        self.assertEqual(a_config_model.label, LABEL_1)

        a_config_model = rule_handler.RuleSetConfigModel()
        self.assertIsNotNone(a_config_model)
        a_config_model.context_details = LABEL_1
        self.assertEqual(a_config_model.label, LABEL_1)

        a_config_model = rule_handler.RuleSetConfigModel()
        self.assertIsNotNone(a_config_model)
        a_config_model.context_label = LABEL_1
        a_config_model.context_details = LABEL_2
        self.assertEqual(a_config_model.label, LABEL_1)

        a_config_model = rule_handler.RuleSetConfigModel()
        self.assertIsNotNone(a_config_model)
        a_config_model.context_details = LABEL_1
        a_config_model.context = LABEL_2
        self.assertEqual(a_config_model.label, LABEL_1)

    def test_regex(self):
        a_config_model = rule_handler.RuleSetConfigModel()
        a_config_model.process_name_pattern = "*"

        with self.assertRaises(configuration.ConfigurationException) as context:
            _a_pattern = a_config_model.regex_process_name_pattern

        self.assertIn("Invalid process REGEX", str(context.exception))

    def test_post_process(self):
        a_config_model = rule_handler.RuleSetConfigModel()
        a_config_model.min_time_of_day = "21:00:00"
        a_config_model.max_time_of_day = "21:00:00"

        with self.assertRaises(configuration.ConfigurationException) as context:
            a_config_model.post_process()

        self.assertIn("must be later", str(context.exception))

        a_config_model = rule_handler.RuleSetConfigModel()
        a_config_model.min_time_of_day = "21:00:00"
        a_config_model.max_time_of_day = "20:59:00"

        with self.assertRaises(configuration.ConfigurationException) as context:
            a_config_model.post_process()

        self.assertIn("must be later", str(context.exception))

        a_config_model = rule_handler.RuleSetConfigModel()
        a_config_model.min_time_of_day = "21:00:00"
        a_config_model.max_time_of_day = "21:01:00"

        a_config_model.post_process()

    def test_apply_override(self):
        a_config_model = rule_handler.RuleSetConfigModel()
        a_config_override_model = rule_handler.RuleSetConfigModel()

        a_config_override_model.min_time_of_day = "1"
        a_config_override_model.max_time_of_day = "2"
        a_config_override_model.max_time_per_day = "3"
        a_config_override_model.min_break = "4"
        a_config_override_model.free_play = "Y"

        new_rule_set = rule_handler.apply_override(p_rule_set=a_config_model, p_rule_override=a_config_override_model)

        self.assertEqual(new_rule_set.min_time_of_day_class, rule_handler.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE)
        self.assertEqual(new_rule_set.max_time_of_day_class, rule_handler.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE)
        self.assertEqual(new_rule_set.max_time_per_day_class, rule_handler.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE)
        self.assertEqual(new_rule_set.min_break_class, rule_handler.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE)
        self.assertEqual(new_rule_set.free_play_class, rule_handler.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE)

        self.assertEqual(new_rule_set.min_time_of_day, "1")
        self.assertEqual(new_rule_set.max_time_of_day, "2")
        self.assertEqual(new_rule_set.max_time_per_day, "3")
        self.assertEqual(new_rule_set.min_break, "4")
        self.assertEqual(new_rule_set.free_play, True)

    def test_apply_empty_override(self):
        a_config_model = rule_handler.RuleSetConfigModel()

        a_config_model.min_break = "1m"
        a_config_model.min_time_of_day = "12:34"
        a_config_model.max_time_of_day = "23:45"
        a_config_model.max_time_per_day = "1h"
        a_config_model.free_play = True

        a_config_override_model = rule_handler.RuleSetConfigModel()

        new_rule_set = rule_handler.apply_override(p_rule_set=a_config_model, p_rule_override=a_config_override_model)

        self.assertEqual(new_rule_set.min_time_of_day_class, "")
        self.assertEqual(new_rule_set.max_time_of_day_class, "")
        self.assertEqual(new_rule_set.max_time_per_day_class, "")
        self.assertEqual(new_rule_set.min_break_class, "")
        self.assertEqual(new_rule_set.free_play_class, "")

        self.assertEqual(new_rule_set.min_time_of_day, "12:34")
        self.assertEqual(new_rule_set.max_time_of_day, "23:45")
        self.assertEqual(new_rule_set.max_time_per_day, "1h")
        self.assertEqual(new_rule_set.min_break, "1m")
        self.assertEqual(new_rule_set.free_play, True)


class TestRulesectionHandler(base_test.BaseTestCase):

    def test_read_config_file(self):
        a_configuration = configuration.Configuration()

        rule_handler_section = rule_handler.RuleHandlerConfigModel()
        a_configuration.add_section(rule_handler_section)

        a_rule_set_section_handler = rule_handler.RuleSetSectionHandler()
        a_configuration.register_section_handler(p_section_handler=a_rule_set_section_handler)

        filename = os.path.join(os.path.dirname(__file__), "resources/ruleset_handler.test.config")
        a_configuration.read_config_file(p_filename=filename)

        ruleset_configs = a_rule_set_section_handler.rule_set_configs

        self.assertIsNotNone(ruleset_configs)

        self.assertEqual(len(ruleset_configs), 2)

        self.assertIn("user1", ruleset_configs)
        self.assertIn("user2", ruleset_configs)

        ruleset_user1 = ruleset_configs["user1"]
        self.assertEqual(len(ruleset_user1), 1)
        ruleset_user2 = ruleset_configs["user2"]
        self.assertEqual(len(ruleset_user2), 4)

        self.assertIsNotNone(a_configuration)

    def test_read_time_of_day(self):
        self.assertIsNone(rule_handler.RuleSetSectionHandler.read_time_of_day(None))

        self.assertEqual(rule_handler.RuleSetSectionHandler.read_time_of_day("12:34"),
                         datetime.time(hour=12, minute=34))

        self.assertEqual(rule_handler.RuleSetSectionHandler.read_time_of_day("12"),
                         datetime.time(hour=12))

        with self.assertRaises(configuration.ConfigurationException) as context:
            rule_handler.RuleSetSectionHandler.read_time_of_day("x")

        self.assertIn("Invalid time of day format", str(context.exception))
