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
import os
import time
import unittest

# from little_brother import constants, dependency_injection
from little_brother import dependency_injection, admin_event, constants
from little_brother.admin_event import AdminEvent
from little_brother.api.master_connector import MasterConnectorConfigModel, MasterConnector
from little_brother.event_handler import EventHandler
from little_brother.persistence.persistence import Persistence
from little_brother.persistence.persistent_daily_user_status_entity_manager import DailyUserStatusEntityManager
from little_brother.persistence.persistent_rule_set import RuleSet
from little_brother.persistence.persistent_user import User
from little_brother.persistence.persistent_user_entity_manager import UserEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.test.web.base_test_status_server import BaseTestStatusServer

USERNAME = "user1"
ACCESS_CODE = "$ecret"
EXTENSION_LENGTH = 5
OPTIONAL_TIME_PER_DAY_IN_SECONDS = 30 * 60


class TestApiViewHandler(BaseTestStatusServer):

    def setUp(self):
        super().setUp()
        self.last_event = None

    def handle_event(self, p_event):
        self.last_event = p_event

    def test_dummy_event(self):
        self.create_dummy_status_server()
        self._status_server.start_server()

        event_handler = dependency_injection.container[EventHandler]
        event_handler.register_event_handler(p_event_type=admin_event.EVENT_TYPE_DUMMY_1, p_handler=self.handle_event)

        port = os.getenv("STATUS_SERVER_PORT", "5555")

        master_connector_config = MasterConnectorConfigModel()
        master_connector_config.host_url = "http://localhost:" + port

        master_connector = MasterConnector(p_config=master_connector_config)

        hostname = "SLAVE"
        process_name = "MY_PROCESS"

        event = AdminEvent(p_event_type=admin_event.EVENT_TYPE_DUMMY_1,
                           p_hostname=hostname,
                           p_processname=process_name)
        outgoing_events = [event]

        time.sleep(1)

        received_events = master_connector.send_events(p_hostname=hostname, p_events=outgoing_events)

        self.assertIsNotNone(received_events)
        self.assertEqual(3, len(received_events))

        event_handler.process_queue()

        self.assertIsNotNone(self.last_event)
        self.assertEqual(hostname, self.last_event.hostname)
        self.assertEqual(process_name, self.last_event.processname)

    def test_status_wrong_user(self):
        self.create_dummy_status_server()
        self._status_server.start_server()

        event_handler = dependency_injection.container[EventHandler]
        event_handler.register_event_handler(p_event_type=admin_event.EVENT_TYPE_DUMMY_1, p_handler=self.handle_event)

        port = os.getenv("STATUS_SERVER_PORT", "5555")

        master_connector_config = MasterConnectorConfigModel()
        master_connector_config.host_url = "http://localhost:" + port

        master_connector = MasterConnector(p_config=master_connector_config)

        result = master_connector.request_status(p_username="USER")

        self.assertIsNone(result)

    def test_request_time_extension_no_user(self):
        self.create_dummy_status_server()
        self._status_server.start_server()

        port = os.getenv("STATUS_SERVER_PORT", "5555")

        master_connector_config = MasterConnectorConfigModel()
        master_connector_config.host_url = "http://localhost:" + port

        master_connector = MasterConnector(p_config=master_connector_config)

        result = master_connector.request_time_extension(p_username=None, p_access_code="ABC", p_extension_length=5)

        self.assertIsNotNone(result)
        self.assertEqual(constants.HTTP_STATUS_CODE_NOT_FOUND, result)

    def create_user(self, p_session_context: SessionContext):
        session = p_session_context.get_session()

        user = User()
        session.add(user)
        user.username = USERNAME
        user.access_code = ACCESS_CODE

        ruleset = RuleSet()
        session.add(ruleset)
        ruleset.optional_time_per_day = OPTIONAL_TIME_PER_DAY_IN_SECONDS

        user.rulesets.append(ruleset)

        session.commit()

        return user.id

    def test_request_time_extension_valid_user(self):
        self.create_dummy_status_server()
        self._status_server.start_server()

        port = os.getenv("STATUS_SERVER_PORT", "5555")

        persistence = dependency_injection.container[Persistence]

        with SessionContext(p_persistence=persistence) as session_context:
            user_id = self.create_user(p_session_context=session_context)

        user_entity_manager = dependency_injection.container[UserEntityManager]

        user : User = user_entity_manager.get_by_id(p_session_context=session_context, p_id=user_id)
        user.active = True

        session_context.get_session().commit()

        master_connector_config = MasterConnectorConfigModel()
        master_connector_config.host_url = "http://localhost:" + port

        master_connector = MasterConnector(p_config=master_connector_config)

        result = master_connector.request_time_extension(p_username=USERNAME, p_access_code=ACCESS_CODE,
                                                         p_extension_length=EXTENSION_LENGTH)

        self.assertIsNotNone(result)
        self.assertEqual(constants.HTTP_STATUS_CODE_OK, result)

        daily_user_status_entity_manager = dependency_injection.container[DailyUserStatusEntityManager]

        with SessionContext(p_persistence=persistence) as session_context:
            user_status = daily_user_status_entity_manager.get_user_status(
                p_session_context=session_context, p_user_id=user_id, p_reference_date=datetime.date.today())

            self.assertIsNotNone(user_status)
            self.assertEqual(EXTENSION_LENGTH, user_status.optional_time_used)


if __name__ == "__main__":
    unittest.main()
