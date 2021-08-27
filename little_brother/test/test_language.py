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

from little_brother import rule_result_info
from little_brother.language import Language
from little_brother.rule_result_info import RuleResultInfo
from python_base_app.test import base_test

HOSTNAME = "hostname"
USERNAME = "username"
PROCESS_NAME = "processname"
PID = 123


class TestLanguage(base_test.BaseTestCase):

    def test_constructor(self):
        language = Language()
        self.assertIsNotNone(language)

    def test_get_text_limited_session_start(self):
        language = Language()
        self.assertIsNotNone(language)

        result_info = RuleResultInfo()

        text = language.get_text_limited_session_start(p_locale="en_US", p_variables=result_info.args)
        self.assertIsNotNone(text)
        self.assertIn('you will be allowed to play for', text)

    def test_get_text_unlimited_session_start(self):
        language = Language()
        self.assertIsNotNone(language)

        result_info = RuleResultInfo()

        text = language.get_text_unlimited_session_start(p_locale="en_US", p_variables=result_info.args)
        self.assertIsNotNone(text)
        self.assertIn('unlimited playtime in this session', text)

    def test_get_text_prohibited_process(self):
        language = Language()
        self.assertIsNotNone(language)

        result_info = RuleResultInfo()

        args = result_info.args
        args['process_name'] = "some-process"
        text = language.get_text_prohibited_process(p_locale="en_US", p_variables=args)
        self.assertIsNotNone(text)
        self.assertIn('you are not allowed to use', text)

    def test_pick_text_for_ruleset(self):
        language = Language()
        self.assertIsNotNone(language)

        result_info = RuleResultInfo(p_locale="en_US")

        text = language.pick_text_for_ruleset(result_info)
        self.assertEqual("", text)

        result_info.applying_rules = rule_result_info.RULE_TIME_PER_DAY
        text = language.pick_text_for_ruleset(result_info)
        self.assertIn("you do not have computer time left today", text)

        result_info.applying_rules = rule_result_info.RULE_DAY_BLOCKED
        text = language.pick_text_for_ruleset(result_info)
        self.assertIn("you do not have any computer time today", text)

        result_info.applying_rules = rule_result_info.RULE_TOO_EARLY
        text = language.pick_text_for_ruleset(result_info)
        self.assertIn("it is too early to use the computer", text)

        result_info.applying_rules = rule_result_info.RULE_TOO_LATE
        text = language.pick_text_for_ruleset(result_info)
        self.assertIn("it is too late to use the computer", text)

        result_info.applying_rules = rule_result_info.RULE_ACTIVITY_DURATION
        text = language.pick_text_for_ruleset(result_info)
        self.assertIn("you have to take a break", text)

        result_info.applying_rules = rule_result_info.RULE_MIN_BREAK
        text = language.pick_text_for_ruleset(result_info)
        self.assertIn("your break will only be over in", text)

    def test_pick_text_for_approaching_logout(self):
        language = Language()
        self.assertIsNotNone(language)

        result_info = RuleResultInfo(p_locale="en_US")

        text = language.pick_text_for_approaching_logout(result_info)
        self.assertEqual("", text)

        result_info.approaching_logout_rules = rule_result_info.RULE_ACTIVITY_DURATION
        text = language.pick_text_for_approaching_logout(result_info)
        self.assertIn("minutes you will have to take a break", text)

        result_info.approaching_logout_rules = rule_result_info.RULE_TOO_LATE
        text = language.pick_text_for_approaching_logout(result_info)
        self.assertIn("minutes it will be too late to use the computer", text)

        result_info.approaching_logout_rules = rule_result_info.RULE_TIME_PER_DAY
        text = language.pick_text_for_approaching_logout(result_info)
        self.assertIn("minutes left today", text)

        result_info.approaching_logout_rules = rule_result_info.RULE_TIME_EXTENSION
        text = language.pick_text_for_approaching_logout(result_info)
        self.assertIn("minutes left in your time extension", text)


if __name__ == "__main__":
    unittest.main()
