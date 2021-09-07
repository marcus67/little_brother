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
import unittest

from little_brother import db_migrations
from little_brother import dependency_injection
from little_brother import process_info
from little_brother.persistence import persistence_base
from little_brother.persistence.persistence import Persistence, PersistenceConfigModel
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
SQLITE_DIR = "/tm" + "p"


class TestPersistence(base_test.BaseTestCase):

    def setUp(self):
        dependency_injection.reset()

    @classmethod
    def create_dummy_persistence_config(cls):
        config = PersistenceConfigModel()
        config.sqlite_filename = SQLITE_FILE
        config.sqlite_dir = SQLITE_DIR
        config.database_driver = persistence_base.DATABASE_DRIVER_SQLITE
        config.database_user = None
        config.database_admin = None
        return config

    @classmethod
    def create_dummy_persistence(cls, p_logger, p_delete=False) -> None:

        config = cls.create_dummy_persistence_config()

        if p_delete:
            Persistence.delete_database(p_logger=p_logger, p_config=config)

        a_persistence = Persistence(p_config=config, p_reuse_session=False)
        a_persistence.delete_database(p_logger=p_logger, p_config=config)
        a_persistence.check_schema(p_create_tables=False)

        db_mig = db_migrations.DatabaseMigrations(p_logger, p_persistence=a_persistence)
        db_mig.upgrade_databases()

        # Dependency injection
        dependency_injection.container[Persistence] = a_persistence

        dependency_injection.container[TimeExtensionEntityManager] = TimeExtensionEntityManager()
        dependency_injection.container[UserEntityManager] = UserEntityManager()
        dependency_injection.container[ProcessInfoEntityManager] = ProcessInfoEntityManager()
        dependency_injection.container[AdminEventEntityManager] = AdminEventEntityManager()
        dependency_injection.container[RuleOverrideEntityManager] = RuleOverrideEntityManager()
        dependency_injection.container[RuleSetEntityManager] = RuleSetEntityManager()
        dependency_injection.container[DeviceEntityManager] = DeviceEntityManager()

    def test_create_database(self):

        self.create_dummy_persistence(self._logger)

        self.assertIsNotNone(dependency_injection.container[Persistence])

    def test_get_admin_session(self):

        self.create_dummy_persistence(self._logger)

        persistence = dependency_injection.container[Persistence]

        session = persistence.get_admin_session()

        self.assertIsNotNone(session)

        session2 = persistence.get_admin_session()

        self.assertIsNotNone(session2)
        self.assertEqual(session, session2)

    def test_get_create_table_session(self):

        self.create_dummy_persistence(self._logger)

        persistence = dependency_injection.container[Persistence]

        session = persistence.get_create_table_session()

        self.assertIsNotNone(session)

        session2 = persistence.get_create_table_session()

        self.assertIsNotNone(session2)
        self.assertEqual(session, session2)



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

    def test_truncate_table(self):

        self.create_dummy_persistence(self._logger)

        a_persistence = dependency_injection.container[Persistence]

        self.assertIsNotNone(a_persistence)

        process_info_entity_manager: ProcessInfoEntityManager = dependency_injection.container[ProcessInfoEntityManager]

        with SessionContext(p_persistence=a_persistence) as session_context:
            p_info = self.create_pinfo(p_age_in_days=3)
            process_info_entity_manager.write_process_info(p_session_context=session_context, p_process_info=p_info)

            p_infos = process_info_entity_manager.load_process_infos(
                p_session_context=session_context, p_lookback_in_days=4)

            self.check_list_length(p_list=p_infos, p_length=1)

            a_persistence.truncate_table(p_entity=ProcessInfo)

            p_infos = process_info_entity_manager.load_process_infos(
                p_session_context=session_context, p_lookback_in_days=4)

            self.check_list_length(p_list=p_infos, p_length=0)


if __name__ == "__main__":
    unittest.main()
