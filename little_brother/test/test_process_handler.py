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

import unittest
import datetime
import copy

import little_brother.process_handler as process_handler

from little_brother import admin_event
from little_brother.test import test_data
from python_base_app.test import base_test


class TestProcessHandler(base_test.BaseTestCase):

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

        reference_time = datetime.datetime.now()

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

    def get_process_handler(self):

        config = process_handler.ProcessHandlerConfigModel(p_section_name="ProcessHandler")
        return process_handler.ProcessHandler(p_config=config)

    def test_can_kill_processes(self):

        a_process_handler = self.get_process_handler()

        self.assertFalse(a_process_handler.can_kill_processes())

    def test_property_process_infos(self):

        a_process_handler = self.get_process_handler()

        process_infos = a_process_handler.process_infos

        self.assertIsNotNone(process_infos)
        self.assertIsInstance(process_infos, dict)
        self.assertEqual(0, len(process_infos))

    def test_handle_event_process_start(self):

        pinfo = test_data.PINFO_1

        a_process_handler = self.get_process_handler()
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

        a_process_handler = self.get_process_handler()
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

        a_process_handler = self.get_process_handler()
        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo)
        a_process_handler.handle_event_process_start(p_event=an_admin_event)

        process_infos = a_process_handler.process_infos

        key = an_admin_event.get_key()

        self.assertIn(key, process_infos)

        reference_time = datetime.datetime.now()

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

        a_process_handler = self.get_process_handler()
        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_end_from_pinfo(
            p_pinfo=pinfo)
        returned_pinfo = a_process_handler.handle_event_process_end(p_event=an_admin_event)

        self.assertIsNone(returned_pinfo)

        process_infos = a_process_handler.process_infos

        key = an_admin_event.get_key()

        self.assertNotIn(key, process_infos)


    def test_handle_event_process_downtime_invalid_pinfo(self):

        pinfo = test_data.PINFO_1

        a_process_handler = self.get_process_handler()
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

        a_process_handler = self.get_process_handler()
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

        a_process_handler = self.get_process_handler()
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

        a_process_handler = self.get_process_handler()
        an_admin_event = process_handler.ProcessHandler.create_admin_event_process_start_from_pinfo(
            p_pinfo=pinfo)
        a_process_handler.handle_event_process_start(p_event=an_admin_event)

        process_infos = a_process_handler.process_infos

        self.assertIsNotNone(process_infos)
        self.assertEqual(1, len(process_infos))

        key = an_admin_event.get_key()

        self.assertIn(key, process_infos)


if __name__ == "__main__":
    unittest.main()
