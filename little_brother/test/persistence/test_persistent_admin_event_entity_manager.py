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
from little_brother.admin_event import AdminEvent
from little_brother.persistence.base_entity_manager import BaseEntityManager
from little_brother.persistence.persistence import Persistence
from little_brother.persistence.persistent_admin_event_entity_manager import AdminEventEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.test import test_data
from little_brother.test.persistence.base_test_case_persistent_entity_manager import BaseTestCasePersistentEntityManager
from little_brother.test.persistence.test_persistence import TestPersistence


class TestAdminEventEntityManager(BaseTestCasePersistentEntityManager):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._entity_manager: BaseEntityManager = AdminEventEntityManager()

    def setUp(self):
        dependency_injection.reset()

    def test_log_admin_event(self):
        TestPersistence.create_dummy_persistence(self._logger)

        a_persistence = dependency_injection.container[Persistence]
        self.assertIsNotNone(a_persistence)

        admin_event_entity_manager: AdminEventEntityManager = dependency_injection.container[AdminEventEntityManager]

        an_admin_event = AdminEvent(
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
