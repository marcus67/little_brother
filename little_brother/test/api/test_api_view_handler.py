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
import os
import time
import unittest

# from little_brother import constants, dependency_injection
from little_brother import dependency_injection, admin_event
from little_brother.admin_event import AdminEvent
from little_brother.event_handler import EventHandler
from little_brother.master_connector import MasterConnectorConfigModel, MasterConnector
from little_brother.test.web.base_test_status_server import BaseTestStatusServer


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
        outgoing_events = [ event ]

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


if __name__ == "__main__":
    unittest.main()
