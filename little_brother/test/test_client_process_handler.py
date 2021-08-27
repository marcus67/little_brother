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

from little_brother import admin_event
from little_brother import client_process_handler
from little_brother import dependency_injection
from little_brother import login_mapping
from little_brother.persistence.persistence import Persistence
from little_brother.persistence.session_context import SessionContext
from little_brother.test import dummy_process_iterator
from little_brother.test import test_data
from little_brother.test.persistence import test_persistence
from python_base_app.test import base_test


class TestClientProcessHandler(base_test.BaseTestCase):

    def setUp(self):
        dependency_injection.reset()

    def check_list_has_n_elements(self, p_list, p_n):

        self.assertIsNotNone(p_list)
        self.assertIsInstance(p_list, list)
        self.assertEqual(len(p_list), p_n)

    def check_default_data(self, p_event):

        self.assertEqual(p_event.hostname, test_data.HOSTNAME_1)
        self.assertEqual(p_event.username, test_data.USER_1)
        self.assertEqual(p_event.process_start_time, test_data.START_TIME_1)
        self.assertEqual(p_event.pid, test_data.PID_1)

    def test_single_process_before(self):
        process_iterator_factory = dummy_process_iterator.DummyProcessFactory(
            p_processes=test_data.PROCESSES_1, p_login_mapping=test_data.LOGIN_MAPPING)

        config = client_process_handler.ClientProcessHandlerConfigModel()
        process_handler = client_process_handler.ClientProcessHandler(
            p_config=config, p_process_iterator_factory=process_iterator_factory)
        session_context = object()
        process_iterator_factory.set_reference_time(
            p_reference_time=test_data.START_TIME_1 + datetime.timedelta(seconds=-1))
        events = process_handler.scan_processes(p_session_context=session_context,
                                                p_server_group=login_mapping.DEFAULT_SERVER_GROUP,
                                                p_login_mapping=test_data.LOGIN_MAPPING,
                                                p_host_name=test_data.HOSTNAME_1,
                                                p_process_regex_map=test_data.get_process_regex_map_1(),
                                                p_prohibited_process_regex_map=None,
                                                p_reference_time=datetime.datetime.now())

        self.check_list_has_n_elements(p_list=events, p_n=0)

    @staticmethod
    def get_dummy_process_handler(p_reference_time=None, p_processes=None, p_config=None):

        if p_processes is None:
            p_processes = test_data.PROCESSES_1

        if p_reference_time is None:
            p_reference_time = test_data.START_TIME_1 + datetime.timedelta(seconds=1)

        process_iterator_factory = dummy_process_iterator.DummyProcessFactory(
            p_processes=p_processes, p_login_mapping=test_data.LOGIN_MAPPING)

        if p_config is None:
            p_config = client_process_handler.ClientProcessHandlerConfigModel()

        process_handler = client_process_handler.ClientProcessHandler(
            p_config=p_config, p_process_iterator_factory=process_iterator_factory)
        process_iterator_factory.set_reference_time(p_reference_time=p_reference_time)

        return process_handler

    def test_single_process_active(self):

        test_persistence.TestPersistence.create_dummy_persistence(self._logger)

        dummy_persistence: test_persistence.TestPersistence = dependency_injection.container[Persistence]

        with SessionContext(p_persistence=dummy_persistence) as session_context:
            process_handler = self.get_dummy_process_handler()

            events = process_handler.scan_processes(p_session_context=session_context,
                                                    p_server_group=login_mapping.DEFAULT_SERVER_GROUP,
                                                    p_login_mapping=test_data.LOGIN_MAPPING,
                                                    p_host_name=test_data.HOSTNAME_1,
                                                    p_process_regex_map=test_data.get_process_regex_map_1(),
                                                    p_prohibited_process_regex_map=None,
                                                    p_reference_time=datetime.datetime.now())

            self.check_list_has_n_elements(p_list=events, p_n=1)

            event = events[0]

            self.assertEqual(event.event_type, admin_event.EVENT_TYPE_PROCESS_START)
            self.assertEqual(event.processhandler, process_handler.id)
            self.check_default_data(p_event=event)

    def test_single_process_active_process_as_pattern(self):

        test_persistence.TestPersistence.create_dummy_persistence(self._logger)

        dummy_persistence: test_persistence.TestPersistence = dependency_injection.container[Persistence]

        with SessionContext(p_persistence=dummy_persistence) as session_context:
            process_handler = self.get_dummy_process_handler(p_processes=test_data.PROCESSES_PATH_1)

            events = process_handler.scan_processes(p_session_context=session_context,
                                                    p_server_group=login_mapping.DEFAULT_SERVER_GROUP,
                                                    p_login_mapping=test_data.LOGIN_MAPPING,
                                                    p_host_name=test_data.HOSTNAME_1,
                                                    p_process_regex_map=test_data.get_process_regex_map_1(),
                                                    p_prohibited_process_regex_map=None,
                                                    p_reference_time=datetime.datetime.now())

            self.check_list_has_n_elements(p_list=events, p_n=1)

            event = events[0]

            self.assertEqual(event.event_type, admin_event.EVENT_TYPE_PROCESS_START)
            self.assertEqual(event.processhandler, process_handler.id)
            self.check_default_data(p_event=event)

    def test_single_process_active_long_pattern(self):

        process_handler = self.get_dummy_process_handler(p_processes=test_data.PROCESSES_PATH_1)

        test_persistence.TestPersistence.create_dummy_persistence(self._logger)

        dummy_persistence: test_persistence.TestPersistence = dependency_injection.container[Persistence]

        with SessionContext(p_persistence=dummy_persistence) as session_context:
            events = process_handler.scan_processes(
                p_session_context=session_context,
                p_server_group=login_mapping.DEFAULT_SERVER_GROUP,
                p_login_mapping=test_data.LOGIN_MAPPING,
                p_host_name=test_data.HOSTNAME_1,
                p_process_regex_map=test_data.get_process_path_regex_map_1(),
                p_prohibited_process_regex_map=test_data.get_prohibited_process_regex_map_1(),
                p_reference_time=datetime.datetime.now())

            self.check_list_has_n_elements(p_list=events, p_n=0)

    def test_single_process_active_command_line_options_active(self):

        test_persistence.TestPersistence.create_dummy_persistence(self._logger)

        dummy_persistence: test_persistence.TestPersistence = dependency_injection.container[Persistence]

        with SessionContext(p_persistence=dummy_persistence) as session_context:
            config = client_process_handler.ClientProcessHandlerConfigModel()
            config.scan_command_line_options = True

            process_handler = self.get_dummy_process_handler(p_processes=test_data.PROCESSES_CMD_LINE_1,
                                                             p_config=config)

            events = process_handler.scan_processes(p_session_context=session_context,
                                                    p_server_group=login_mapping.DEFAULT_SERVER_GROUP,
                                                    p_login_mapping=test_data.LOGIN_MAPPING,
                                                    p_host_name=test_data.HOSTNAME_1,
                                                    p_process_regex_map=test_data.get_process_cmd_line_option_regex_map_1(),
                                                    p_prohibited_process_regex_map=None,
                                                    p_reference_time=datetime.datetime.now())

            self.check_list_has_n_elements(p_list=events, p_n=1)

            event = events[0]

            self.assertEqual(event.event_type, admin_event.EVENT_TYPE_PROCESS_START)
            self.assertEqual(event.processhandler, process_handler.id)
            self.check_default_data(p_event=event)

    def test_single_process_active_command_line_options_inactive(self):

        config = client_process_handler.ClientProcessHandlerConfigModel()
        config.scan_command_line_options = False

        process_handler = self.get_dummy_process_handler(p_processes=test_data.PROCESSES_CMD_LINE_1,
                                                         p_config=config)

        session_context = object()
        events = process_handler.scan_processes(
            p_session_context=session_context,
            p_server_group=login_mapping.DEFAULT_SERVER_GROUP,
            p_login_mapping=test_data.LOGIN_MAPPING,
            p_host_name=test_data.HOSTNAME_1,
            p_process_regex_map=test_data.get_process_cmd_line_option_regex_map_1(),
            p_prohibited_process_regex_map=test_data.get_prohibited_process_regex_map_1(),
            p_reference_time=datetime.datetime.now())

        self.check_list_has_n_elements(p_list=events, p_n=0)

    def test_single_process_active_command_line_options_inactive_pattern_part_of_path(self):

        config = client_process_handler.ClientProcessHandlerConfigModel()
        config.scan_command_line_options = False

        process_handler = self.get_dummy_process_handler(p_processes=test_data.PROCESSES_CMD_LINE_1,
                                                         p_config=config)

        session_context = object()
        events = process_handler.scan_processes(
            p_session_context=session_context,
            p_server_group=login_mapping.DEFAULT_SERVER_GROUP,
            p_login_mapping=test_data.LOGIN_MAPPING,
            p_host_name=test_data.HOSTNAME_1,
            p_process_regex_map=test_data.get_process_cmd_line_option_part_of_path_regex_map_1(),
            p_prohibited_process_regex_map=test_data.get_prohibited_process_regex_map_1(),
            p_reference_time=datetime.datetime.now())

        self.check_list_has_n_elements(p_list=events, p_n=0)

    def test_single_process_after(self):
        process_iterator_factory = dummy_process_iterator.DummyProcessFactory(
            p_processes=test_data.PROCESSES_2, p_login_mapping=test_data.LOGIN_MAPPING)

        config = client_process_handler.ClientProcessHandlerConfigModel()
        process_handler = client_process_handler.ClientProcessHandler(
            p_config=config, p_process_iterator_factory=process_iterator_factory)
        session_context = object()
        process_iterator_factory.set_reference_time(
            p_reference_time=test_data.END_TIME_1 + datetime.timedelta(seconds=1))
        events = process_handler.scan_processes(p_session_context=session_context,
                                                p_server_group=login_mapping.DEFAULT_SERVER_GROUP,
                                                p_login_mapping=test_data.LOGIN_MAPPING,
                                                p_host_name=test_data.HOSTNAME_1,
                                                p_process_regex_map=test_data.get_process_regex_map_1(),
                                                p_prohibited_process_regex_map=None,
                                                p_reference_time=datetime.datetime.now())

        self.check_list_has_n_elements(p_list=events, p_n=0)

    def test_single_process_active_and_inactive(self):

        test_persistence.TestPersistence.create_dummy_persistence(self._logger)

        dummy_persistence: test_persistence.TestPersistence = dependency_injection.container[Persistence]

        with SessionContext(p_persistence=dummy_persistence) as session_context:
            processes = copy.deepcopy(test_data.PROCESSES_1)

            process_iterator_factory = dummy_process_iterator.DummyProcessFactory(
                p_processes=processes, p_login_mapping=test_data.LOGIN_MAPPING)

            config = client_process_handler.ClientProcessHandlerConfigModel()
            process_handler = client_process_handler.ClientProcessHandler(
                p_config=config, p_process_iterator_factory=process_iterator_factory)
            process_iterator_factory.set_reference_time(
                p_reference_time=test_data.START_TIME_1 + datetime.timedelta(seconds=1))
            events = process_handler.scan_processes(p_session_context=session_context,
                                                    p_server_group=login_mapping.DEFAULT_SERVER_GROUP,
                                                    p_login_mapping=test_data.LOGIN_MAPPING,
                                                    p_host_name=test_data.HOSTNAME_1,
                                                    p_process_regex_map=test_data.get_process_regex_map_1(),
                                                    p_prohibited_process_regex_map=None,
                                                    p_reference_time=datetime.datetime.now())

            self.check_list_has_n_elements(p_list=events, p_n=1)

            event = events[0]

            self.assertEqual(event.event_type, admin_event.EVENT_TYPE_PROCESS_START)
            self.assertEqual(event.processhandler, process_handler.id)
            self.check_default_data(p_event=event)

            process_handler.handle_event_process_start(p_event=event)

            processes[0].end_time = test_data.END_TIME_1

            now = datetime.datetime.now()
            process_iterator_factory.set_reference_time(
                p_reference_time=test_data.END_TIME_1 + datetime.timedelta(seconds=1))
            events = process_handler.scan_processes(p_session_context=session_context,
                                                    p_server_group=login_mapping.DEFAULT_SERVER_GROUP,
                                                    p_login_mapping=test_data.LOGIN_MAPPING,
                                                    p_host_name=test_data.HOSTNAME_1,
                                                    p_process_regex_map=test_data.get_process_regex_map_1(),
                                                    p_prohibited_process_regex_map=None,
                                                    p_reference_time=now)

            self.check_list_has_n_elements(p_list=events, p_n=1)

            event = events[0]

            self.assertEqual(event.event_type, admin_event.EVENT_TYPE_PROCESS_END)
            self.assertEqual(event.event_time, now)
            self.assertEqual(event.processhandler, process_handler.id)

            self.check_default_data(p_event=event)
