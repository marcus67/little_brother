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
from little_brother.persistence.base_entity_manager import BaseEntityManager
from little_brother.persistence.persistence import Persistence
from little_brother.persistence.persistent_daily_user_status import DailyUserStatus
from little_brother.persistence.persistent_daily_user_status_entity_manager import DailyUserStatusEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.test.persistence.base_test_case_persistent_entity_manager import BaseTestCasePersistentEntityManager
from little_brother.test.persistence.test_persistence import TestPersistence


class TestDailyUserStatusEntityManager(BaseTestCasePersistentEntityManager):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._entity_manager: BaseEntityManager = DailyUserStatusEntityManager()

    def setUp(self):
        dependency_injection.reset()

    def test_delete_user_status(self):

        TestPersistence.create_dummy_persistence(self._logger)

        a_persistence = dependency_injection.container[Persistence]
        self.assertIsNotNone(a_persistence)

        daily_user_status_entity_manager: DailyUserStatusEntityManager = dependency_injection.container[DailyUserStatusEntityManager]

        with SessionContext(a_persistence) as session_context:

            daily_user_status = DailyUserStatus()
            session = session_context.get_session()
            session.add(daily_user_status)
            daily_user_status.populate_test_data(p_session_context=session_context)

            session.commit()

            id = daily_user_status.id

            daily_user_status_entity_manager.delete_user_status(p_session_context=session_context, p_user_status_id=id)

    def test_delete_non_existing_user_status(self):

        TestPersistence.create_dummy_persistence(self._logger)

        a_persistence = dependency_injection.container[Persistence]
        self.assertIsNotNone(a_persistence)

        daily_user_status_entity_manager: DailyUserStatusEntityManager = dependency_injection.container[DailyUserStatusEntityManager]

        with SessionContext(a_persistence) as session_context:
            daily_user_status_entity_manager.delete_user_status(p_session_context=session_context, p_user_status_id=1)

