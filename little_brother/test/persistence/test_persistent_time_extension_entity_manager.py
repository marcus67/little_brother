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

import little_brother.persistence.session_context
from little_brother import dependency_injection
from little_brother.persistence.base_entity_manager import BaseEntityManager
from little_brother.persistence.persistence import Persistence
from little_brother.persistence.persistent_time_extension import TimeExtension
from little_brother.persistence.persistent_time_extension_entity_manager import TimeExtensionEntityManager
from little_brother.test.persistence.base_test_case_persistent_entity_manager import BaseTestCasePersistentEntityManager
from little_brother.test.persistence.test_persistence import TestPersistence


class TestTimeExtensionEntityManager(BaseTestCasePersistentEntityManager):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._entity_manager: BaseEntityManager = TimeExtensionEntityManager()

    def setUp(self):
        dependency_injection.reset()

    def test_time_extension(self):

        TestPersistence.create_dummy_persistence(self._logger)

        a_persistence = dependency_injection.container[Persistence]
        self.assertIsNotNone(a_persistence)

        reference_time = datetime.datetime.utcnow()

        time_extension = TimeExtension()
        time_extension.username = "USER"
        time_extension.reference_datetime = reference_time
        time_extension.start_datetime = reference_time + datetime.timedelta(seconds=600)
        time_extension.end_datetime = reference_time + datetime.timedelta(seconds=1200)

        time_extension_entity_manager: TimeExtensionEntityManager = \
            dependency_injection.container[TimeExtensionEntityManager]

        with little_brother.persistence.session_context.SessionContext(
                p_persistence=a_persistence) as session_context:
            time_extension_entity_manager.set_time_extension(
                p_session_context=session_context, p_reference_datetime=reference_time,
                p_start_datetime=reference_time + datetime.timedelta(seconds=600),
                p_time_delta=10, p_username="USER")

            test_config = (
                (-1, 0, "inactive before reference time and start time"),
                (0, 1, "active at the beginning of reference time"),
                (599, 1, "active just before start time"),
                (600, 1, "active just at the beginning of start time"),
                (1199, 1, "active just before end time"),
                (1200, 0, "inactive after end time"),
            )

            for delta_time, expected_count, message in test_config:

                active_time_extensions: TimeExtension = \
                    time_extension_entity_manager.get_active_time_extensions(
                        p_session_context=session_context,
                        p_reference_datetime=reference_time + datetime.timedelta(seconds=delta_time))

                self.assertEqual(len(active_time_extensions), expected_count, message)

                if len(active_time_extensions) > 0:
                    active_time_extension = active_time_extensions.get("USER")
                    self.assertIsNotNone(active_time_extension)
                    self.assertEqual(active_time_extension.username, time_extension.username)
                    self.assertEqual(active_time_extension.reference_datetime, time_extension.reference_datetime)
                    self.assertEqual(active_time_extension.start_datetime, time_extension.start_datetime)
                    self.assertEqual(active_time_extension.end_datetime, time_extension.end_datetime)
