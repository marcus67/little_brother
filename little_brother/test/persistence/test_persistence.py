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
import unittest

from little_brother import admin_event
from little_brother import db_migrations
from little_brother import dependency_injection
from little_brother import process_info
from little_brother import rule_override
from little_brother.persistence import persistence
from little_brother.persistence import persistence_base
from little_brother.persistence.persistent_admin_event_entity_manager import AdminEventEntityManager
from little_brother.persistence.persistent_device_entity_manager import DeviceEntityManager
from little_brother.persistence.persistent_process_info import ProcessInfo
from little_brother.persistence.persistent_process_info_entity_manager import ProcessInfoEntityManager
from little_brother.persistence.persistent_rule_override_entity_manager import RuleOverrideEntityManager
from little_brother.persistence.persistent_rule_set_entity_manager import RuleSetEntityManager
from little_brother.persistence.persistent_time_extension_entity_manager import TimeExtensionEntityManager
from little_brother.persistence.persistent_user_entity_manager import UserEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.test import test_data
from python_base_app.test import base_test

SQLITE_FILE = "test.db"
SQLITE_DIR = "/tmp"


class TestPersistence(base_test.BaseTestCase):

    def setUp(self):
        dependency_injection.reset()

    @staticmethod
    def create_dummy_persistence(p_logger):

        sqlite_file = os.path.join(SQLITE_DIR, SQLITE_FILE)

        if os.path.exists(sqlite_file):
            os.unlink(sqlite_file)

        config = persistence.PersistenceConfigModel()
        config.sqlite_filename = SQLITE_FILE
        config.sqlite_dir = SQLITE_DIR
        config.database_driver = persistence_base.DATABASE_DRIVER_SQLITE
        config.database_user = None
        config.database_admin = None

        a_persistence = persistence.Persistence(p_config=config, p_reuse_session=False)
        a_persistence.check_schema(p_create_tables=False)

        db_mig = db_migrations.DatabaseMigrations(p_logger, p_persistence=a_persistence)
        db_mig.upgrade_databases()

        # Dependency injection
        dependency_injection.container[persistence.Persistence] = a_persistence

        dependency_injection.container[TimeExtensionEntityManager] = TimeExtensionEntityManager()
        dependency_injection.container[UserEntityManager] = UserEntityManager()
        dependency_injection.container[ProcessInfoEntityManager] = ProcessInfoEntityManager()
        dependency_injection.container[AdminEventEntityManager] = AdminEventEntityManager()
        dependency_injection.container[RuleOverrideEntityManager] = RuleOverrideEntityManager()
        dependency_injection.container[RuleSetEntityManager] = RuleSetEntityManager()
        dependency_injection.container[DeviceEntityManager] = DeviceEntityManager()

        return a_persistence

    def test_create_database(self):

        a_persistence = self.create_dummy_persistence(self._logger)

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

        a_persistence = self.create_dummy_persistence(self._logger)

        process_info_entity_manager: ProcessInfoEntityManager = dependency_injection.container[ProcessInfoEntityManager]

        self.assertIsNotNone(a_persistence)

        with SessionContext(p_persistence=a_persistence) as session_context:
            p_info = self.create_pinfo(p_age_in_days=3)
            process_info_entity_manager.write_process_info(p_session_context=session_context, p_process_info=p_info)

            p_infos = process_info_entity_manager.load_process_infos(
                p_session_context=session_context, p_lookback_in_days=4)

            self.check_list_length(p_list=p_infos, p_length=1)

            loaded_p_info = p_infos[0]

            self.compare_pinfos(p_p_info=p_info, p_loaded_p_info=loaded_p_info)

            self.assertIsNotNone(loaded_p_info.id)

            p_infos = process_info_entity_manager.load_process_infos(
                p_session_context=session_context, p_lookback_in_days=2)

            self.check_list_length(p_list=p_infos, p_length=0)

            p_info.end_time = p_info.start_time + datetime.timedelta(minutes=5)

            process_info_entity_manager.update_process_info(
                p_session_context=session_context, p_process_info=p_info)

            p_infos = process_info_entity_manager.load_process_infos(
                p_session_context=session_context, p_lookback_in_days=4)

            self.check_list_length(p_list=p_infos, p_length=1)

            loaded_p_info = p_infos[0]

            an_id = loaded_p_info.id

            self.compare_pinfos(p_p_info=p_info, p_loaded_p_info=loaded_p_info)

            self.assertEqual(an_id, loaded_p_info.id)

    def test_update_rule_override(self):

        a_persistence = self.create_dummy_persistence(self._logger)

        self.assertIsNotNone(a_persistence)

        rule_override_entity_manager: RuleOverrideEntityManager = \
            dependency_injection.container[RuleOverrideEntityManager]

        with SessionContext(p_persistence=a_persistence) as session_context:
            reference_date = datetime.datetime.utcnow().date() + datetime.timedelta(days=-2)

            a_rule_override = rule_override.RuleOverride(
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

    def test_log_admin_event(self):

        a_persistence = self.create_dummy_persistence(self._logger)

        self.assertIsNotNone(a_persistence)

        admin_event_entity_manager: AdminEventEntityManager = dependency_injection.container[AdminEventEntityManager]

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

        with SessionContext(p_persistence=a_persistence) as session_context:
            admin_event_entity_manager.log_admin_event(
                p_session_context=session_context, p_admin_event=an_admin_event)

    def test_truncate_table(self):

        a_persistence = self.create_dummy_persistence(self._logger)

        self.assertIsNotNone(a_persistence)

        process_info_entity_manager: ProcessInfoEntityManager = dependency_injection.container[ProcessInfoEntityManager]

        with SessionContext(p_persistence=a_persistence) as session_context:
            p_info = self.create_pinfo(p_age_in_days=3)
            process_info_entity_manager.write_process_info(
                p_session_context=session_context, p_process_info=p_info)

            p_infos = process_info_entity_manager.load_process_infos(
                p_session_context=session_context, p_lookback_in_days=4)

            self.check_list_length(p_list=p_infos, p_length=1)

            a_persistence.truncate_table(p_entity=ProcessInfo)

            p_infos = process_info_entity_manager.load_process_infos(
                p_session_context=session_context, p_lookback_in_days=4)

            self.check_list_length(p_list=p_infos, p_length=0)


if __name__ == "__main__":
    unittest.main()
