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
import unittest

import little_brother.client_info as client_info
from little_brother.client_stats import ClientStats
from python_base_app import tools
from python_base_app.test import base_test

HOSTNAME = "hostname"
USERNAME = "username"
CLIENT_NAME = "clientname"
MAXIMUM_PING_INTERVAL = 123
MASTER_VERSION = "1.2.3"
OLD_CLIENT_VERSION = "1.2.2"
PID = 123
TIME_DELTA = 12 * 3600 + 34 * 60 + 56


class TestClientInfo(base_test.BaseTestCase):

    def test_constructor(self):

        ci = client_info.ClientInfo(p_is_master=True, p_host_name=HOSTNAME, p_client_stats=None,
                                    p_maximum_client_ping_interval=MAXIMUM_PING_INTERVAL,
                                    p_master_version=MASTER_VERSION)

        self.assertTrue(ci.is_master)
        self.assertIsNone(ci.client_stats)
        self.assertEqual(ci.host_name, HOSTNAME)
        self.assertEqual(ci.maximum_client_ping_interval, MAXIMUM_PING_INTERVAL)
        self.assertEqual(ci.master_version, MASTER_VERSION)

    def test_property_node_type(self):

        ci = client_info.ClientInfo(p_is_master=True, p_host_name=HOSTNAME, p_client_stats=None)

        self.assertEqual(ci.node_type, "Master")

        ci = client_info.ClientInfo(p_is_master=False, p_host_name=HOSTNAME, p_client_stats=None)

        self.assertEqual(ci.node_type, "Slave")

    def test_property_seconds_without_ping(self):

        ci = client_info.ClientInfo(p_is_master=True, p_host_name=HOSTNAME, p_client_stats=None)

        self.assertIsNone(ci.seconds_without_ping)

        ci.last_message = tools.get_current_time()

        self.assertLessEqual(ci.seconds_without_ping, 0.01)

        ci.last_message = tools.get_current_time() + datetime.timedelta(seconds=-TIME_DELTA)

        self.assertAlmostEqual(ci.seconds_without_ping, TIME_DELTA, delta=0.01)

    def test_property_last_message_string(self):

        ci = client_info.ClientInfo(p_is_master=True, p_host_name=HOSTNAME, p_client_stats=None)

        self.assertEqual(ci.last_message_string, "n/a")

        ci.last_message = tools.get_current_time() + datetime.timedelta(seconds=-TIME_DELTA)

        message_string = ci.last_message_string

        self.assertIn(message_string, ["12h34m56s", "12h34m57s"])

    def test_property_last_message_class(self):

        ci = client_info.ClientInfo(p_is_master=True, p_host_name=HOSTNAME, p_client_stats=None,
                                    p_maximum_client_ping_interval=MAXIMUM_PING_INTERVAL)

        self.assertEqual(ci.last_message_class, "")

        ci.last_message = tools.get_current_time() + datetime.timedelta(seconds=-(MAXIMUM_PING_INTERVAL + 1))

        self.assertEqual(ci.last_message_class, client_info.CSS_CLASS_MAXIMUM_PING_EXCEEDED)

        ci.last_message = tools.get_current_time() + datetime.timedelta(seconds=-(MAXIMUM_PING_INTERVAL - 1))

        self.assertEqual(ci.last_message_class, "")


    def test_property_version_string(self):

        ci = client_info.ClientInfo(p_is_master=True, p_host_name=HOSTNAME, p_client_stats=None)

        self.assertEqual(ci.version_string, "<" + client_info.MINIMUM_VERSION_WITH_CLIENT_STAT_SUPPORT)

        ci.client_stats = ClientStats(p_version=MASTER_VERSION)

        self.assertEqual(ci.version_string, MASTER_VERSION)

    def test_property_version_class(self):

        ci = client_info.ClientInfo(p_is_master=True, p_host_name=HOSTNAME, p_client_stats=None,
                                    p_master_version=MASTER_VERSION)

        self.assertEqual(ci.version_class, client_info.CSS_CLASS_SLAVE_VERSION_OUTDATED)

        ci.client_stats = ClientStats(p_version=MASTER_VERSION)

        self.assertEqual(ci.version_class, "")

        ci.client_stats = ClientStats(p_version=OLD_CLIENT_VERSION)

        self.assertEqual(ci.version_class, client_info.CSS_CLASS_SLAVE_VERSION_OUTDATED)

if __name__ == "__main__":
    unittest.main()
