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

import datetime
import copy

from python_base_app.test import base_test

from little_brother import client_process_handler
from little_brother import admin_event

from little_brother.test import test_data
from little_brother.test import dummy_process_iterator

class TestClientProcessHandler(base_test.BaseTestCase):

    def test_single_process_before(self):
        
        process_iterator_factory = dummy_process_iterator.DummyProcessFactory(
            p_processes=test_data.PROCESSES_1, p_uid_map=test_data.UID_MAP)
        
        config = client_process_handler.ClientProcessHandlerConfigModel()
        process_handler = client_process_handler.ClientProcessHandler(p_config=config, p_process_iterator_factory=process_iterator_factory)
        process_iterator_factory.set_reference_time(p_reference_time=test_data.START_TIME_1 + datetime.timedelta(seconds=-1))
        events = process_handler.scan_processes(p_uid_map=test_data.UID_MAP, p_host_name=test_data.HOSTNAME_1, 
                                                p_process_regex_map=test_data.PROCESS_REGEX_MAP_1, p_reference_time=datetime.datetime.now())
        
        self.assertIsNotNone(events)
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 0)
        
    def test_single_process_active(self):
        
        process_iterator_factory = dummy_process_iterator.DummyProcessFactory(
            p_processes=test_data.PROCESSES_1, p_uid_map=test_data.UID_MAP)
        
        config = client_process_handler.ClientProcessHandlerConfigModel()
        process_handler = client_process_handler.ClientProcessHandler(p_config=config, p_process_iterator_factory=process_iterator_factory)
        process_iterator_factory.set_reference_time(p_reference_time=test_data.START_TIME_1 + datetime.timedelta(seconds=1))
        events = process_handler.scan_processes(p_uid_map=test_data.UID_MAP, p_host_name=test_data.HOSTNAME_1, 
                                                p_process_regex_map=test_data.PROCESS_REGEX_MAP_1, p_reference_time=datetime.datetime.now())
        
        self.assertIsNotNone(events)
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 1)
        
        event = events[0]
        
        self.assertEqual(event.event_type, admin_event.EVENT_TYPE_PROCESS_START)
        self.assertEqual(event.hostname, test_data.HOSTNAME_1)
        self.assertEqual(event.processhandler, process_handler.id)
        self.assertEqual(event.username, test_data.USER_1)
        self.assertEqual(event.process_start_time, test_data.START_TIME_1)
        self.assertEqual(event.pid, test_data.PID_1)
        
    def test_single_process_after(self):
        
        process_iterator_factory = dummy_process_iterator.DummyProcessFactory(
            p_processes=test_data.PROCESSES_2, p_uid_map=test_data.UID_MAP)
        
        config = client_process_handler.ClientProcessHandlerConfigModel()
        process_handler = client_process_handler.ClientProcessHandler(p_config=config, p_process_iterator_factory=process_iterator_factory)
        process_iterator_factory.set_reference_time(p_reference_time=test_data.END_TIME_1 + datetime.timedelta(seconds=1))
        events = process_handler.scan_processes(p_uid_map=test_data.UID_MAP, p_host_name=test_data.HOSTNAME_1, 
                                                p_process_regex_map=test_data.PROCESS_REGEX_MAP_1, p_reference_time=datetime.datetime.now())
        
        self.assertIsNotNone(events)
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 0)
        
        
    def test_single_process_active_and_inactive(self):
        
        processes = copy.deepcopy(test_data.PROCESSES_1)
        
        process_iterator_factory = dummy_process_iterator.DummyProcessFactory(
            p_processes=processes, p_uid_map=test_data.UID_MAP)
        
        
        
        config = client_process_handler.ClientProcessHandlerConfigModel()
        process_handler = client_process_handler.ClientProcessHandler(p_config=config, p_process_iterator_factory=process_iterator_factory)
        process_iterator_factory.set_reference_time(p_reference_time=test_data.START_TIME_1 + datetime.timedelta(seconds=1))
        events = process_handler.scan_processes(p_uid_map=test_data.UID_MAP, p_host_name=test_data.HOSTNAME_1, 
                                                p_process_regex_map=test_data.PROCESS_REGEX_MAP_1, p_reference_time=datetime.datetime.now())
        
        self.assertIsNotNone(events)
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 1)
        
        event = events[0]
        
        self.assertEqual(event.event_type, admin_event.EVENT_TYPE_PROCESS_START)
        self.assertEqual(event.hostname, test_data.HOSTNAME_1)
        self.assertEqual(event.processhandler, process_handler.id)
        self.assertEqual(event.username, test_data.USER_1)
        self.assertEqual(event.process_start_time, test_data.START_TIME_1)
        self.assertEqual(event.pid, test_data.PID_1)
        
        process_handler.handle_event_process_start(p_event=event)
        
        processes[0].end_time = test_data.END_TIME_1

        now = datetime.datetime.now()
        process_iterator_factory.set_reference_time(p_reference_time=test_data.END_TIME_1 + datetime.timedelta(seconds=1))
        events = process_handler.scan_processes(p_uid_map=test_data.UID_MAP, p_host_name=test_data.HOSTNAME_1, 
                                                p_process_regex_map=test_data.PROCESS_REGEX_MAP_1, p_reference_time=now)
        
        self.assertIsNotNone(events)
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 1)
        
        event = events[0]
        
        self.assertEqual(event.event_type, admin_event.EVENT_TYPE_PROCESS_END)
        self.assertEqual(event.hostname, test_data.HOSTNAME_1)
        self.assertEqual(event.processhandler, process_handler.id)
        self.assertEqual(event.username, test_data.USER_1)
        self.assertEqual(event.process_start_time, test_data.START_TIME_1)
        self.assertEqual(event.event_time, now)
        self.assertEqual(event.pid, test_data.PID_1)
        