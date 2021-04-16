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
from little_brother.persistence.persistent_process_info_entity_manager import ProcessInfoEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.test.persistence.base_test_case_persistent_entity_manager import BaseTestCasePersistentEntityManager
from little_brother.test.persistence.test_persistence import TestPersistence


class TestProcessInfoEntityManager(BaseTestCasePersistentEntityManager):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._entity_manager: BaseEntityManager = ProcessInfoEntityManager()

    def setUp(self):
        dependency_injection.reset()

    def compare_pinfos(self, p_p_info, p_loaded_p_info):
        self.assertEqual(p_p_info.start_time, p_loaded_p_info.start_time)
        self.assertEqual(p_p_info.end_time, p_loaded_p_info.end_time)
        self.assertEqual(p_p_info.hostname, p_loaded_p_info.hostname)
        self.assertEqual(p_p_info.username, p_loaded_p_info.username)
        self.assertEqual(p_p_info.processhandler, p_loaded_p_info.processhandler)
        self.assertEqual(p_p_info.processname, p_loaded_p_info.processname)

    def test_write_and_update_process_info(self):
        TestPersistence.create_dummy_persistence(self._logger)

        a_persistence = dependency_injection.container[Persistence]
        self.assertIsNotNone(a_persistence)

        process_info_entity_manager: ProcessInfoEntityManager = dependency_injection.container[ProcessInfoEntityManager]

        self.assertIsNotNone(a_persistence)

        with SessionContext(p_persistence=a_persistence) as session_context:
            p_info = TestPersistence.create_pinfo(p_age_in_days=3)
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
