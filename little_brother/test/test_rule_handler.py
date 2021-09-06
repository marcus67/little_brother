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
import os.path

import little_brother.persistence.session_context
from little_brother import constants
from little_brother import db_migrations
from little_brother import dependency_injection
from little_brother import german_vacation_context_rule_handler
from little_brother import process_info
from little_brother import process_statistics
from little_brother import rule_handler
from little_brother import rule_override
from little_brother import rule_result_info
from little_brother import simple_context_rule_handlers
from little_brother.persistence import persistent_user, persistent_user_entity_manager
from little_brother.persistence.persistence import Persistence
from little_brother.test.persistence import test_persistence
from python_base_app import configuration, tools
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

HOSTNAME = "hostname"
HOSTNAME2 = "hostname2"
USERNAME = "username"
PROCESS_NAME = "processname"
PID = 123
MIN_ACTIVITY_DURATION = 60
MAX_LOOKBACK_IN_DAYS = 10
DURATION = 55  # seconds


class TestRuleHandler(base_test.BaseTestCase):

    def setUp(self):
        dependency_injection.reset()

    @base_test.skip_if_env("NO_GERMAN_VACATION_CALENDAR")
    def test_priority(self):
        test_persistence.TestPersistence.create_dummy_persistence(self._logger)
        dummy_persistence: test_persistence.TestPersistence = \
            dependency_injection.container[Persistence]

        session_context = little_brother.persistence.session_context.SessionContext(p_persistence=dummy_persistence)
        a_rule_handler = self.create_dummy_rule_handler(p_persistence=dummy_persistence)

        user_entity_manager = dependency_injection.container[persistent_user_entity_manager.UserEntityManager]

        migrator = db_migrations.DatabaseMigrations(p_logger=self._logger, p_persistence=dummy_persistence)
        migrator.migrate_ruleset_configs(self.create_dummy_ruleset_configs())

        user: persistent_user.User = user_entity_manager.user_map(p_session_context=session_context).get(TEST_USER)
        self.assertIsNotNone(user)

        active_rule_set = a_rule_handler.get_active_ruleset(p_rule_sets=user.rulesets, p_reference_date=NORMAL_DAY_1)

        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context, simple_context_rule_handlers.DEFAULT_CONTEXT_RULE_HANDLER_NAME)

        active_rule_set = a_rule_handler.get_active_ruleset(p_rule_sets=user.rulesets, p_reference_date=WEEKEND_DAY_1)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context, simple_context_rule_handlers.WEEKPLAN_CONTEXT_RULE_HANDLER_NAME)

        active_rule_set = a_rule_handler.get_active_ruleset(p_rule_sets=user.rulesets, p_reference_date=WEEKEND_DAY_2)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context, simple_context_rule_handlers.WEEKPLAN_CONTEXT_RULE_HANDLER_NAME)

        active_rule_set = a_rule_handler.get_active_ruleset(p_rule_sets=user.rulesets, p_reference_date=VACATION_DAY_1)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context,
                         german_vacation_context_rule_handler.CALENDAR_CONTEXT_RULE_HANDLER_NAME)

        active_rule_set = a_rule_handler.get_active_ruleset(p_rule_sets=user.rulesets, p_reference_date=VACATION_DAY_2)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context,
                         german_vacation_context_rule_handler.CALENDAR_CONTEXT_RULE_HANDLER_NAME)

        active_rule_set = a_rule_handler.get_active_ruleset(p_rule_sets=user.rulesets, p_reference_date=WEEKEND_DAY_3)
        self.assertIsNotNone(active_rule_set)
        self.assertEqual(active_rule_set.context, simple_context_rule_handlers.WEEKPLAN_CONTEXT_RULE_HANDLER_NAME)

    @staticmethod
    def create_dummy_ruleset_config():

        default_config = rule_handler.RuleSetConfigModel()
        default_config.username = TEST_USER
        default_config.context = simple_context_rule_handlers.DEFAULT_CONTEXT_RULE_HANDLER_NAME

        return default_config

    @staticmethod
    def create_dummy_ruleset_configs(p_create_complex_configs=True):

        # TODO: Migrate test instances of ruleset configurations to database entries of ruleset
        configs = []

        # DEFAULT
        default_config = TestRuleHandler.create_dummy_ruleset_config()

        configs.append(default_config)

        if p_create_complex_configs:
            # VACATION
            vacation_config = rule_handler.RuleSetConfigModel()
            vacation_config.username = TEST_USER
            vacation_config.priority = 2
            vacation_config.context = german_vacation_context_rule_handler.CALENDAR_CONTEXT_RULE_HANDLER_NAME
            vacation_config.context_details = "Nordrhein-Westfalen"

            configs.append(vacation_config)

            # WEEKEND
            weekend_config = rule_handler.RuleSetConfigModel()
            weekend_config.username = TEST_USER
            weekend_config.priority = 3
            weekend_config.context = simple_context_rule_handlers.WEEKPLAN_CONTEXT_RULE_HANDLER_NAME
            weekend_config.context_details = simple_context_rule_handlers.WEEKPLAN_PREDEFINED_DETAILS["weekend"]

            configs.append(weekend_config)

        return {TEST_USER: configs}

    @staticmethod
    def create_dummy_rule_handler(p_persistence, p_create_complex_handlers=True):
        default_context_rule_handler = simple_context_rule_handlers.DefaultContextRuleHandler()
        rulehandler_config = rule_handler.RuleHandlerConfigModel()

        a_rule_handler = rule_handler.RuleHandler(p_config=rulehandler_config, p_persistence=p_persistence)
        a_rule_handler.register_context_rule_handler(p_context_rule_handler=default_context_rule_handler,
                                                     p_default=True)
        if p_create_complex_handlers:
            weekend_context_rule_handler = simple_context_rule_handlers.WeekplanContextRuleHandler()
            vacation_context_rule_handler = german_vacation_context_rule_handler.GermanVacationContextRuleHandler()
            a_rule_handler.register_context_rule_handler(p_context_rule_handler=weekend_context_rule_handler)
            a_rule_handler.register_context_rule_handler(p_context_rule_handler=vacation_context_rule_handler)

        return a_rule_handler

    def test_min_break_time(self):

        reference_time = datetime.datetime.utcnow()
        rule_set = TestRuleHandler.create_dummy_ruleset_config()

        previous_activity_start = reference_time + datetime.timedelta(seconds=-1200)
        previous_activity_end = previous_activity_start + datetime.timedelta(seconds=600)

        previous_activity = process_statistics.Activity(p_start_time=previous_activity_start)
        previous_activity.set_end_time(previous_activity_end)

        previous_short_activity_end = previous_activity_start + datetime.timedelta(seconds=200)
        previous_short_activity = process_statistics.Activity(p_start_time=previous_activity_start)
        previous_short_activity.set_end_time(previous_short_activity_end)

        rule_set.max_activity_duration = 600

        stat_info = process_statistics.ProcessStatisticsInfo(p_username=USERNAME, p_reference_time=reference_time,
                                                             p_min_activity_duration=MIN_ACTIVITY_DURATION,
                                                             p_max_lookback_in_days=MAX_LOOKBACK_IN_DAYS)

        stat_info.previous_activity = previous_activity

        # Check that playing is not allowed after full break minus one second
        a_rule_result_info = rule_handler.RuleResultInfo()
        activity_start_time = reference_time + datetime.timedelta(seconds=-299)
        stat_info.last_inactivity_start_time = activity_start_time
        rule_set.min_break = 300

        rule_handler.RuleHandler.check_min_break(p_rule_set=rule_set, p_stat_info=stat_info,
                                                 p_rule_result_info=a_rule_result_info)

        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_MIN_BREAK,
                         rule_result_info.RULE_MIN_BREAK)

        # Check that playing is allowed after full break minus one second but with free_play activated
        a_rule_result_info = rule_handler.RuleResultInfo()
        activity_start_time = reference_time + datetime.timedelta(seconds=-299)
        stat_info.last_inactivity_start_time = activity_start_time
        rule_set.min_break = 300

        test_persistence.TestPersistence.create_dummy_persistence(self._logger)
        dummy_persistence: test_persistence.TestPersistence = \
            dependency_injection.container[Persistence]

        a_rule_handler = self.create_dummy_rule_handler(p_persistence=dummy_persistence,
                                                        p_create_complex_handlers=False)
        rule_set.free_play = True

        a_rule_handler.check_free_play(p_rule_set=rule_set, p_rule_result_info=a_rule_result_info)

        rule_handler.RuleHandler.check_min_break(p_rule_set=rule_set, p_stat_info=stat_info,
                                                 p_rule_result_info=a_rule_result_info)
        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_MIN_BREAK, 0)

        # Check that playing is allowed after full break
        rule_set.free_play = False
        a_rule_result_info = rule_handler.RuleResultInfo()
        activity_start_time = reference_time + datetime.timedelta(seconds=-300)
        stat_info.last_inactivity_start_time = activity_start_time
        rule_set.min_break = 300
        rule_handler.RuleHandler.check_min_break(p_rule_set=rule_set, p_stat_info=stat_info,
                                                 p_rule_result_info=a_rule_result_info)
        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_MIN_BREAK, 0)

        # Check that playing is not allowed after break after short period (1/3 of max) minus one second
        stat_info.previous_activity = previous_short_activity
        a_rule_result_info = rule_handler.RuleResultInfo()
        activity_start_time = reference_time + datetime.timedelta(seconds=-99)
        stat_info.last_inactivity_start_time = activity_start_time
        rule_handler.RuleHandler.check_min_break(p_rule_set=rule_set, p_stat_info=stat_info,
                                                 p_rule_result_info=a_rule_result_info)
        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_MIN_BREAK,
                         rule_result_info.RULE_MIN_BREAK)
        self.assertEqual(a_rule_result_info.args['break_minutes_left'], 0)

        # Check that playing is not allowed after break after short period (1/3 of max) minus one second
        # but with max_activity_duration=0
        stat_info.previous_activity = previous_short_activity
        a_rule_result_info = rule_handler.RuleResultInfo()
        rule_set.max_activity_duration = 0
        activity_start_time = reference_time + datetime.timedelta(seconds=-299)
        stat_info.last_inactivity_start_time = activity_start_time
        rule_handler.RuleHandler.check_min_break(p_rule_set=rule_set, p_stat_info=stat_info,
                                                 p_rule_result_info=a_rule_result_info)
        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_MIN_BREAK,
                         rule_result_info.RULE_MIN_BREAK)

        # Check that playing is allowed after break after short period (1/3 of max)
        # but with max_activity_duration=0
        stat_info.previous_activity = previous_short_activity
        a_rule_result_info = rule_handler.RuleResultInfo()
        rule_set.max_activity_duration = 0
        activity_start_time = reference_time + datetime.timedelta(seconds=-300)
        stat_info.last_inactivity_start_time = activity_start_time
        rule_handler.RuleHandler.check_min_break(p_rule_set=rule_set, p_stat_info=stat_info,
                                                 p_rule_result_info=a_rule_result_info)
        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_MIN_BREAK, 0)

        # Check that playing is allowed after break after short period (1/3 of max)
        stat_info.previous_activity = previous_short_activity
        rule_set.max_activity_duration = 600
        a_rule_result_info = rule_handler.RuleResultInfo()
        activity_start_time = reference_time + datetime.timedelta(seconds=-100)
        stat_info.last_inactivity_start_time = activity_start_time
        rule_handler.RuleHandler.check_min_break(p_rule_set=rule_set, p_stat_info=stat_info,
                                                 p_rule_result_info=a_rule_result_info)
        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_MIN_BREAK, 0)

        # Check that playing is not allowed after break after short period (1/3 of max) minus 31 second and
        # that the number of break minutes left = 1
        stat_info.previous_activity = previous_short_activity
        a_rule_result_info = rule_handler.RuleResultInfo()
        activity_start_time = reference_time + datetime.timedelta(seconds=-69)
        stat_info.last_inactivity_start_time = activity_start_time
        rule_handler.RuleHandler.check_min_break(p_rule_set=rule_set, p_stat_info=stat_info,
                                                 p_rule_result_info=a_rule_result_info)
        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_MIN_BREAK,
                         rule_result_info.RULE_MIN_BREAK)
        self.assertEqual(a_rule_result_info.args['break_minutes_left'], 1)

        # Check that playing is not allowed after break after short period (1/3 of max) minus 91 second and
        # that the number of break minutes left = 2
        stat_info.previous_activity = previous_short_activity
        a_rule_result_info = rule_handler.RuleResultInfo()
        activity_start_time = reference_time + datetime.timedelta(seconds=-9)
        stat_info.last_inactivity_start_time = activity_start_time
        rule_handler.RuleHandler.check_min_break(p_rule_set=rule_set, p_stat_info=stat_info,
                                                 p_rule_result_info=a_rule_result_info)
        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_MIN_BREAK,
                         rule_result_info.RULE_MIN_BREAK)
        self.assertEqual(a_rule_result_info.args['break_minutes_left'], 2)

    def test_max_session_duration(self):

        test_persistence.TestPersistence.create_dummy_persistence(self._logger)
        dummy_persistence: test_persistence.TestPersistence = \
            dependency_injection.container[Persistence]
        a_rule_handler = self.create_dummy_rule_handler(p_persistence=dummy_persistence,
                                                        p_create_complex_handlers=False)

        reference_time = datetime.datetime.utcnow()
        rule_set = TestRuleHandler.create_dummy_ruleset_config()

        activity_start = reference_time + datetime.timedelta(seconds=-1200)

        rule_set.max_activity_duration = 1199
        stat_info = process_statistics.ProcessStatisticsInfo(p_username=USERNAME, p_reference_time=reference_time,
                                                             p_min_activity_duration=MIN_ACTIVITY_DURATION,
                                                             p_max_lookback_in_days=MAX_LOOKBACK_IN_DAYS)

        a_process_info = process_info.ProcessInfo(p_hostname=HOSTNAME, p_username=USERNAME, p_pid=PID,
                                                  p_start_time=activity_start)
        stat_info.add_process_start(p_process_info=a_process_info, p_start_time=activity_start)

        # Check that playing is allowed up to the maximum session time
        a_rule_result_info = rule_handler.RuleResultInfo()

        a_rule_handler.check_activity_duration(p_rule_set=rule_set, p_stat_info=stat_info,
                                               p_rule_result_info=a_rule_result_info)

        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_ACTIVITY_DURATION,
                         rule_result_info.RULE_ACTIVITY_DURATION)

        rule_set.max_activity_duration = 1201

        # Check that playing is allowed after the maximum session time
        a_rule_result_info = rule_handler.RuleResultInfo()

        a_rule_handler.check_activity_duration(p_rule_set=rule_set, p_stat_info=stat_info,
                                               p_rule_result_info=a_rule_result_info)

        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_ACTIVITY_DURATION, 0)

    def test_max_session_duration_with_downtime(self):

        test_persistence.TestPersistence.create_dummy_persistence(self._logger)
        dummy_persistence: test_persistence.TestPersistence = \
            dependency_injection.container[Persistence]
        a_rule_handler = self.create_dummy_rule_handler(p_persistence=dummy_persistence,
                                                        p_create_complex_handlers=False)

        reference_time = datetime.datetime.utcnow()
        rule_set = TestRuleHandler.create_dummy_ruleset_config()

        activity_start = reference_time + datetime.timedelta(seconds=-1200)

        stat_info = process_statistics.ProcessStatisticsInfo(p_username=USERNAME, p_reference_time=reference_time,
                                                             p_min_activity_duration=MIN_ACTIVITY_DURATION,
                                                             p_max_lookback_in_days=MAX_LOOKBACK_IN_DAYS)

        a_process_info = process_info.ProcessInfo(p_hostname=HOSTNAME, p_username=USERNAME, p_pid=PID,
                                                  p_start_time=activity_start,
                                                  p_downtime=300)
        stat_info.add_process_start(p_process_info=a_process_info, p_start_time=activity_start)

        # Check that playing is allowed up to the maximum session time
        rule_set.max_activity_duration = 899
        a_rule_result_info = rule_handler.RuleResultInfo()

        a_rule_handler.check_activity_duration(p_rule_set=rule_set, p_stat_info=stat_info,
                                               p_rule_result_info=a_rule_result_info)

        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_ACTIVITY_DURATION,
                         rule_result_info.RULE_ACTIVITY_DURATION)

        rule_set.max_activity_duration = 901

        # Check that playing is allowed after the maximum session time
        a_rule_result_info = rule_handler.RuleResultInfo()

        a_rule_handler.check_activity_duration(p_rule_set=rule_set, p_stat_info=stat_info,
                                               p_rule_result_info=a_rule_result_info)

        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_ACTIVITY_DURATION, 0)

    def test_max_time_per_day(self):

        test_persistence.TestPersistence.create_dummy_persistence(self._logger)
        dummy_persistence: test_persistence.TestPersistence = \
            dependency_injection.container[Persistence]
        a_rule_handler = self.create_dummy_rule_handler(p_persistence=dummy_persistence,
                                                        p_create_complex_handlers=False)

        reference_time = datetime.datetime.utcnow()
        rule_set = TestRuleHandler.create_dummy_ruleset_config()

        activity_start = reference_time + datetime.timedelta(seconds=-1200)

        activity = process_statistics.Activity(p_start_time=activity_start)

        stat_info = process_statistics.ProcessStatisticsInfo(p_username=USERNAME, p_reference_time=reference_time,
                                                             p_min_activity_duration=MIN_ACTIVITY_DURATION,
                                                             p_max_lookback_in_days=MAX_LOOKBACK_IN_DAYS)

        stat_info.current_activity = activity

        # Check that playing is allowed up to the maximum session time
        rule_set.max_time_per_day = 1199
        a_rule_result_info = rule_handler.RuleResultInfo()

        a_rule_handler.check_time_per_day(p_rule_set=rule_set, p_stat_info=stat_info,
                                          p_rule_result_info=a_rule_result_info)

        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_TIME_PER_DAY,
                         rule_result_info.RULE_TIME_PER_DAY)

        rule_set.max_time_per_day = 1201

        # Check that playing is allowed after the maximum session time
        a_rule_result_info = rule_handler.RuleResultInfo()

        a_rule_handler.check_time_per_day(p_rule_set=rule_set, p_stat_info=stat_info,
                                          p_rule_result_info=a_rule_result_info)

        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_TIME_PER_DAY, 0)

    def test_max_time_per_day_with_downtime(self):

        test_persistence.TestPersistence.create_dummy_persistence(self._logger)
        dummy_persistence: test_persistence.TestPersistence = \
            dependency_injection.container[Persistence]
        a_rule_handler = self.create_dummy_rule_handler(p_persistence=dummy_persistence,
                                                        p_create_complex_handlers=False)

        reference_time = datetime.datetime.utcnow()
        rule_set = TestRuleHandler.create_dummy_ruleset_config()

        activity_start = reference_time + datetime.timedelta(seconds=-1200)

        stat_info = process_statistics.ProcessStatisticsInfo(p_username=USERNAME, p_reference_time=reference_time,
                                                             p_min_activity_duration=MIN_ACTIVITY_DURATION,
                                                             p_max_lookback_in_days=MAX_LOOKBACK_IN_DAYS)

        a_process_info = process_info.ProcessInfo(p_hostname=HOSTNAME, p_username=USERNAME, p_pid=PID,
                                                  p_start_time=activity_start,
                                                  p_downtime=300)
        stat_info.add_process_start(p_process_info=a_process_info, p_start_time=activity_start)

        # Check that playing is allowed up to the maximum session time
        rule_set.max_time_per_day = 899
        a_rule_result_info = rule_handler.RuleResultInfo()

        a_rule_handler.check_time_per_day(p_rule_set=rule_set, p_stat_info=stat_info,
                                          p_rule_result_info=a_rule_result_info)

        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_TIME_PER_DAY,
                         rule_result_info.RULE_TIME_PER_DAY)

        rule_set.max_time_per_day = 901

        # Check that playing is allowed after the maximum session time
        a_rule_result_info = rule_handler.RuleResultInfo()

        a_rule_handler.check_time_per_day(p_rule_set=rule_set, p_stat_info=stat_info,
                                          p_rule_result_info=a_rule_result_info)

        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_TIME_PER_DAY, 0)

    def test_max_time_per_day_with_downtime_and_previous_activity(self):

        test_persistence.TestPersistence.create_dummy_persistence(self._logger)
        dummy_persistence: test_persistence.TestPersistence = \
            dependency_injection.container[Persistence]
        a_rule_handler = self.create_dummy_rule_handler(p_persistence=dummy_persistence,
                                                        p_create_complex_handlers=False)

        # Use reference time around noon so that we don't get trouble with time intervals spanning midnight
        reference_time = tools.get_today() + datetime.timedelta(hours=+12)
        rule_set = TestRuleHandler.create_dummy_ruleset_config()

        activity_start = reference_time + datetime.timedelta(seconds=-2000)
        activity_end = reference_time + datetime.timedelta(seconds=-1700)

        stat_info = process_statistics.ProcessStatisticsInfo(p_username=USERNAME, p_reference_time=reference_time,
                                                             p_min_activity_duration=MIN_ACTIVITY_DURATION,
                                                             p_max_lookback_in_days=MAX_LOOKBACK_IN_DAYS)

        a_process_info = process_info.ProcessInfo(p_hostname=HOSTNAME, p_username=USERNAME, p_pid=PID,
                                                  p_start_time=activity_start,
                                                  p_downtime=50)
        stat_info.add_process_start(p_process_info=a_process_info, p_start_time=activity_start)

        a_process_info.end_time = activity_end

        stat_info.add_process_end(p_process_info=a_process_info, p_end_time=activity_end)

        activity_start = reference_time + datetime.timedelta(seconds=-500)

        a_process_info = process_info.ProcessInfo(p_hostname=HOSTNAME, p_username=USERNAME, p_pid=PID,
                                                  p_start_time=activity_start,
                                                  p_downtime=100)
        stat_info.add_process_start(p_process_info=a_process_info, p_start_time=activity_start)

        # Check that playing is allowed up to the maximum session time
        rule_set.max_time_per_day = 649
        a_rule_result_info = rule_handler.RuleResultInfo()

        a_rule_handler.check_time_per_day(p_rule_set=rule_set, p_stat_info=stat_info,
                                          p_rule_result_info=a_rule_result_info)

        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_TIME_PER_DAY,
                         rule_result_info.RULE_TIME_PER_DAY)

        rule_set.max_time_per_day = 651

        # Check that playing is allowed after the maximum session time
        a_rule_result_info = rule_handler.RuleResultInfo()

        a_rule_handler.check_time_per_day(p_rule_set=rule_set, p_stat_info=stat_info,
                                          p_rule_result_info=a_rule_result_info)

        self.assertEqual(a_rule_result_info.applying_rules & rule_result_info.RULE_TIME_PER_DAY, 0)


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

        new_rule_set = rule_result_info.apply_override(p_rule_set=a_config_model,
                                                       p_rule_override=a_config_override_model)

        self.assertEqual(new_rule_set.min_time_of_day_class, constants.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE)
        self.assertEqual(new_rule_set.max_time_of_day_class, constants.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE)
        self.assertEqual(new_rule_set.max_time_per_day_class, constants.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE)
        self.assertEqual(new_rule_set.min_break_class, constants.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE)
        self.assertEqual(new_rule_set.free_play_class, constants.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE)

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

        new_rule_set = rule_result_info.apply_override(p_rule_set=a_config_model,
                                                       p_rule_override=a_config_override_model)

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
