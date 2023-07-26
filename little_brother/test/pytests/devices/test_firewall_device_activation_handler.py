# -*- coding: utf-8 -*-

#    Copyright (C) 2021-2022  Marcus Rickert
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

import pytest
from mockito import patch

from little_brother import dependency_injection
from little_brother.devices.firewall_device_activation_handler import FirewallDeviceActivationHandler
from little_brother.devices.firewall_handler import FirewallHandler
from little_brother.devices.firewall_handler_config_model import FirewallHandlerConfigModel
from little_brother.persistence.persistence import Persistence
from little_brother.persistence.persistent_device import Device
from little_brother.persistence.session_context import SessionContext
from little_brother.test.persistence.test_persistence import TestPersistence
from python_base_app import log_handling, tools

DEFAULT_TARGET_IP = "8.8.8.8"
DEFAULT_HOSTNAME = "localhost"


class CallResult:

    def __init__(self):
        self.ip_address = None
        self.usage_permitted = None
        self.blocked_ip_addresses = []

    def set(self, p_ip_address, p_blocked_ip_addresses, p_usage_permitted):
        self.ip_address = p_ip_address
        self.blocked_ip_addresses = p_blocked_ip_addresses
        self.usage_permitted = p_usage_permitted


@pytest.fixture
def default_firewall_handler_config():
    config = FirewallHandlerConfigModel()
    config.target_ip = [DEFAULT_TARGET_IP]
    return config


@pytest.fixture
def default_firewall_handler(default_firewall_handler_config):
    handler = FirewallHandler(p_config=default_firewall_handler_config)
    dependency_injection.container[FirewallHandler] = handler
    return handler


@pytest.fixture
def patched_firewall_handler_test_result(default_firewall_handler_config):
    handler = FirewallHandler(p_config=default_firewall_handler_config)
    test_result = CallResult()
    with patch(handler.set_usage_permission_for_ip,
               lambda p_ip_address, p_blocked_ip_addresses, p_usage_permitted:
               test_result.set(p_ip_address=p_ip_address,
                               p_blocked_ip_addresses=p_blocked_ip_addresses,
                               p_usage_permitted=p_usage_permitted)):
        dependency_injection.container[FirewallHandler] = handler
        yield test_result


@pytest.fixture
def logger():
    return log_handling.get_logger("pytest-executor")


def setup_function():
    dependency_injection.reset()


@pytest.fixture
def dummy_persistence(logger):
    TestPersistence.create_dummy_persistence(p_logger=logger, p_delete=True)
    return dependency_injection.container[Persistence]


def test_create_firewall_device_activation_handler(default_firewall_handler):
    handler = FirewallDeviceActivationHandler()
    assert handler is not None
    assert handler.firewall_handler == default_firewall_handler


def test_create_firewall_device_activation_handler_set_usage_permission_for_ip(
        patched_firewall_handler_test_result, dummy_persistence):
    with SessionContext(p_persistence=dummy_persistence) as session_context:
        handler = FirewallDeviceActivationHandler()
        assert handler is not None
        device = Device()
        device.populate_test_data(p_session_context=session_context)
        device.hostname = DEFAULT_HOSTNAME
        session = session_context.get_session()
        session.add(device)
        session.commit()

        handler.set_usage_permission_for_device(p_device=device, p_usage_permitted=False)

        assert patched_firewall_handler_test_result.ip_address == tools.get_ip_address_by_dns_name(
            p_dns_name=DEFAULT_HOSTNAME)
        assert not patched_firewall_handler_test_result.usage_permitted

        device.hostname = tools.get_ip_address_by_dns_name(p_dns_name=DEFAULT_HOSTNAME)
        session.commit()

        handler.set_usage_permission_for_device(p_device=device, p_usage_permitted=True)

        assert patched_firewall_handler_test_result.ip_address == device.hostname
        assert patched_firewall_handler_test_result.usage_permitted
