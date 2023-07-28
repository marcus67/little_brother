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
import time

import pytest

from little_brother.devices.firewall_entry import key, FirewallEntry
from little_brother.devices.firewall_handler import FirewallHandler
from little_brother.devices.firewall_handler_config_model import FirewallHandlerConfigModel, \
    DEFAULT_IPTABLES_ADD_FORWARD_COMMAND_PATTERN, DEFAULT_IPTABLES_REMOVE_FORWARD_COMMAND_PATTERN, \
    DEFAULT_IPTABLES_LIST_FORWARD_COMMAND
from python_base_app.configuration import ConfigurationException

DEFAULT_SOURCE_IP = "192.1.0.254"
DEFAULT_SOURCE_IP_2 = "192.1.0.253"
DEFAULT_TARGET_IP = "8.8.8.8"


@pytest.fixture
def default_firewall_handler_config():
    config = FirewallHandlerConfigModel()
    config.target_ip = [DEFAULT_TARGET_IP]
    return config


def test_create_firewall_handler(default_firewall_handler_config):
    handler = FirewallHandler(default_firewall_handler_config)
    assert handler is not None
    assert handler._config.target_ip is not None
    assert len(handler._config.target_ip) == 1
    assert handler._config.target_ip[0] == DEFAULT_TARGET_IP


@pytest.mark.skipif(os.getenv("NO_IPTABLES"), reason="no iptables allowed")
def test_iptables_read_table(default_firewall_handler_config):
    handler = FirewallHandler(default_firewall_handler_config)
    assert handler is not None

    handler.read_forward_entries()
    assert handler._entries is not None

    entry_key = key(p_source=DEFAULT_SOURCE_IP, p_destination=DEFAULT_TARGET_IP)
    assert entry_key not in handler._entries


@pytest.mark.skipif(os.getenv("NO_IPTABLES"), reason="no iptables allowed")
def test_iptables_insert_and_delete_entry(default_firewall_handler_config):
    handler: FirewallHandler = FirewallHandler(default_firewall_handler_config)
    assert handler is not None

    handler.read_forward_entries()
    assert handler._entries is not None

    entries = handler._entries

    number_of_entries = len(entries)

    forward_entries = handler.get_active_forward_entries(p_ip_address=DEFAULT_SOURCE_IP)

    try:
        entry_key = key(p_source=DEFAULT_SOURCE_IP, p_destination=DEFAULT_TARGET_IP)
        assert entry_key not in forward_entries

        handler.set_usage_permission_for_ip(p_ip_address=DEFAULT_SOURCE_IP, p_blocked_ip_addresses=[],
                                            p_usage_permitted=False)
        forward_entries = handler.get_active_forward_entries(p_ip_address=DEFAULT_SOURCE_IP)
        assert entry_key in forward_entries

        assert len(entries) == number_of_entries + 1

        handler.set_usage_permission_for_ip(p_ip_address=DEFAULT_SOURCE_IP_2, p_blocked_ip_addresses=[],
                                            p_usage_permitted=False)
        assert entry_key in forward_entries
        assert len(entries) == number_of_entries + 2

        entry_key_2 = key(p_source=DEFAULT_SOURCE_IP_2, p_destination=DEFAULT_TARGET_IP)
        forward_entries = handler.get_active_forward_entries(p_ip_address=DEFAULT_SOURCE_IP)
        forward_entries_2 = handler.get_active_forward_entries(p_ip_address=DEFAULT_SOURCE_IP_2)
        assert entry_key in forward_entries
        assert entry_key_2 in forward_entries_2

        handler.set_usage_permission_for_ip(p_ip_address=DEFAULT_SOURCE_IP, p_blocked_ip_addresses=[],
                                            p_usage_permitted=True)
        forward_entries = handler.get_active_forward_entries(p_ip_address=DEFAULT_SOURCE_IP)
        forward_entries_2 = handler.get_active_forward_entries(p_ip_address=DEFAULT_SOURCE_IP_2)
        assert entry_key not in forward_entries
        assert entry_key_2 in forward_entries_2
        assert len(entries) == number_of_entries + 1

        handler.set_usage_permission_for_ip(p_ip_address=DEFAULT_SOURCE_IP_2, p_blocked_ip_addresses=[],
                                            p_usage_permitted=True)
        forward_entries = handler.get_active_forward_entries(p_ip_address=DEFAULT_SOURCE_IP)
        forward_entries_2 = handler.get_active_forward_entries(p_ip_address=DEFAULT_SOURCE_IP_2)
        assert entry_key not in forward_entries
        assert entry_key_2 not in forward_entries_2
        assert len(entries) == number_of_entries

    finally:
        handler.set_usage_permission_for_ip(p_ip_address=DEFAULT_SOURCE_IP, p_blocked_ip_addresses=[],
                                            p_usage_permitted=True)
        handler.set_usage_permission_for_ip(p_ip_address=DEFAULT_SOURCE_IP_2, p_blocked_ip_addresses=[],
                                            p_usage_permitted=True)


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


@pytest.mark.skipif(os.getenv("NO_IPTABLES"), reason="no iptables allowed")
def test_iptables_remove_entry_invalid_binary(default_firewall_handler_config):
    handler = FirewallHandler(default_firewall_handler_config)
    assert handler is not None

    handler.read_forward_entries()
    old_pattern = handler._config.iptables_remove_forward_command_pattern

    try:
        handler.set_usage_permission_for_ip(p_ip_address=DEFAULT_SOURCE_IP, p_blocked_ip_addresses=[],
                                            p_usage_permitted=False)

        handler._config.iptables_remove_forward_command_pattern = "x" + DEFAULT_IPTABLES_REMOVE_FORWARD_COMMAND_PATTERN

        with pytest.raises(ConfigurationException) as e:
            handler.set_usage_permission_for_ip(p_ip_address=DEFAULT_SOURCE_IP, p_blocked_ip_addresses=[],
                                                p_usage_permitted=True)

        assert "returns exit code" in str(e)

    finally:
        handler._config.iptables_remove_forward_command_pattern = old_pattern
        handler.set_usage_permission_for_ip(p_ip_address=DEFAULT_SOURCE_IP, p_blocked_ip_addresses=[],
                                            p_usage_permitted=True)


@pytest.mark.skipif(os.getenv("NO_IPTABLES"), reason="no iptables allowed")
def test_iptables_list_entries_invalid_binary(default_firewall_handler_config):
    handler = FirewallHandler(default_firewall_handler_config)
    assert handler is not None

    handler._config.iptables_list_forward_command = "x" + DEFAULT_IPTABLES_LIST_FORWARD_COMMAND

    with pytest.raises(ConfigurationException) as e:
        handler.read_forward_entries()

    assert "returns exit code" in str(e)


@pytest.mark.skipif(os.getenv("NO_IPTABLES"), reason="no iptables allowed")
def test_iptables_list_entries_with_cache_timeout(default_firewall_handler_config):
    default_firewall_handler_config.cache_ttl = 1
    handler = FirewallHandler(default_firewall_handler_config)
    assert handler is not None

    entries = handler.entries

    assert id(entries) == id(handler.entries)

    entries.append(FirewallEntry())

    assert id(entries) == id(handler.entries)

    time.sleep(default_firewall_handler_config.cache_ttl + 1)

    assert id(entries) != id(handler.entries)
