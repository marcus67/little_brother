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

import datetime

from little_brother import dependency_injection
from little_brother.persistence.base_entity_manager import BaseEntityManager
from little_brother.persistence.persistence import Persistence
from little_brother.persistence.persistent_rule_override_entity_manager import RuleOverrideEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.rule_override import RuleOverride
from little_brother.test import test_data
from little_brother.test.persistence.base_test_case_persistent_entity_manager import BaseTestCasePersistentEntityManager
from little_brother.test.persistence.test_persistence import TestPersistence


class TestRuleOverrideEntityManager(BaseTestCasePersistentEntityManager):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._entity_manager: BaseEntityManager = RuleOverrideEntityManager()

    def setUp(self):
        dependency_injection.reset()

    def compare_rule_overrides(self, p_rule_override, p_loaded_rule_override):
        self.assertEqual(p_rule_override.username, p_loaded_rule_override.username)
        self.assertEqual(p_rule_override.reference_date, p_loaded_rule_override.reference_date)
        self.assertEqual(p_rule_override.max_time_per_day, p_loaded_rule_override.max_time_per_day)
        self.assertEqual(p_rule_override.min_time_of_day, p_loaded_rule_override.min_time_of_day)
        self.assertEqual(p_rule_override.max_time_of_day, p_loaded_rule_override.max_time_of_day)

    def test_update_rule_override(self):

        TestPersistence.create_dummy_persistence(self._logger)

        a_persistence = dependency_injection.container[Persistence]
        self.assertIsNotNone(a_persistence)

        rule_override_entity_manager: RuleOverrideEntityManager = \
            dependency_injection.container[RuleOverrideEntityManager]

        with SessionContext(p_persistence=a_persistence) as session_context:
            reference_date = datetime.datetime.utcnow().date() + datetime.timedelta(days=-2)

            a_rule_override = RuleOverride(
                p_username=test_data.USER_1,
                p_reference_date=reference_date,
                p_max_time_per_day=test_data.MAX_TIME_PER_DAY_1,
                p_min_time_of_day=test_data.MIN_TIME_OF_DAY_1,
                p_max_time_of_day=test_data.MAX_TIME_OF_DAY_1,
                p_min_break=test_data.MIN_BREAK_1,
                p_free_play=test_data.FREEPLAY_1)

            rule_override_entity_manager.update_rule_override(
                p_session_context=session_context, p_rule_override=a_rule_override)

            rule_overrides = rule_override_entity_manager.load_rule_overrides(
                p_session_context=session_context, p_lookback_in_days=1)

            self.check_list_length(p_list=rule_overrides, p_length=0)

            rule_overrides = rule_override_entity_manager.load_rule_overrides(
                p_session_context=session_context, p_lookback_in_days=4)

            self.check_list_length(p_list=rule_overrides, p_length=1)

            loaded_rule_override = rule_overrides[0]

            self.compare_rule_overrides(p_rule_override=a_rule_override, p_loaded_rule_override=loaded_rule_override)

            a_rule_override.max_time_per_day = test_data.MAX_TIME_PER_DAY_2

            rule_override_entity_manager.update_rule_override(
                p_session_context=session_context, p_rule_override=a_rule_override)

            rule_overrides = rule_override_entity_manager.load_rule_overrides(
                p_session_context=session_context, p_lookback_in_days=4)

            self.check_list_length(p_list=rule_overrides, p_length=1)

            loaded_rule_override = rule_overrides[0]

            self.compare_rule_overrides(p_rule_override=a_rule_override, p_loaded_rule_override=loaded_rule_override)
