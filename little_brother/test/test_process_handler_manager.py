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
import logging
import unittest

from little_brother import dependency_injection, db_migrations
from little_brother.admin_data_handler import AdminDataHandler
from little_brother.admin_event import AdminEvent, EVENT_TYPE_PROCESS_START
from little_brother.app import ProcessIteratorFactory
from little_brother.app_control_config_model import AppControlConfigModel
from little_brother.client_device_handler import ClientDeviceHandler, ClientDeviceHandlerConfigModel
from little_brother.client_process_handler import ClientProcessHandlerConfigModel, ClientProcessHandler
from little_brother.language import Language
from little_brother.login_mapping import LoginMapping, DEFAULT_SERVER_GROUP
from little_brother.persistence.persistence import Persistence
from little_brother.persistence.persistent_process_info import ProcessInfo
from little_brother.process_handler_manager import ProcessHandlerManager
from little_brother.rule_handler import RuleHandler
from little_brother.test.persistence.test_persistence import TestPersistence
from little_brother.test.test_rule_handler import TestRuleHandler, TEST_USER
from little_brother.user_manager import UserManager
from python_base_app.pinger import PingerConfigModel, Pinger
from python_base_app.test import base_test

HOSTNAME = "some.host"


class TestProcessHandlerManager(base_test.BaseTestCase):

    def setUp(self):
        dependency_injection.reset()

    def create_default_process_handlers(self):
        self._client_process_handler_config = ClientProcessHandlerConfigModel()
        self._client_process_handler = ClientProcessHandler(p_config=self._client_process_handler_config,
                                                            p_process_iterator_factory=ProcessIteratorFactory())

        self._pinger_config = PingerConfigModel()
        self._pinger = Pinger(p_config=self._pinger_config)

        self._client_device_handler_config = ClientDeviceHandlerConfigModel()
        self._client_device_handler = ClientDeviceHandler(p_config=self._client_device_handler_config,
                                                          p_pinger=self._pinger)

        self._process_handlers = {
            self._client_process_handler.id: self._client_process_handler,
            self._client_device_handler.id: self._client_device_handler
        }

    def create_default_process_handler_manager(self):
        self._config = AppControlConfigModel()
        self.create_default_process_handlers()
        self._language = Language()
        self._login_mapping = LoginMapping()
        self._manager = ProcessHandlerManager(p_config=self._config, p_process_handlers=self._process_handlers,
                                              p_language=self._language,
                                              p_is_master=True, p_login_mapping=self._login_mapping)

    def test_constructor(self):
        self.create_default_process_handler_manager()
        self.assertIsNotNone(self._manager)

    def test_get_process_handler(self):
        self.create_default_process_handler_manager()
        self.assertIsNotNone(self._manager)

        handler = self._manager.get_process_handler(p_id=self._client_process_handler.id)

        self.assertIsNotNone(handler)
        self.assertIsInstance(handler, ClientProcessHandler)

        handler = self._manager.get_process_handler(p_id=self._client_device_handler.id)

        self.assertIsNotNone(handler)
        self.assertIsInstance(handler, ClientDeviceHandler)

    def create_handlers(self):
        app_control_config = AppControlConfigModel()
        admin_data_handler = AdminDataHandler(p_config=app_control_config)
        dependency_injection.container[AdminDataHandler] = admin_data_handler

        persistence: Persistence = dependency_injection.container[Persistence]

        rule_handler = TestRuleHandler.create_dummy_rule_handler(p_persistence=persistence)
        dependency_injection.container[RuleHandler] = rule_handler

        login_mapping = LoginMapping()

        user_manager = UserManager(p_config=app_control_config, p_is_master=True, p_login_mapping=login_mapping,
                                   p_server_group=DEFAULT_SERVER_GROUP)
        dependency_injection.container[UserManager] = user_manager

        migrator = db_migrations.DatabaseMigrations(p_logger=self._logger, p_persistence=persistence)
        migrator.migrate_ruleset_configs(TestRuleHandler.create_dummy_ruleset_configs())

    def test_handle_event_process_start(self):
        self.create_default_process_handler_manager()
        self.assertIsNotNone(self._manager)

        logger = logging.Logger("root")

        TestPersistence.create_dummy_persistence(p_logger=logger, p_delete=True)

        persistence: Persistence = dependency_injection.container[Persistence]

        self.create_handlers()

        event = AdminEvent(p_hostname=HOSTNAME, p_locale="en_US", p_username=TEST_USER,
                           p_process_start_time=datetime.datetime.now(), p_processname="test",
                           p_event_type=EVENT_TYPE_PROCESS_START, p_processhandler=self._client_process_handler.id)

        self._manager.handle_event_process_start(p_event=event)

        self.assertEqual(1, persistence.count_rows(p_entity=ProcessInfo))

    def test_handle_event_process_stop(self):
        self.create_default_process_handler_manager()
        self.assertIsNotNone(self._manager)

        logger = logging.Logger("root")

        TestPersistence.create_dummy_persistence(p_logger=logger, p_delete=True)

        persistence: Persistence = dependency_injection.container[Persistence]

        self.create_handlers()

        event = AdminEvent(p_hostname=HOSTNAME, p_locale="en_US", p_username=TEST_USER,
                           p_process_start_time=datetime.datetime.now(), p_processname="test",
                           p_event_type=EVENT_TYPE_PROCESS_START, p_processhandler=self._client_process_handler.id)

        self._manager.handle_event_process_start(p_event=event)

        self.assertEqual(1, persistence.count_rows(p_entity=ProcessInfo))

        event.event_time = datetime.datetime.now()

        self._manager.handle_event_process_end(p_event=event)

        self.assertEqual(1, persistence.count_rows(p_entity=ProcessInfo))

    def test_load_historic_process_infos(self):
        self.create_default_process_handler_manager()
        self.assertIsNotNone(self._manager)

        logger = logging.Logger("root")

        TestPersistence.create_dummy_persistence(p_logger=logger, p_delete=True)

        persistence: Persistence = dependency_injection.container[Persistence]

        self.create_handlers()

        event = AdminEvent(p_hostname=HOSTNAME, p_locale="en_US", p_username=TEST_USER,
                           p_process_start_time=datetime.datetime.now(), p_processname="test",
                           p_event_type=EVENT_TYPE_PROCESS_START, p_processhandler=self._client_process_handler.id)

        self._manager.handle_event_process_start(p_event=event)

        self.assertEqual(1, persistence.count_rows(p_entity=ProcessInfo))

        self._client_process_handler._process_infos = {}

        self._manager.load_historic_process_infos()

        self.assertEqual(1, len(self._client_process_handler._process_infos))


if __name__ == "__main__":
    unittest.main()
