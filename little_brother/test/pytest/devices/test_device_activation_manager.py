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

import os

import pytest
from mockito import when

from little_brother import dependency_injection
from little_brother.app_control_config_model import AppControlConfigModel
from little_brother.devices.device_activation_manager import DeviceActivationManager
from little_brother.devices.device_activation_manager_config_model import DeviceActivationManagerConfigModel
from little_brother.devices.firewall_device_activation_handler import FirewallDeviceActivationHandler
from little_brother.devices.firewall_entry import key
from little_brother.devices.firewall_handler import FirewallHandler
from little_brother.devices.firewall_handler_config_model import FirewallHandlerConfigModel, \
    DEFAULT_IPTABLES_ADD_FORWARD_COMMAND_PATTERN, DEFAULT_COMMENT
from little_brother.login_mapping import LoginMapping
from little_brother.persistence.persistence import Persistence
from little_brother.persistence.persistent_device import Device
from little_brother.persistence.persistent_user import User
from little_brother.persistence.persistent_user_2_device import User2Device
from little_brother.persistence.session_context import SessionContext
from little_brother.test.persistence.test_persistence import TestPersistence
from little_brother.user_manager import UserManager
from little_brother.user_status import UserStatus
from python_base_app import log_handling, tools
from python_base_app.configuration import ConfigurationException

DEFAULT_SERVER_GROUP = "default-group"
DEFAULT_TARGET_IP = "0.0.0.0"
DEFAULT_SOURCE_IP = "192.1.0.254"

DEFAULT_SPECIFIC_TARGET_IPS = [ "1.2.3.4", "4.3.2.1" ]


@pytest.fixture
def default_device_activation_manager_config():
    config = DeviceActivationManagerConfigModel()
    return config


@pytest.fixture
def logger():
    return log_handling.get_logger("pytest-executor")


def setup_function():
    dependency_injection.reset()


@pytest.fixture
def dummy_persistence(logger):
    TestPersistence.create_dummy_persistence(p_logger=logger, p_delete=True)
    yield dependency_injection.container[Persistence]


@pytest.fixture
def user_manager_with_activity_forbidden() -> UserManager:
    app_control_config = AppControlConfigModel()
    login_mapping = LoginMapping()

    user_status = UserStatus()
    user_status.activity_allowed = False

    with when(UserManager).get_current_user_status(...).thenReturn(user_status):
        user_manager = UserManager(p_config=app_control_config, p_is_master=True, p_login_mapping=login_mapping,
                                   p_server_group=DEFAULT_SERVER_GROUP)
        dependency_injection.container[UserManager] = user_manager
        yield user_manager


@pytest.fixture
def user_manager_with_activity_permitted() -> UserManager:
    app_control_config = AppControlConfigModel()
    login_mapping = LoginMapping()

    user_status = UserStatus()
    user_status.activity_allowed = True

    with when(UserManager).get_current_user_status(...).thenReturn(user_status):
        user_manager = UserManager(p_config=app_control_config, p_is_master=True, p_login_mapping=login_mapping,
                                   p_server_group=DEFAULT_SERVER_GROUP)
        dependency_injection.container[UserManager] = user_manager
        yield user_manager


@pytest.fixture
def default_firewall_handler_config():
    config = FirewallHandlerConfigModel()
    config.target_ip = [DEFAULT_TARGET_IP]
    return config

@pytest.fixture
def firewall_handler_config_with_several_ips():
    config = FirewallHandlerConfigModel()
    config.target_ip = DEFAULT_SPECIFIC_TARGET_IPS
    return config


@pytest.fixture
def firewall_device_activation_handler(default_firewall_handler_config):
    handler = FirewallDeviceActivationHandler()
    firewall_handler = FirewallHandler(p_config=default_firewall_handler_config)
    dependency_injection.container[FirewallHandler] = firewall_handler
    return handler

@pytest.fixture
def firewall_device_activation_handler_with_several_ips(firewall_handler_config_with_several_ips):
    handler = FirewallDeviceActivationHandler()
    firewall_handler = FirewallHandler(p_config=firewall_handler_config_with_several_ips)
    dependency_injection.container[FirewallHandler] = firewall_handler
    return handler


def populate_user_and_device(p_session_context : SessionContext, p_blocked_urls : list[str]=None):
    session = p_session_context.get_session()
    user = User()
    session.add(user)
    user.populate_test_data(p_session_context=p_session_context)
    device = Device()
    session.add(device)
    device.populate_test_data(p_session_context=p_session_context)

    if p_blocked_urls is not None:
        device.blocked_urls = "\n".join(p_blocked_urls)

    device.hostname = "localhost"
    user2device = User2Device()
    session.add(user2device)
    user2device.user = user
    user2device.device = device
    user2device.active = True
    user2device.blockable = True
    session.commit()
    return device


def test_create_device_activation_manager(default_device_activation_manager_config):
    manager = DeviceActivationManager(p_config=default_device_activation_manager_config)
    assert manager is not None


def test_get_recurring_task_without_handlers(default_device_activation_manager_config):
    manager = DeviceActivationManager(p_config=default_device_activation_manager_config)

    task = manager.get_recurring_task()
    assert task is None


def test_get_recurring_task_with_handlers(default_device_activation_manager_config):
    manager = DeviceActivationManager(p_config=default_device_activation_manager_config)

    handler = FirewallDeviceActivationHandler()
    manager.add_handler(p_handler=handler)

    task = manager.get_recurring_task()
    assert task is not None
    assert "check_device_activation_status" in task.name
    assert task.interval == manager._config.check_interval


def test_user_manager(default_device_activation_manager_config, user_manager_with_activity_forbidden):
    manager = DeviceActivationManager(p_config=default_device_activation_manager_config)

    local_user_manager = manager.user_manager
    assert local_user_manager is not None
    assert user_manager_with_activity_forbidden == local_user_manager


@pytest.mark.skipif(os.getenv("NO_IPTABLES"), reason="no iptables allowed")
def test_set_usage_permission_status_for_device_with_activity_forbidden(dummy_persistence,
                                                                        user_manager_with_activity_forbidden,
                                                                        default_device_activation_manager_config,
                                                                        firewall_device_activation_handler):
    with SessionContext(p_persistence=dummy_persistence) as session_context:

        device = populate_user_and_device(p_session_context=session_context)

        manager = DeviceActivationManager(default_device_activation_manager_config)

        manager.add_handler(p_handler=firewall_device_activation_handler)
        handler = dependency_injection.container[FirewallHandler]

        try:

            forward_entries = handler.get_active_forward_entries(p_ip_address=device.hostname)

            entry_key = key(p_source=tools.get_ip_address_by_dns_name(device.hostname), p_destination=DEFAULT_TARGET_IP)
            assert entry_key not in forward_entries

            entries = handler.entries
            number_of_entries = len(entries)

            manager.check_device_activation_status()

            forward_entries = handler.get_active_forward_entries(p_ip_address=device.hostname)
            assert entry_key in forward_entries

            assert len(entries) == number_of_entries + 1

        finally:
            manager.shutdown()

@pytest.mark.skipif(os.getenv("NO_IPTABLES"), reason="no iptables allowed")
def test_set_usage_permission_status_for_device_with_activity_forbidden_check_comment(
        dummy_persistence,
        user_manager_with_activity_forbidden,
        default_device_activation_manager_config,
        firewall_device_activation_handler):
    with SessionContext(p_persistence=dummy_persistence) as session_context:

        device = populate_user_and_device(p_session_context=session_context)

        manager = DeviceActivationManager(default_device_activation_manager_config)

        manager.add_handler(p_handler=firewall_device_activation_handler)
        handler = dependency_injection.container[FirewallHandler]

        try:
            entry_key = key(p_source=tools.get_ip_address_by_dns_name(device.hostname), p_destination=DEFAULT_TARGET_IP)

            manager.check_device_activation_status()

            forward_entries = handler.get_active_forward_entries(p_ip_address=device.hostname)
            assert entry_key in forward_entries

            forward_entry = forward_entries.get(entry_key)

            assert DEFAULT_COMMENT in forward_entry.comment

        finally:
            manager.shutdown()

@pytest.mark.skipif(os.getenv("NO_IPTABLES"), reason="no iptables allowed")
def test_set_usage_permission_status_for_device_with_activity_forbidden_several_ip_addresses(
        dummy_persistence,
        user_manager_with_activity_forbidden,
        default_device_activation_manager_config,
        firewall_device_activation_handler_with_several_ips):
    with SessionContext(p_persistence=dummy_persistence) as session_context:

        device = populate_user_and_device(p_session_context=session_context)

        firewall_device_activation_handler.target_ip = DEFAULT_SPECIFIC_TARGET_IPS

        manager = DeviceActivationManager(default_device_activation_manager_config)

        manager.add_handler(p_handler=firewall_device_activation_handler_with_several_ips)
        handler = dependency_injection.container[FirewallHandler]

        try:

            forward_entries = handler.get_active_forward_entries(p_ip_address=device.hostname)

            for ip_address in DEFAULT_SPECIFIC_TARGET_IPS:
                entry_key = key(p_source=tools.get_ip_address_by_dns_name(device.hostname), p_destination=ip_address)
                assert entry_key not in forward_entries

            entries = handler.entries
            number_of_entries = len(entries)

            manager.check_device_activation_status()
            forward_entries = handler.get_active_forward_entries(p_ip_address=device.hostname)

            entry_key = key(p_source=tools.get_ip_address_by_dns_name(device.hostname), p_destination=DEFAULT_TARGET_IP)
            assert entry_key not in forward_entries

            for ip_address in DEFAULT_SPECIFIC_TARGET_IPS:
                entry_key = key(p_source=tools.get_ip_address_by_dns_name(device.hostname), p_destination=ip_address)
                assert entry_key in forward_entries

            assert len(entries) == number_of_entries + len(DEFAULT_SPECIFIC_TARGET_IPS)

        finally:
            manager.shutdown()

@pytest.mark.skipif(os.getenv("NO_IPTABLES"), reason="no iptables allowed")
def test_set_usage_permission_status_for_device_with_activity_forbidden_device_ip_addresses_override(
        dummy_persistence,
        user_manager_with_activity_forbidden,
        default_device_activation_manager_config,
        firewall_device_activation_handler):
    with SessionContext(p_persistence=dummy_persistence) as session_context:

        device = populate_user_and_device(p_session_context=session_context, p_blocked_urls=DEFAULT_SPECIFIC_TARGET_IPS)

        firewall_device_activation_handler.target_ip = DEFAULT_SPECIFIC_TARGET_IPS

        manager = DeviceActivationManager(default_device_activation_manager_config)

        manager.add_handler(p_handler=firewall_device_activation_handler)
        handler = dependency_injection.container[FirewallHandler]

        try:

            forward_entries = handler.get_active_forward_entries(p_ip_address=device.hostname)

            for ip_address in DEFAULT_SPECIFIC_TARGET_IPS:
                entry_key = key(p_source=tools.get_ip_address_by_dns_name(device.hostname), p_destination=ip_address)
                assert entry_key not in forward_entries

            entries = handler.entries
            number_of_entries = len(entries)

            manager.check_device_activation_status()
            forward_entries = handler.get_active_forward_entries(p_ip_address=device.hostname)

            entry_key = key(p_source=tools.get_ip_address_by_dns_name(device.hostname), p_destination=DEFAULT_TARGET_IP)
            assert entry_key not in forward_entries

            for ip_address in DEFAULT_SPECIFIC_TARGET_IPS:
                entry_key = key(p_source=tools.get_ip_address_by_dns_name(device.hostname), p_destination=ip_address)
                assert entry_key in forward_entries

            assert len(entries) == number_of_entries + len(DEFAULT_SPECIFIC_TARGET_IPS)

        finally:
            manager.shutdown()


@pytest.mark.skipif(os.getenv("NO_IPTABLES"), reason="no iptables allowed")
def test_set_usage_permission_status_for_device_with_activity_allowed(dummy_persistence,
                                                                      user_manager_with_activity_permitted,
                                                                      default_device_activation_manager_config,
                                                                      firewall_device_activation_handler):
    with SessionContext(p_persistence=dummy_persistence) as session_context:

        device = populate_user_and_device(p_session_context=session_context)

        manager = DeviceActivationManager(default_device_activation_manager_config)

        manager.add_handler(p_handler=firewall_device_activation_handler)
        handler = dependency_injection.container[FirewallHandler]

        try:

            forward_entries = handler.get_active_forward_entries(p_ip_address=device.hostname)

            entry_key = key(p_source=tools.get_ip_address_by_dns_name(device.hostname), p_destination=DEFAULT_TARGET_IP)
            assert entry_key not in forward_entries

            entries = handler.entries
            number_of_entries = len(entries)

            manager.check_device_activation_status()

            forward_entries = handler.get_active_forward_entries(p_ip_address=device.hostname)
            assert entry_key not in forward_entries

            assert len(entries) == number_of_entries

        finally:
            manager.shutdown()


@pytest.mark.skipif(os.getenv("NO_IPTABLES"), reason="no iptables allowed")
def test_set_usage_permission_status_for_device_invalid_binary(dummy_persistence,
                                                               user_manager_with_activity_forbidden,
                                                               default_device_activation_manager_config,
                                                               firewall_device_activation_handler):
    with SessionContext(p_persistence=dummy_persistence) as session_context:

        manager = DeviceActivationManager(default_device_activation_manager_config)

        populate_user_and_device(p_session_context=session_context)

        manager.add_handler(p_handler=firewall_device_activation_handler)
        handler = dependency_injection.container[FirewallHandler]
        handler._config.iptables_add_forward_command_pattern = "x" + DEFAULT_IPTABLES_ADD_FORWARD_COMMAND_PATTERN

        try:
            with pytest.raises(ConfigurationException) as e:
                manager.check_device_activation_status()

            assert "returns exit code" in str(e)

        finally:
            manager.shutdown()


@pytest.mark.skipif(os.getenv("NO_IPTABLES"), reason="no iptables allowed")
def test_iptables_insert_entry_invalid_binary(default_firewall_handler_config):
    handler = FirewallHandler(default_firewall_handler_config)
    assert handler is not None

    handler.read_forward_entries()

    try:
        handler._config.iptables_add_forward_command_pattern = "x" + DEFAULT_IPTABLES_ADD_FORWARD_COMMAND_PATTERN

        with pytest.raises(ConfigurationException) as e:
            handler.set_usage_permission_for_ip(p_ip_address=DEFAULT_SOURCE_IP, p_blocked_ip_addresses=[],
                                                p_usage_permitted=False)

        assert "returns exit code" in str(e)

    finally:
        handler.set_usage_permission_for_ip(p_ip_address=DEFAULT_SOURCE_IP, p_blocked_ip_addresses=[],
                                            p_usage_permitted=True)
