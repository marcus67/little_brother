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

import datetime
import re
import shlex
import subprocess
from typing import Optional

from little_brother.devices.firewall_entry import FirewallEntry, key
from little_brother.devices.firewall_handler_config_model import FirewallHandlerConfigModel, DEFAULT_PROTOCOL, \
    DEFAULT_TARGET, DEFAULT_COMMENT
from python_base_app import log_handling, tools
from python_base_app.configuration import ConfigurationException


class FirewallHandler:

    def __init__(self, p_config: FirewallHandlerConfigModel):
        self._logger = log_handling.get_logger(self.__class__.__name__)

        self._config: FirewallHandlerConfigModel = p_config
        self._entries: Optional[list[FirewallEntry]] = None
        self._last_table_scan: Optional[datetime.datetime] = None

    @property
    def entries(self) -> Optional[list[FirewallEntry]]:
        self.read_forward_entries()
        return self._entries

    def get_active_forward_entries(self, p_ip_address) -> dict[str, FirewallEntry]:

        source = tools.get_ip_address_by_dns_name(p_dns_name=p_ip_address)

        return {entry.key(): entry for entry in self.entries
                if (entry.protocol == DEFAULT_PROTOCOL and
                    entry.source == source and
                    entry.target == DEFAULT_TARGET)}

    def add_entry_to_cache(self, p_new_entry: FirewallEntry):

        for entry in self.entries:
            entry.index += 1

        self.entries.insert(0, p_new_entry)

    def remove_entry_from_cache(self, p_entry: FirewallEntry):

        self.entries.remove(p_entry)

        for entry in self._entries:
            if entry.index > p_entry.index:
                entry.index -= 1

    def remove_entry(self, p_entry):

        self._logger.info(f"Removing iptables entry for blocking {p_entry.source} -> {p_entry.destination}...")

        iptables_command = self._config.iptables_remove_forward_command_pattern.format(index=p_entry.index)
        command = shlex.split(self._config.sudo_command + " " + iptables_command)

        self._logger.debug(f"Executing command {command} in subprocess")
        proc = subprocess.run(command, stdout=subprocess.PIPE)

        if proc.returncode >= 1:
            raise ConfigurationException(f"{command} returns exit code {proc.returncode}")

        self.remove_entry_from_cache(p_entry=p_entry)

    def remove_entries(self, p_forward_entries: dict[str, FirewallEntry]):
        for entry in p_forward_entries.values():
            self.remove_entry(p_entry=entry)

    def add_missing_entry(self, p_ip_address: str, p_target_ip: str, p_comment:str):

        self._logger.info(f"Adding iptables entry for blocking {p_ip_address} -> {p_target_ip}...")

        iptables_command = self._config.iptables_add_forward_command_pattern.format(
            source_ip=p_ip_address,
            destination_ip=p_target_ip,
            comment=p_comment
        )

        # Remove the specification of the default route (= "any IP address") from the command since this is not an
        # allowed ip address! However, iptables will list the default route as such so we will use the string "0.0.0.0"
        # everywhere else.
        iptables_command = iptables_command.replace("-d 0.0.0.0", "")

        command = shlex.split(self._config.sudo_command + " " + iptables_command)

        self._logger.debug(f"Executing command {command} in subprocess")
        proc = subprocess.run(command, stdout=subprocess.PIPE)

        if proc.returncode >= 1:
            raise ConfigurationException(f"{command} returns exit code {proc.returncode}")

        new_entry = FirewallEntry()
        new_entry.index = 1
        new_entry.source = p_ip_address
        new_entry.destination = p_target_ip
        new_entry.target = DEFAULT_TARGET
        new_entry.protocol = DEFAULT_PROTOCOL
        new_entry.comment = p_comment

        self.add_entry_to_cache(new_entry)

    def update_active_entries(self, p_ip_address: str, p_blocked_ip_addresses: list[str],
                              p_forward_entries: dict[str, FirewallEntry], p_comment:str):

        # Use the devices blocked ip addresses if they defined else use the globally defined addresses
        effective_list_of_ip_addresses = self._config.target_ip \
            if len(p_blocked_ip_addresses) == 0 else p_blocked_ip_addresses

        for target_ip in effective_list_of_ip_addresses:
            entry_key = key(p_source=p_ip_address, p_destination=target_ip)

            if entry_key not in p_forward_entries:
                self.add_missing_entry(p_ip_address=p_ip_address, p_target_ip=target_ip, p_comment=p_comment)

        for forward_entry in p_forward_entries.values():
            if forward_entry.destination not in p_blocked_ip_addresses:
                self.remove_entry(p_entry=forward_entry)


    def set_usage_permission_for_ip(self, p_ip_address: str, p_blocked_ip_addresses: list[str],
                                    p_usage_permitted: bool):

        self.read_forward_entries()

        forward_entries = self.get_active_forward_entries(p_ip_address=p_ip_address)

        if p_usage_permitted and len(forward_entries) > 0:
            self.remove_entries(p_forward_entries=forward_entries)

        elif not p_usage_permitted:
            self.update_active_entries(p_ip_address=p_ip_address, p_blocked_ip_addresses=p_blocked_ip_addresses,
                                       p_forward_entries=forward_entries, p_comment=DEFAULT_COMMENT)

    def read_forward_entries(self):

        if self._entries is not None and self._last_table_scan is not None:
            if datetime.datetime.now() < self._last_table_scan + datetime.timedelta(seconds=self._config.cache_ttl):
                return

            self._logger.debug("Clearing iptables cache.")
            self._entries = []

        command = shlex.split(self._config.sudo_command + " " + self._config.iptables_list_forward_command)

        self._logger.debug(f"Executing command {command} in subprocess")
        proc = subprocess.run(command, stdout=subprocess.PIPE)

        if proc.returncode >= 1:
            raise ConfigurationException(f"{command} returns exit code {proc.returncode}")

        stdout_string = proc.stdout.decode("UTF-8")

        line_regex = re.compile(self._config.iptables_list_forward_entry_pattern)

        self._entries = []

        for line in stdout_string.split("\n"):
            self._logger.debug(f"iptables output: {line}")

            result = line_regex.match(line)

            if result:
                entry = FirewallEntry()
                entry.index = int(result.group(self._config.iptables_list_forward_entry_pattern_index_group))
                entry.target = result.group(self._config.iptables_list_forward_entry_pattern_target_group)
                entry.protocol = result.group(self._config.iptables_list_forward_entry_pattern_protocol_group)
                entry.option = result.group(self._config.iptables_list_forward_entry_pattern_option_group)
                entry.source = result.group(self._config.iptables_list_forward_entry_pattern_source_group)
                entry.destination = \
                    result.group(self._config.iptables_list_forward_entry_pattern_destination_group)
                entry.comment = \
                    result.group(self._config.iptables_list_forward_entry_pattern_comment_group)
                self._entries.append(entry)

        self._last_table_scan = datetime.datetime.now()
