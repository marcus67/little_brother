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

import copy
import datetime
import unittest

from little_brother import admin_event
from little_brother import process_handler
from little_brother.test import dummy_process_handler
from little_brother.test import test_data
from python_base_app.test import base_test

DOWNTIME = 12.3


class TestProcessHandler(base_test.BaseTestCase):

    @staticmethod
    def get_process_handler():
        config = process_handler.ProcessHandlerConfigModel(p_section_name="ProcessHandler")
        return dummy_process_handler.DummyProcessHandler(p_config=config)

    def test_create_admin_event_process_start_from_pinfo(self):
        pinfo = test_data.PINFO_1

        reference_time = datetime.datetime.now()

        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo, p_reference_time=reference_time)

        self.assertEqual(an_admin_event.event_type, admin_event.EVENT_TYPE_PROCESS_START)
        self.assertEqual(pinfo.start_time, an_admin_event.process_start_time)
        self.assertEqual(pinfo.hostname, an_admin_event.hostname)
        self.assertEqual(pinfo.username, an_admin_event.username)
        self.assertEqual(pinfo.pid, an_admin_event.pid)
        self.assertEqual(None, an_admin_event.processname)
        self.assertEqual(pinfo.processhandler, an_admin_event.processhandler)
        self.assertEqual(pinfo.downtime, an_admin_event.downtime)

        pinfo2 = copy.copy(pinfo)
        pinfo2.start_time = None

        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo2, p_reference_time=reference_time)

        self.assertEqual(reference_time, an_admin_event.process_start_time)

        reference_time = datetime.datetime.now()

        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo2)

        diff_time = abs((an_admin_event.event_time - reference_time).total_seconds())

        self.assertLess(diff_time, 0.01)

    def test_create_admin_event_process_end_from_pinfo(self):
        pinfo = test_data.PINFO_1

        reference_time = datetime.datetime.now()

        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_end_from_pinfo(
            p_pinfo=pinfo, p_reference_time=reference_time)

        self.assertEqual(an_admin_event.event_type, admin_event.EVENT_TYPE_PROCESS_END)
        self.assertEqual(pinfo.start_time, an_admin_event.process_start_time)
        self.assertEqual(reference_time, an_admin_event.event_time)
        self.assertEqual(pinfo.hostname, an_admin_event.hostname)
        self.assertEqual(pinfo.username, an_admin_event.username)
        self.assertEqual(pinfo.pid, an_admin_event.pid)
        self.assertEqual(None, an_admin_event.processname)
        self.assertEqual(pinfo.processhandler, an_admin_event.processhandler)
        self.assertEqual(pinfo.downtime, an_admin_event.downtime)

        pinfo2 = copy.copy(pinfo)
        pinfo2.start_time = None

        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_end_from_pinfo(
            p_pinfo=pinfo2)

        reference_time = datetime.datetime.now()

        diff_time = abs((an_admin_event.event_time - reference_time).total_seconds())

        self.assertLess(diff_time, 0.01)

    def test_create_admin_event_process_downtime_from_pinfo(self):
        pinfo = test_data.PINFO_1

        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_downtime_from_pinfo(
            p_pinfo=pinfo)

        self.assertEqual(an_admin_event.event_type, admin_event.EVENT_TYPE_PROCESS_DOWNTIME)
        self.assertEqual(pinfo.start_time, an_admin_event.process_start_time)
        self.assertEqual(pinfo.hostname, an_admin_event.hostname)
        self.assertEqual(pinfo.username, an_admin_event.username)
        self.assertEqual(pinfo.pid, an_admin_event.pid)
        self.assertEqual(None, an_admin_event.processname)
        self.assertEqual(pinfo.processhandler, an_admin_event.processhandler)
        self.assertEqual(pinfo.downtime, an_admin_event.downtime)

    def test_can_kill_processes(self):
        a_process_handler = TestProcessHandler.get_process_handler()

        self.assertFalse(a_process_handler.can_kill_processes())

    def test_property_process_infos(self):
        a_process_handler = TestProcessHandler.get_process_handler()

        process_infos = a_process_handler.process_infos

        self.assertIsNotNone(process_infos)
        self.assertIsInstance(process_infos, dict)
        self.assertEqual(0, len(process_infos))

    def test_handle_event_process_start(self):
        pinfo = test_data.PINFO_1

        a_process_handler = TestProcessHandler.get_process_handler()
        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo)
        a_process_handler.handle_event_process_start(p_event=an_admin_event)

        process_infos = a_process_handler.process_infos

        self.assertIsNotNone(process_infos)
        self.assertEqual(1, len(process_infos))

        key = an_admin_event.get_key()

        self.assertIn(key, process_infos)

    def test_handle_event_process_end(self):
        pinfo = test_data.PINFO_1

        a_process_handler = TestProcessHandler.get_process_handler()
        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo)
        a_process_handler.handle_event_process_start(p_event=an_admin_event)

        process_infos = a_process_handler.process_infos

        key = an_admin_event.get_key()

        self.assertIn(key, process_infos)

        reference_time = datetime.datetime.now()

        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_end_from_pinfo(
            p_pinfo=pinfo, p_reference_time=reference_time)
        returned_pinfo = a_process_handler.handle_event_process_end(p_event=an_admin_event)

        self.assertIsNotNone(returned_pinfo)

        self.assertIn(key, process_infos)
        self.assertEqual(1, len(process_infos))

        pinfo = process_infos[key]

        self.assertEqual(returned_pinfo, pinfo)
        self.assertEqual(reference_time, pinfo.end_time)

    def test_handle_event_process_downtime(self):
        pinfo = test_data.PINFO_1

        a_process_handler = TestProcessHandler.get_process_handler()
        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo)
        a_process_handler.handle_event_process_start(p_event=an_admin_event)

        process_infos = a_process_handler.process_infos

        key = an_admin_event.get_key()

        self.assertIn(key, process_infos)

        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_downtime_from_pinfo(
            p_pinfo=pinfo)
        an_admin_event.downtime = 123
        (returned_pinfo, handled) = a_process_handler.handle_event_process_downtime(p_event=an_admin_event)

        self.assertIsNotNone(returned_pinfo)
        self.assertTrue(handled)

        self.assertIn(key, process_infos)
        self.assertEqual(1, len(process_infos))

        pinfo = process_infos[key]

        self.assertEqual(returned_pinfo, pinfo)
        self.assertEqual(pinfo.downtime, an_admin_event.downtime)

    def test_handle_event_process_end_invalid_pinfo(self):
        pinfo = test_data.PINFO_1

        a_process_handler = TestProcessHandler.get_process_handler()
        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_end_from_pinfo(
            p_pinfo=pinfo)
        returned_pinfo = a_process_handler.handle_event_process_end(p_event=an_admin_event)

        self.assertIsNone(returned_pinfo)

        process_infos = a_process_handler.process_infos

        key = an_admin_event.get_key()

        self.assertNotIn(key, process_infos)

    def test_handle_event_process_downtime_invalid_pinfo(self):
        pinfo = test_data.PINFO_1

        a_process_handler = TestProcessHandler.get_process_handler()
        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_downtime_from_pinfo(
            p_pinfo=pinfo)
        (returned_pinfo, handled) = a_process_handler.handle_event_process_downtime(p_event=an_admin_event)

        self.assertIsNone(returned_pinfo)
        self.assertFalse(handled)

        process_infos = a_process_handler.process_infos

        key = an_admin_event.get_key()

        self.assertNotIn(key, process_infos)

    def test_handle_event_process_start_same_event(self):
        pinfo = test_data.PINFO_1

        a_process_handler = TestProcessHandler.get_process_handler()
        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo)
        a_process_handler.handle_event_process_start(p_event=an_admin_event)

        process_infos = a_process_handler.process_infos

        self.assertIsNotNone(process_infos)
        self.assertEqual(1, len(process_infos))

        key = an_admin_event.get_key()

        self.assertIn(key, process_infos)

        a_process_handler.handle_event_process_start(p_event=an_admin_event)
        self.assertEqual(1, len(process_infos))

    def test_handle_event_process_start_different_events(self):
        pinfo = test_data.PINFO_1

        a_process_handler = TestProcessHandler.get_process_handler()
        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo)
        a_process_handler.handle_event_process_start(p_event=an_admin_event)

        process_infos = a_process_handler.process_infos

        self.assertIsNotNone(process_infos)
        self.assertEqual(1, len(process_infos))

        key = an_admin_event.get_key()

        self.assertIn(key, process_infos)

        pinfo2 = copy.copy(pinfo)
        pinfo2.pid = pinfo2.pid + 1

        an_admin_event2 = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo2)
        a_process_handler.handle_event_process_start(p_event=an_admin_event2)

        self.assertEqual(2, len(process_infos))

        key = an_admin_event2.get_key()

        self.assertIn(key, process_infos)

    def test_handle_event_downtime(self):
        pinfo = test_data.PINFO_1

        a_process_handler = TestProcessHandler.get_process_handler()
        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(p_pinfo=pinfo)
        a_process_handler.handle_event_process_start(p_event=an_admin_event)

        pinfo.downtime = 123

        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_downtime_from_pinfo(p_pinfo=pinfo)
        a_process_handler.handle_event_process_downtime(p_event=an_admin_event)

        process_infos = a_process_handler.process_infos

        self.assertIsNotNone(process_infos)
        self.assertEqual(1, len(process_infos))

        key = an_admin_event.get_key()

        self.assertIn(key, process_infos)

        process_info = process_infos[key]

        self.assertEqual(123, process_info.downtime)

    def test_handle_event_kill_process(self):
        pinfo = test_data.PINFO_1

        a_process_handler = TestProcessHandler.get_process_handler()
        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo)
        a_process_handler.handle_event_kill_process(p_event=an_admin_event)

    def test_add_historic_process(self):
        pinfo = test_data.PINFO_1

        a_process_handler = TestProcessHandler.get_process_handler()
        a_process_handler.add_historic_process(p_process_info=pinfo)

        process_infos = a_process_handler.process_infos

        self.assertIsNotNone(process_infos)
        self.assertEqual(1, len(process_infos))

        key = pinfo.get_key()

        self.assertIn(key, process_infos)

    def test_get_artificial_termination_events(self):
        pinfo = test_data.PINFO_1

        a_process_handler = TestProcessHandler.get_process_handler()
        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo)
        a_process_handler.handle_event_process_start(p_event=an_admin_event)

        pinfo = test_data.PINFO_2

        an_admin_event2 = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo)
        an_admin_event2.pid = an_admin_event2.pid + 1
        a_process_handler.handle_event_process_start(p_event=an_admin_event2)
        a_process_handler.handle_event_process_end(p_event=an_admin_event2)

        process_infos = a_process_handler.process_infos

        self.assertIsNotNone(process_infos)
        self.assertEqual(2, len(process_infos))

        termination_events = a_process_handler.get_artificial_termination_events()
        self.assertIsNotNone(termination_events)
        self.assertEqual(1, len(termination_events))

        termination_event = termination_events[0]

        self.assertEqual(admin_event.EVENT_TYPE_PROCESS_END, termination_event.event_type)
        self.assertEqual(termination_event.pid, an_admin_event.pid)

    def test_get_artificial_activation_events(self):
        pinfo = test_data.PINFO_1

        a_process_handler = TestProcessHandler.get_process_handler()
        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo)
        a_process_handler.handle_event_process_start(p_event=an_admin_event)

        pinfo = test_data.PINFO_2

        an_admin_event2 = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo)
        an_admin_event2.pid = an_admin_event2.pid + 1
        a_process_handler.handle_event_process_start(p_event=an_admin_event2)
        a_process_handler.handle_event_process_end(p_event=an_admin_event2)

        process_infos = a_process_handler.process_infos

        self.assertIsNotNone(process_infos)
        self.assertEqual(2, len(process_infos))

        activation_events = a_process_handler.get_artificial_activation_events()
        self.assertIsNotNone(activation_events)
        self.assertEqual(1, len(activation_events))

        activation_event = activation_events[0]

        self.assertEqual(admin_event.EVENT_TYPE_PROCESS_START, activation_event.event_type)
        self.assertEqual(activation_event.pid, an_admin_event.pid)

    def test_get_downtime_corrected_admin_events(self):
        pinfo1 = copy.copy(test_data.PINFO_1)

        a_process_handler = TestProcessHandler.get_process_handler()
        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo1)
        an_admin_event.downtime = 0
        a_process_handler.handle_event_process_start(p_event=an_admin_event)

        pinfo2 = copy.copy(test_data.PINFO_2)

        an_admin_event2 = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo2)
        an_admin_event2.pid = an_admin_event2.pid + 1
        an_admin_event2.downtime = 0
        a_process_handler.handle_event_process_start(p_event=an_admin_event2)
        a_process_handler.handle_event_process_end(p_event=an_admin_event2)

        process_infos = a_process_handler.process_infos

        self.assertIsNotNone(process_infos)
        self.assertEqual(2, len(process_infos))

        corrected_events = a_process_handler.get_downtime_corrected_admin_events(p_downtime=DOWNTIME)
        self.assertIsNotNone(corrected_events)
        self.assertEqual(1, len(corrected_events))

        corrected_event = corrected_events[0]

        self.assertEqual(admin_event.EVENT_TYPE_PROCESS_DOWNTIME, corrected_event.event_type)
        self.assertEqual(corrected_event.pid, an_admin_event.pid)
        self.assertEqual(DOWNTIME, corrected_event.downtime)

        key = an_admin_event.get_key()
        pinfo1 = process_infos[key]

        key = an_admin_event2.get_key()
        pinfo2 = process_infos[key]

        self.assertEqual(DOWNTIME, pinfo1.downtime)
        self.assertEqual(0, pinfo2.downtime)

    def test_scan_processes(self):
        a_process_handler = TestProcessHandler.get_process_handler()
        session_context = object()
        a_process_handler.scan_processes(p_session_context=session_context, p_reference_time=None, p_host_name=None,
                                         p_login_mapping=None, p_server_group=None, p_process_regex_map=None,
                                         p_prohibited_process_map=None)


if __name__ == "__main__":
    unittest.main()
