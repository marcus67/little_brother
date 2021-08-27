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

import unittest

from little_brother.admin_event import AdminEvent
from little_brother.api.master_connector import MasterConnector, MasterConnectorConfigModel
from little_brother.client_stats import ClientStats
from python_base_app.test import base_test

HOSTNAME = "some.host"


class TestMasterConnector(base_test.BaseTestCase):

    def test_constructor(self):

        config = MasterConnectorConfigModel()
        connector = MasterConnector(p_config=config)
        self.assertIsNotNone(connector)

    def test_encode_and_decode(self):

        config = MasterConnectorConfigModel()
        config.access_token = "token123"

        connector = MasterConnector(p_config=config)
        self.assertIsNotNone(connector)

        events = [ AdminEvent() ]
        client_stats = [ ClientStats() ]

        message = connector.encode_event(p_hostname=HOSTNAME, p_events=events, p_client_stats=client_stats)
        received_message = connector.receive_events(message)

        self.assertIsNotNone(received_message)
        self.assertEqual(3, len(received_message))

        hostname, json_events, json_slave_stats = received_message

        self.assertEqual(HOSTNAME, hostname)
        self.assertEqual(1, len(json_events))
        self.assertEqual(1, len(json_slave_stats))


if __name__ == "__main__":
    unittest.main()
