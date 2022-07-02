# -*- coding: utf-8 -*-

#    Copyright (C) 2019-2022  Marcus Rickert
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

from little_brother import dependency_injection
from little_brother.persistence.persistence import Persistence
from little_brother.persistence.persistent_device import Device
from little_brother.persistence.persistent_device_entity_manager import DeviceEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.test.persistence import test_persistence
from python_base_app import tools
from python_base_app.test import base_test

SPECIFIC_DNS_NAME = "welt.de"
SPECIFIC_DNS_NAMES = [ "welt.de", "ikea.de" ]
SPECIFIC_DNS_NAMES_STRING = "\n".join(SPECIFIC_DNS_NAMES)

class TestDevice(base_test.BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        dependency_injection.reset()

    def test_list_of_ip_addresses(self):

        test_persistence.TestPersistence.create_dummy_persistence(self._logger)
        dummy_persistence = dependency_injection.container[Persistence]

        with SessionContext(p_persistence=dummy_persistence) as session_context:
            device = Device()
            device.populate_test_data(p_session_context=session_context)
            device.blocked_urls = SPECIFIC_DNS_NAMES_STRING
            session = session_context.get_session()
            session.add(device)
            session.commit()
            new_id = device.id

        with SessionContext(p_persistence=dummy_persistence) as session_context:
            entity_manager = DeviceEntityManager()
            saved_entity : Device = entity_manager.get_by_id(p_session_context=session_context, p_id=new_id)
            self.assertIsNotNone(saved_entity)

            ip_addresses = saved_entity.list_of_blocked_ip_addresses

            for dns_name in SPECIFIC_DNS_NAMES:
                ip_address = tools.get_ip_address_by_dns_name(dns_name)
                self.assertIn(ip_address, ip_addresses)


    def test_ip_address(self):

        test_persistence.TestPersistence.create_dummy_persistence(self._logger)
        dummy_persistence = dependency_injection.container[Persistence]

        with SessionContext(p_persistence=dummy_persistence) as session_context:
            device = Device()
            device.populate_test_data(p_session_context=session_context)
            device.hostname = SPECIFIC_DNS_NAME
            session = session_context.get_session()
            session.add(device)
            session.commit()
            new_id = device.id

        with SessionContext(p_persistence=dummy_persistence) as session_context:
            entity_manager = DeviceEntityManager()
            saved_entity : Device = entity_manager.get_by_id(p_session_context=session_context, p_id=new_id)
            self.assertIsNotNone(saved_entity)

            self.assertEqual(tools.get_ip_address_by_dns_name(SPECIFIC_DNS_NAME), saved_entity.ip_address)
