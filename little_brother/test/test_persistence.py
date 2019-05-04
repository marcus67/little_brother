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

from little_brother import persistence
from little_brother import admin_event
from little_brother import process_info
from little_brother import rule_override

from little_brother.test import test_data


class TestPersistence(base_test.BaseTestCase):

    @staticmethod
    def create_dummy_persistence():

        config = persistence.PersistenceConfigModel()
        config.database_driver = persistence.DATABASE_DRIVER_SQLITE
        config.database_user = None
        config.database_admin = None

        a_persistence = persistence.Persistence(p_config=config, p_reuse_session=False)
        a_persistence.check_schema()

        return a_persistence

    def test_create_database(self):

        a_persistence = self.create_dummy_persistence()

        self.assertIsNotNone(a_persistence)

    @staticmethod
    def create_pinfo(p_age_in_days, p_include_end_time=False):

        start_time = datetime.datetime.utcnow() + datetime.timedelta(days=-p_age_in_days)

        if p_include_end_time:
            end_time = start_time + datetime.timedelta(minutes=5)

        else:
            end_time = None

        return process_info.ProcessInfo(p_username=test_data.USER_1, p_processname=test_data.PROCESS_NAME_1,
                                        p_pid=test_data.PID_1, p_start_time=start_time,
                                        p_end_time=end_time)

    def compare_pinfos(self, p_p_info, p_loaded_p_info):

        self.assertEqual(p_p_info.start_time, p_loaded_p_info.start_time)
        self.assertEqual(p_p_info.end_time, p_loaded_p_info.end_time)
        self.assertEqual(p_p_info.hostname, p_loaded_p_info.hostname)
        self.assertEqual(p_p_info.username, p_loaded_p_info.username)
        self.assertEqual(p_p_info.processhandler, p_loaded_p_info.processhandler)
        self.assertEqual(p_p_info.processname, p_loaded_p_info.processname)

    def compare_rule_overrides(self, p_rule_override, p_loaded_rule_override):

        self.assertEqual(p_rule_override.username, p_loaded_rule_override.username)
        self.assertEqual(p_rule_override.reference_date, p_loaded_rule_override.reference_date)
        self.assertEqual(p_rule_override.max_time_per_day, p_loaded_rule_override.max_time_per_day)
        self.assertEqual(p_rule_override.min_time_of_day, p_loaded_rule_override.min_time_of_day)
        self.assertEqual(p_rule_override.max_time_of_day, p_loaded_rule_override.max_time_of_day)

    def check_list_length(self, p_list, p_length):

        self.assertIsNotNone(p_list)
        self.assertEqual(len(p_list), p_length)

    def test_write_and_update_process_info(self):

        a_persistence = self.create_dummy_persistence()

        self.assertIsNotNone(a_persistence)

        p_info = self.create_pinfo(p_age_in_days=3)
        a_persistence.write_process_info(p_info)

        p_infos = a_persistence.load_process_infos(p_lookback_in_days=4)

        self.check_list_length(p_list=p_infos, p_length=1)

        loaded_p_info = p_infos[0]

        self.compare_pinfos(p_p_info=p_info, p_loaded_p_info=loaded_p_info)

        self.assertIsNotNone(loaded_p_info.id)

        p_infos = a_persistence.load_process_infos(p_lookback_in_days=2)

        self.check_list_length(p_list=p_infos, p_length=0)

        p_info.end_time = p_info.start_time + datetime.timedelta(minutes=5)

        a_persistence.update_process_info(p_process_info=p_info)

        p_infos = a_persistence.load_process_infos(p_lookback_in_days=4)

        self.check_list_length(p_list=p_infos, p_length=1)

        loaded_p_info = p_infos[0]

        an_id = loaded_p_info.id

        self.compare_pinfos(p_p_info=p_info, p_loaded_p_info=loaded_p_info)

        self.assertEqual(an_id, loaded_p_info.id)

        a_persistence = None

    def test_update_rule_override(self):

        a_persistence = self.create_dummy_persistence()

        self.assertIsNotNone(a_persistence)

        reference_date = datetime.datetime.utcnow().date() + datetime.timedelta(days=-2)

        a_rule_override = rule_override.RuleOverride(
            p_username=test_data.USER_1,
            p_reference_date=reference_date,
            p_max_time_per_day=test_data.MAX_TIME_PER_DAY_1,
            p_min_time_of_day=test_data.MIN_TIME_OF_DAY_1,
            p_max_time_of_day=test_data.MAX_TIME_OF_DAY_1,
            p_min_break=test_data.MIN_BREAK_1,
            p_free_play=test_data.FREEPLAY_1)

        a_persistence.update_rule_override(p_rule_override=a_rule_override)

        rule_overrides = a_persistence.load_rule_overrides(p_lookback_in_days=1)

        self.check_list_length(p_list=rule_overrides, p_length=0)

        rule_overrides = a_persistence.load_rule_overrides(p_lookback_in_days=4)

        self.check_list_length(p_list=rule_overrides, p_length=1)

        loaded_rule_override = rule_overrides[0]

        self.compare_rule_overrides(p_rule_override=a_rule_override, p_loaded_rule_override=loaded_rule_override)

        a_rule_override.max_time_per_day = test_data.MAX_TIME_PER_DAY_2

        a_persistence.update_rule_override(p_rule_override=a_rule_override)

        rule_overrides = a_persistence.load_rule_overrides(p_lookback_in_days=4)

        self.check_list_length(p_list=rule_overrides, p_length=1)

        loaded_rule_override = rule_overrides[0]

        self.compare_rule_overrides(p_rule_override=a_rule_override, p_loaded_rule_override=loaded_rule_override)

        a_persistence = None

    def test_log_admin_event(self):

        a_persistence = self.create_dummy_persistence()

        self.assertIsNotNone(a_persistence)

        an_admin_event = admin_event.AdminEvent(
            p_hostname=test_data.HOSTNAME_1,
            p_username=test_data.USER_1,
            p_pid=test_data.PID_1,
            p_processhandler=None,
            p_processname=None,
            p_event_type=None,
            p_event_time=None,
            p_process_start_time=test_data.START_TIME_NOW,
            p_text=None,
            p_payload=None)

        a_persistence.log_admin_event(p_admin_event=an_admin_event)

        a_persistence = None

    def test_truncate_table(self):

        a_persistence = self.create_dummy_persistence()

        self.assertIsNotNone(a_persistence)

        p_info = self.create_pinfo(p_age_in_days=3)
        a_persistence.write_process_info(p_info)

        p_infos = a_persistence.load_process_infos(p_lookback_in_days=4)

        self.check_list_length(p_list=p_infos, p_length=1)

        a_persistence.truncate_table(p_entity=persistence.ProcessInfo)

        p_infos = a_persistence.load_process_infos(p_lookback_in_days=4)

        self.check_list_length(p_list=p_infos, p_length=0)

        a_persistence = None


if __name__ == "__main__":
    unittest.main()
