# -*- coding: utf-8 -*-

#    Copyright (C) 2019-2024  Marcus Rickert
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

from little_brother import dependency_injection
from little_brother.persistence.base_entity_manager import BaseEntityManager
from little_brother.persistence.persistence import Persistence
from little_brother.persistence.persistent_uid_mapping import UidMapping, DEFAULT_SERVER_GROUP
from little_brother.persistence.persistent_uid_mapping_entity_manager import UidMappingEntityManager
from little_brother.persistence.persistent_user_entity_manager import UserEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.test.persistence.base_test_case_persistent_entity_manager import BaseTestCasePersistentEntityManager
from little_brother.test.persistence.test_persistence import TestPersistence
from python_base_app import tools


class TestUidMappingEntityManager(BaseTestCasePersistentEntityManager):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._entity_manager: BaseEntityManager = UserEntityManager()

    def setUp(self):
        dependency_injection.reset()

    def test_insert(self):

        TestPersistence.create_dummy_persistence(self._logger)

        a_persistence = dependency_injection.container[Persistence]
        self.assertIsNotNone(a_persistence)

        uid_mapping_entity_manager: UidMappingEntityManager = dependency_injection.container[UidMappingEntityManager]

        with SessionContext(a_persistence) as session_context:
            uid_mapping = UidMapping()
            uid_mapping.uid = 1
            uid_mapping.username = "willi"
            uid_mapping.server_group = DEFAULT_SERVER_GROUP
            session = session_context.get_session()
            uid_mapping_entity_manager.insert_or_update_uid_mapping(p_session_context=session_context,
                                                                    p_uid_mapping=uid_mapping)
            session.commit()

        with SessionContext(a_persistence) as session_context:
            uid_mapping2 = uid_mapping_entity_manager.get_by_uid_and_server_group(
                p_session_context=session_context, p_uid=1, p_server_group=DEFAULT_SERVER_GROUP)
            self.assertIsNotNone(uid_mapping2)

            result = tools.objects_are_equal(uid_mapping, uid_mapping2, p_logger=self._logger)
            self.assertTrue(result)

    def test_replace(self):
        TestPersistence.create_dummy_persistence(self._logger)

        a_persistence = dependency_injection.container[Persistence]
        self.assertIsNotNone(a_persistence)

        uid_mapping_entity_manager: UidMappingEntityManager = dependency_injection.container[UidMappingEntityManager]

        with SessionContext(a_persistence) as session_context:
            uid_mapping = UidMapping()
            uid_mapping.uid = 1
            uid_mapping.username = "willi"
            uid_mapping.server_group = DEFAULT_SERVER_GROUP
            session = session_context.get_session()
            uid_mapping_entity_manager.insert_or_update_uid_mapping(p_session_context=session_context,
                                                                    p_uid_mapping=uid_mapping)
            session.commit()

        with SessionContext(a_persistence) as session_context:
            uid_mapping = UidMapping()
            uid_mapping.uid = 1
            uid_mapping.username = "lumpi"
            uid_mapping.server_group = DEFAULT_SERVER_GROUP
            session = session_context.get_session()
            uid_mapping_entity_manager.insert_or_update_uid_mapping(p_session_context=session_context,
                                                                    p_uid_mapping=uid_mapping)
            session.commit()

        with SessionContext(a_persistence) as session_context:
            uid_mapping2 = uid_mapping_entity_manager.get_by_uid_and_server_group(
                p_session_context=session_context, p_uid=1, p_server_group=DEFAULT_SERVER_GROUP)
            self.assertIsNotNone(uid_mapping2)

            result = tools.objects_are_equal(uid_mapping, uid_mapping2, p_logger=self._logger)
            self.assertTrue(result)

    def test_find_by_username(self):
        TestPersistence.create_dummy_persistence(self._logger)

        a_persistence = dependency_injection.container[Persistence]
        self.assertIsNotNone(a_persistence)

        uid_mapping_entity_manager: UidMappingEntityManager = dependency_injection.container[UidMappingEntityManager]

        with SessionContext(a_persistence) as session_context:
            uid_mapping = UidMapping()
            uid_mapping.uid = 1
            uid_mapping.username = "willi"
            uid_mapping.server_group = DEFAULT_SERVER_GROUP
            session = session_context.get_session()
            uid_mapping_entity_manager.insert_or_update_uid_mapping(p_session_context=session_context,
                                                                    p_uid_mapping=uid_mapping)
            session.commit()

        with SessionContext(a_persistence) as session_context:
            uid_mapping2 = uid_mapping_entity_manager.get_by_username_and_server_group(
                p_session_context=session_context, p_username="willi", p_server_group=DEFAULT_SERVER_GROUP)
            self.assertIsNotNone(uid_mapping2)

            result = tools.objects_are_equal(uid_mapping, uid_mapping2, p_logger=self._logger)
            self.assertTrue(result)

    def test_server_groups_are_unique(self):
        TestPersistence.create_dummy_persistence(self._logger)

        a_persistence = dependency_injection.container[Persistence]
        self.assertIsNotNone(a_persistence)

        uid_mapping_entity_manager: UidMappingEntityManager = dependency_injection.container[UidMappingEntityManager]

        with SessionContext(a_persistence) as session_context:
            session = session_context.get_session()
            uid_mapping = UidMapping()
            uid_mapping.uid = 1
            uid_mapping.username = "willi"
            uid_mapping.server_group = DEFAULT_SERVER_GROUP
            uid_mapping_entity_manager.insert_or_update_uid_mapping(p_session_context=session_context,
                                                                    p_uid_mapping=uid_mapping)
            uid_mapping = UidMapping()
            uid_mapping.uid = 2
            uid_mapping.username = "lumpi"
            uid_mapping.server_group = DEFAULT_SERVER_GROUP
            uid_mapping_entity_manager.insert_or_update_uid_mapping(p_session_context=session_context,
                                                                    p_uid_mapping=uid_mapping)
            session.commit()

        with SessionContext(a_persistence) as session_context:
            server_groups = uid_mapping_entity_manager.get_server_groups(p_session_context=session_context)
            self.assertIsNotNone(server_groups)
            self.assertEqual(1, len(server_groups))
            self.assertIn(DEFAULT_SERVER_GROUP, server_groups)

    def test_all_server_groups(self):
        TestPersistence.create_dummy_persistence(self._logger)

        a_persistence = dependency_injection.container[Persistence]
        self.assertIsNotNone(a_persistence)

        uid_mapping_entity_manager: UidMappingEntityManager = dependency_injection.container[UidMappingEntityManager]

        with SessionContext(a_persistence) as session_context:
            session = session_context.get_session()
            uid_mapping = UidMapping()
            uid_mapping.uid = 1
            uid_mapping.username = "willi"
            uid_mapping.server_group = DEFAULT_SERVER_GROUP
            uid_mapping_entity_manager.insert_or_update_uid_mapping(p_session_context=session_context,
                                                                    p_uid_mapping=uid_mapping)
            uid_mapping = UidMapping()
            uid_mapping.uid = 2
            uid_mapping.username = "lumpi"
            uid_mapping.server_group = "SOME-OTHER-SERVER-GROUP"
            uid_mapping_entity_manager.insert_or_update_uid_mapping(p_session_context=session_context,
                                                                    p_uid_mapping=uid_mapping)
            session.commit()

        with SessionContext(a_persistence) as session_context:
            server_groups = uid_mapping_entity_manager.get_server_groups(p_session_context=session_context)
            self.assertIsNotNone(server_groups)
            self.assertEqual(2, len(server_groups))
            self.assertIn(DEFAULT_SERVER_GROUP, server_groups)
            self.assertIn("SOME-OTHER-SERVER-GROUP", server_groups)
