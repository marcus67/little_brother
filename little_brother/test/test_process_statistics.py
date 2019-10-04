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
import unittest

from little_brother import process_info
from little_brother import process_statistics
from python_base_app.test import base_test

from little_brother.test import test_data

HOSTNAME = "hostname"
HOSTNAME2 = "hostname2"
USERNAME = "username"
PROCESS_NAME = "processname"
PID = 123
MIN_ACTIVITY_DURATION = 60
MAX_LOOKBACK_IN_DAYS = 10
DURATION = 55  # seconds


class TestProcessStatistics(base_test.BaseTestCase):

    def test_activity_init(self):
        reference_time = datetime.datetime.utcnow()
        a = process_statistics.Activity(p_start_time=reference_time)

        self.assertIsNotNone(a.host_process_counts)
        self.assertEqual(len(a.host_process_counts), 0)
        self.assertEqual(a.start_time, reference_time)
        self.assertIsNone(a.end_time)

    def test_activity_add_host_process(self):
        reference_time = datetime.datetime.utcnow()
        a = process_statistics.Activity(p_start_time=reference_time)

        self.assertIsNotNone(a.host_process_counts)
        self.assertEqual(len(a.host_process_counts), 0)

        a.add_host_process(p_hostname=HOSTNAME)

        self.assertIsNotNone(a.host_process_counts)
        self.assertEqual(len(a.host_process_counts), 1)
        self.assertIn(HOSTNAME, a.host_process_counts)
        self.assertEqual(a.host_process_counts[HOSTNAME], 1)

        a.add_host_process(p_hostname=HOSTNAME)

        self.assertIsNotNone(a.host_process_counts)
        self.assertEqual(len(a.host_process_counts), 1)
        self.assertIn(HOSTNAME, a.host_process_counts)
        self.assertEqual(a.host_process_counts[HOSTNAME], 2)

        a.add_host_process(p_hostname=HOSTNAME2)

        self.assertIsNotNone(a.host_process_counts)
        self.assertEqual(len(a.host_process_counts), 2)
        self.assertIn(HOSTNAME2, a.host_process_counts)
        self.assertEqual(a.host_process_counts[HOSTNAME2], 1)

    def test_activity_duration(self):
        reference_time = datetime.datetime.utcnow()
        a = process_statistics.Activity(p_start_time=reference_time)

        self.assertIsNone(a.duration)

        a.end_time = reference_time + datetime.timedelta(seconds=DURATION)

        self.assertIsNotNone(a.duration)
        self.assertEqual(a.duration, DURATION)

    def test_activity_str(self):
        reference_time = datetime.datetime.utcnow()
        a = process_statistics.Activity(p_start_time=reference_time)
        a.end_time = reference_time + datetime.timedelta(seconds=DURATION)

        a_str = str(a)

        self.assertIsNotNone(a_str)
        self.assertIn(str(DURATION), a_str)
        self.assertIn('Activity', a_str)

    def test_activity_host_infos(self):
        reference_time = datetime.datetime.utcnow()
        a = process_statistics.Activity(p_start_time=reference_time)

        a.add_host_process(p_hostname=HOSTNAME)

        host_infos = a.host_infos

        self.assertIsNotNone(host_infos)
        self.assertIn(HOSTNAME, host_infos)

    def test_constructor_statistics_info(self):
        reference_time = datetime.datetime.utcnow()
        psi = process_statistics.ProcessStatisticsInfo(p_username=USERNAME, p_reference_time=reference_time,
                                                       p_min_activity_duration=MIN_ACTIVITY_DURATION,
                                                       p_max_lookback_in_days=MAX_LOOKBACK_IN_DAYS)

        self.assertEqual(psi.username, USERNAME)
        self.assertEqual(psi.reference_time, reference_time)
        self.assertEqual(psi.min_activity_duration, MIN_ACTIVITY_DURATION)
        self.assertEqual(psi.max_lookback_in_days, MAX_LOOKBACK_IN_DAYS)

        self.assertEqual(psi.active_processes, 0)

        self.assertIsNone(psi.last_inactivity_start_time)
        self.assertIsNone(psi.current_activity)
        self.assertIsNone(psi.previous_activity)

        self.assertEqual(psi.accumulated_break_time, 0)

        self.assertIsNotNone(psi.day_statistics)
        self.assertEqual(len(psi.day_statistics), MAX_LOOKBACK_IN_DAYS + 1)
        self.assertIsInstance(psi.day_statistics[0], process_statistics.DayStatistics)

        self.assertIsNotNone(psi.currently_active_host_processes)
        self.assertEqual(len(psi.currently_active_host_processes), 0)

    def test_day_statistics_init(self):
        ds = process_statistics.DayStatistics()

        self.assertIsNotNone(ds.activities)
        self.assertEqual(len(ds.activities), 0)
        self.assertIsNone(ds.min_time)
        self.assertIsNone(ds.max_time)
        self.assertIsNotNone(ds.host_process_counts)
        self.assertEqual(len(ds.host_process_counts), 0)

    def test_day_statistics_add_activity(self):
        ds = process_statistics.DayStatistics()

        self.assertIsNotNone(ds.activities)
        self.assertEqual(len(ds.activities), 0)

        reference_time = datetime.datetime.utcnow()
        a = process_statistics.Activity(p_start_time=reference_time)
        a.add_host_process(p_hostname=HOSTNAME)

        ds.add_activity(p_activity=a)

        self.assertIsNotNone(ds.activities)
        self.assertEqual(len(ds.activities), 1)

        self.assertIsNotNone(ds.host_process_counts)
        self.assertEqual(len(ds.host_process_counts), 1)
        self.assertIn(HOSTNAME, ds.host_process_counts)
        self.assertEqual(ds.host_process_counts[HOSTNAME], 1)

    def test_process_statistics_info_add_process_with_end_time(self):

        start_time = datetime.datetime.utcnow()
        end_time = start_time + datetime.timedelta(seconds=60)
        psi = process_statistics.ProcessStatisticsInfo(p_username=USERNAME, p_reference_time=start_time,
                                                       p_min_activity_duration=MIN_ACTIVITY_DURATION,
                                                       p_max_lookback_in_days=MAX_LOOKBACK_IN_DAYS)

        self.assertEqual(psi.active_processes, 0)

        pi = process_info.ProcessInfo(p_hostname=HOSTNAME, p_username=USERNAME, p_processhandler=None,
                                      p_processname=PROCESS_NAME, p_pid=PID, p_start_time=start_time,
                                      p_end_time=end_time)

        psi.add_process_start(p_process_info=pi, p_start_time=pi.start_time)

        self.assertEqual(psi.active_processes, 1)

        psi.add_process_end(p_process_info=pi, p_end_time=pi.end_time)

        self.assertEqual(psi.active_processes, 0)

    def test_process_statistics_info_add_process_without_end_time(self):

        start_time = datetime.datetime.utcnow()
        #end_time = start_time + datetime.timedelta(seconds=60)
        psi = process_statistics.ProcessStatisticsInfo(p_username=USERNAME, p_reference_time=start_time,
                                                       p_min_activity_duration=MIN_ACTIVITY_DURATION,
                                                       p_max_lookback_in_days=MAX_LOOKBACK_IN_DAYS)

        self.assertEqual(psi.active_processes, 0)

        pi = process_info.ProcessInfo(p_hostname=HOSTNAME, p_username=USERNAME, p_processhandler=None,
                                      p_processname=PROCESS_NAME, p_pid=PID, p_start_time=start_time,
                                      p_end_time=None)

        psi.add_process_start(p_process_info=pi, p_start_time=pi.start_time)

        self.assertEqual(psi.active_processes, 1)

        psi.add_process_end(p_process_info=pi, p_end_time=pi.end_time)

        self.assertEqual(psi.active_processes, 0)

    def test_process_statistics_info_str(self):

        start_time = datetime.datetime.utcnow()
        psi = process_statistics.ProcessStatisticsInfo(p_username=USERNAME, p_reference_time=start_time,
                                                       p_min_activity_duration=MIN_ACTIVITY_DURATION,
                                                       p_max_lookback_in_days=MAX_LOOKBACK_IN_DAYS)

        self.assertIsNotNone(str(psi))

    def test_process_statistics_get_empty_stat_infos(self):

        start_time = datetime.datetime.utcnow()
        rule_set_configs = test_data.get_dummy_ruleset_configs(p_ruleset_config=test_data.RULESET_CONFIGS_USER1_ALL_RESTRICTIONS)
        sis = process_statistics.get_empty_stat_infos(
            p_rule_set_configs=rule_set_configs,
            p_reference_time=start_time,
            p_max_lookback_in_days=5,
            p_min_activity_duration=30)

        self.assertIsNotNone(sis)

    def test_get_process_statistics(self):

        start_time = datetime.datetime.utcnow()
        rule_set_configs = test_data.get_dummy_ruleset_configs(
            p_ruleset_config=test_data.RULESET_CONFIGS_USER1_ALL_RESTRICTIONS)

        pss = process_statistics.get_process_statistics(
            p_rule_set_configs=rule_set_configs,
            p_process_infos=test_data.get_process_dict(p_processes=test_data.PROCESSES_3),
            p_reference_time=start_time,
            p_max_lookback_in_days=5,
            p_min_activity_duration=30)

        self.assertIsNotNone(pss)

if __name__ == "__main__":
    unittest.main()
