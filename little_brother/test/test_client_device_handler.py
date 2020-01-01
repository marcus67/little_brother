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

from little_brother import client_device_handler
from little_brother.test import test_data
from python_base_app.test import base_test


class TestClientDeviceHandler(base_test.BaseTestCase):

    def check_list_has_n_elements(self, p_list, p_n):
        self.assertIsNotNone(p_list)
        self.assertIsInstance(p_list, list)
        self.assertEqual(len(p_list), p_n)

    @base_test.skip_if_env("NO_PING")
    def test_existing_host(self):
        config = client_device_handler.ClientDeviceHandlerConfigModel()

        device_config = client_device_handler.ClientDeviceConfigModel(p_section_name="my_device")
        device_config.username = test_data.USER_1
        device_config.hostname = "localhost"
        device_config.min_activity_duration = 0

        device_configs = {device_config.section_name: device_config}

        process_handler = client_device_handler.ClientDeviceHandler(p_config=config,
                                                                    p_client_device_configs=device_configs)

        process_handler.scan_processes(p_server_group=None,
                                       p_login_mapping=None,
                                       p_host_name=None,
                                       p_process_regex_map=None,
                                       p_reference_time=datetime.datetime.now())

        events = process_handler.scan_processes(p_server_group=None,
                                                p_login_mapping=None,
                                                p_host_name=None,
                                                p_process_regex_map=None,
                                                p_reference_time=datetime.datetime.now())

        self.check_list_has_n_elements(p_list=events, p_n=1)

    def test_nonexisting_host(self):
        config = client_device_handler.ClientDeviceHandlerConfigModel()

        device_config = client_device_handler.ClientDeviceConfigModel(p_section_name="my_device")
        device_config.username = test_data.USER_1
        device_config.hostname = "localhostx"
        device_config.min_activity_duration = 0

        device_configs = {device_config.section_name: device_config}

        process_handler = client_device_handler.ClientDeviceHandler(p_config=config,
                                                                    p_client_device_configs=device_configs)

        process_handler.scan_processes(p_server_group=None,
                                       p_login_mapping=None,
                                       p_host_name=None,
                                       p_process_regex_map=None,
                                       p_reference_time=datetime.datetime.now())

        events = process_handler.scan_processes(p_server_group=None,
                                                p_login_mapping=None,
                                                p_host_name=None,
                                                p_process_regex_map=None,
                                                p_reference_time=datetime.datetime.now())

        self.check_list_has_n_elements(p_list=events, p_n=0)
