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
from little_brother import persistence
from little_brother import persistent_time_extension
from little_brother import persistent_time_extension_entity_manager
from little_brother.test import test_persistence
from python_base_app.test import base_test


class TestPersistentTimeExtension(base_test.BaseTestCase):

    def setUp(self):
        dependency_injection.reset()

    def test_time_extension(self):

        dummy_persistence = test_persistence.TestPersistence.create_dummy_persistence(self._logger)

        reference_time = datetime.datetime.utcnow()

        time_extension = persistent_time_extension.TimeExtension()
        time_extension.reference_datetime = reference_time
        time_extension.start_datetime = reference_time + datetime.timedelta(seconds=600)
        time_extension.end_datetime = reference_time + datetime.timedelta(seconds=1200)

        time_extension_entity_manager: persistent_time_extension_entity_manager.TimeExtensionEntityManager = \
            dependency_injection.container[persistent_time_extension_entity_manager.TimeExtensionEntityManager]

        with persistence.SessionContext(p_persistence=dummy_persistence) as session_context:
            time_extension_entity_manager.set_time_extension(
                p_session_context=session_context, p_reference_datetime=reference_time,
                p_start_datetime=reference_time + datetime.timedelta(seconds=600),
                p_time_delta=600, p_username="USER")

            test_config = (
                (-1, False, "inactive before reference time and start time"),
                (0, True, "active at the beginning of reference time"),
                (599, True, "active just before start time"),
                (600, True, "active just at the beginning of start time"),
                (1199, True, "active just before end time"),
                (1200, False, "inactive after end time"),
            )

            for delta_time, is_active, message in test_config:

                active_time_extension: persistent_time_extension.TimeExtension = \
                    time_extension_entity_manager.get_active_time_extensions(
                        p_session_context=session_context,
                        p_reference_datetime=reference_time + datetime.timedelta(seconds=delta_time))

                self.assertEqual(True if active_time_extension is not None else False, is_active, message)

                if active_time_extension is not None:
                    self.assertEqual(active_time_extension.username, time_extension.username)
                    self.assertEqual(active_time_extension.reference_datetime, time_extension.reference_datetime)
                    self.assertEqual(active_time_extension.start_datetime, time_extension.start_datetime)
                    self.assertEqual(active_time_extension.end_datetime, time_extension.end_datetime)
