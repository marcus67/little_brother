# -*- coding: utf-8 -*-

# Copyright (C) 2019-2022  Marcus Rickert
#
# See https://github.com/marcus67/little_brother
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from typing import Optional

from python_base_app import configuration

SECTION_NAME = "FirewallHandler"

DEFAULT_SUDO_COMMAND = "/usr/bin/sudo"
DEFAULT_CHAIN = "FORWARD"
DEFAULT_TARGET = "DROP"
DEFAULT_PROTOCOL = "all"

DEFAULT_IPTABLES_LIST_FORWARD_COMMAND = "/usr/sbin/iptables -n --line-numbers  -L " + DEFAULT_CHAIN
DEFAULT_IPTABLES_ADD_FORWARD_COMMAND_PATTERN = "iptables -I " + DEFAULT_CHAIN + " -p " + DEFAULT_PROTOCOL + " -j " + DEFAULT_TARGET + " -s {source_ip} -d {destination_ip}"
DEFAULT_IPTABLES_REMOVE_FORWARD_COMMAND_PATTERN = "iptables -D " + DEFAULT_CHAIN + " {index}"
DEFAULT_IPTABLES_LIST_FORWARD_ENTRY_PATTERN = \
    r"^([0-9]+)\s+(\w+)\s+(\w+)\s+(\S+)\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/[0-9]+\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/[0-9]+.*?"
DEFAULT_IPTABLES_LIST_FORWARD_ENTRY_PATTERN_INDEX_GROUP = 1
DEFAULT_IPTABLES_LIST_FORWARD_ENTRY_PATTERN_TARGET_GROUP = 2
DEFAULT_IPTABLES_LIST_FORWARD_ENTRY_PATTERN_PROTOCOL_GROUP = 3
DEFAULT_IPTABLES_LIST_FORWARD_ENTRY_PATTERN_OPTION_GROUP = 4
DEFAULT_IPTABLES_LIST_FORWARD_ENTRY_PATTERN_SOURCE_GROUP = 5
DEFAULT_IPTABLES_LIST_FORWARD_ENTRY_PATTERN_DESTINATION_GROUP = 6


class FirewallHandlerConfigModel(configuration.ConfigModel):

    def __init__(self):
        super().__init__(p_section_name=SECTION_NAME)

        self.sudo_command = DEFAULT_SUDO_COMMAND

        self.target_ip: Optional[list[str]] = [configuration.NONE_STRING]

        self.iptables_list_forward_command: str = \
            DEFAULT_IPTABLES_LIST_FORWARD_COMMAND
        self.iptables_add_forward_command_pattern: str = \
            DEFAULT_IPTABLES_ADD_FORWARD_COMMAND_PATTERN
        self.iptables_remove_forward_command_pattern: str = \
            DEFAULT_IPTABLES_REMOVE_FORWARD_COMMAND_PATTERN

        self.iptables_list_forward_entry_pattern: str = \
            DEFAULT_IPTABLES_LIST_FORWARD_ENTRY_PATTERN
        self.iptables_list_forward_entry_pattern_index_group: int = \
            DEFAULT_IPTABLES_LIST_FORWARD_ENTRY_PATTERN_INDEX_GROUP
        self.iptables_list_forward_entry_pattern_target_group: int = \
            DEFAULT_IPTABLES_LIST_FORWARD_ENTRY_PATTERN_TARGET_GROUP
        self.iptables_list_forward_entry_pattern_protocol_group: int = \
            DEFAULT_IPTABLES_LIST_FORWARD_ENTRY_PATTERN_PROTOCOL_GROUP
        self.iptables_list_forward_entry_pattern_option_group: int = \
            DEFAULT_IPTABLES_LIST_FORWARD_ENTRY_PATTERN_OPTION_GROUP
        self.iptables_list_forward_entry_pattern_source_group: int = \
            DEFAULT_IPTABLES_LIST_FORWARD_ENTRY_PATTERN_SOURCE_GROUP
        self.iptables_list_forward_entry_pattern_destination_group: int = \
            DEFAULT_IPTABLES_LIST_FORWARD_ENTRY_PATTERN_DESTINATION_GROUP

    def is_active(self):
        return len(self.target_ip) > 0
