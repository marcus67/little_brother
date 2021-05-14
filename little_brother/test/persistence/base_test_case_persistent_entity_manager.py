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

from little_brother import dependency_injection
from little_brother.persistence.base_entity import BaseEntity
from little_brother.persistence.base_entity_manager import BaseEntityManager
from little_brother.persistence.persistence import Persistence
from little_brother.persistence.session_context import SessionContext
from little_brother.test.persistence import test_persistence
from python_base_app import tools
from python_base_app.test import base_test


class BaseTestCasePersistentEntityManager(base_test.BaseTestCase):

    @classmethod
    def setUpClass(cls):
        cls._entity_manager: BaseEntityManager = None

    def setUp(self):
        dependency_injection.reset()

    def test_create(self):
        an_entity = self._entity_manager._entity_class()
        self.assertIsNotNone(an_entity)
        self.assertIsNotNone(str(an_entity))

    def test_save(self):
        test_persistence.TestPersistence.create_dummy_persistence(self._logger)
        dummy_persistence = dependency_injection.container[Persistence]

        with SessionContext(p_persistence=dummy_persistence) as session_context:
            an_entity: BaseEntity = self._entity_manager._entity_class()
            an_entity.populate_test_data(p_session_context=session_context)
            self.assertIsNotNone(an_entity)
            session = session_context.get_session()
            session.add(an_entity)
            session.commit()
            new_id = an_entity.id

        with SessionContext(p_persistence=dummy_persistence) as session_context:
            saved_entity = self._entity_manager.get_by_id(p_session_context=session_context, p_id=new_id)
            self.assertIsNotNone(saved_entity)

            result = tools.objects_are_equal(an_entity, saved_entity, p_logger=self._logger)

            self.assertTrue(result)
