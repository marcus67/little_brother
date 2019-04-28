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

import unittest
import datetime

from python_base_app.test import base_test 
from little_brother import process_statistics

HOSTNAME="hostname"
USERNAME="username"
PROCESS_NAME="processname"
PID=123
MIN_ACTIVITY_DURATION = 60
MAX_LOOKBACK_IN_DAYS = 10


class TestProcessStatistics(base_test.BaseTestCase):


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


if __name__ == "__main__":
    unittest.main()