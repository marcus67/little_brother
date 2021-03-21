# -*- coding: utf-8 -*-

# Copyright (C) 2019  Marcus Rickert
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

import collections
import re

from python_base_app import configuration
from python_base_app import tools


DEFAULT_SERVER_GROUP = "default-group"
LOGIN_MAPPING_SECTION_PREFIX = "LoginMapping"

LoginUidMappingEntry = collections.namedtuple('LoginUidMappingEntry', ['login', 'uid'])

MAPPING_ENTRY_PATTERN = re.compile("^ *([-a-z0-9]+) *: *([0-9]+) *$")

class LoginMappingSectionHandler(configuration.ConfigurationSectionHandler):

    def __init__(self):

        super().__init__(p_section_prefix=LOGIN_MAPPING_SECTION_PREFIX)
        self._login_mapping_sections = {}

    def handle_section(self, p_section_name):

        login_mapping_section = LoginMappingSection(p_section_name=p_section_name)
        self.scan(p_section=login_mapping_section)

        tools.check_config_value(p_config=login_mapping_section, p_config_attribute_name="server_group")

        self._login_mapping_sections[login_mapping_section.server_group] = login_mapping_section

        mappings = ", ".join(login_mapping_section.mapping_entries)
        msg = "Found login mapping for server group '{server_group}': {mappings}"
        self._logger.info(msg.format(server_group=login_mapping_section.server_group, mappings=mappings))



class LoginMappingSection(configuration.ConfigModel):

    def __init__(self, p_section_name=None):

        super().__init__(p_section_name=p_section_name)

        self.server_group = configuration.NONE_STRING
        self.mapping_entries = [ configuration.NONE_STRING ]

class LoginMapping(object):

    def __init__(self, p_default_server_group=DEFAULT_SERVER_GROUP):

        self._default_server_group = p_default_server_group
        self._login2uid_mappings = {}
        self._uid2login_mappings = {}

    def to_json(self):

        json = [ (server_group,
                  [ (entry.login, entry.uid) for entry in mapping.values()])
                 for (server_group, mapping) in self._login2uid_mappings.items() ]
        return json

    def from_json(self, p_json):

        for (server_group, mapping) in p_json:
            for (login, uid) in mapping:
                entry = LoginUidMappingEntry(login, uid)
                self.add_entry(p_login_uid_mapping_entry=entry, p_server_group=server_group)

    def get_server_group_names(self):
        return self._login2uid_mappings.keys()


    def add_entry(self, p_login_uid_mapping_entry:LoginUidMappingEntry, p_server_group:str=DEFAULT_SERVER_GROUP):

        login2uid_mapping = self._login2uid_mappings.get(p_server_group)

        if login2uid_mapping is None:
            login2uid_mapping = {}
            self._login2uid_mappings[p_server_group] = login2uid_mapping

        login2uid_mapping[p_login_uid_mapping_entry.login] = p_login_uid_mapping_entry

        uid2login_mapping = self._uid2login_mappings.get(p_server_group)

        if uid2login_mapping is None:
            uid2login_mapping = {}
            self._uid2login_mappings[p_server_group] = uid2login_mapping

        uid2login_mapping[p_login_uid_mapping_entry.uid] = p_login_uid_mapping_entry

    def get_login_by_uid(self, p_uid:int, p_server_group:str=DEFAULT_SERVER_GROUP):

        uid2login_mapping = self._uid2login_mappings.get(p_server_group)

        if uid2login_mapping is None:
            uid2login_mapping = self._uid2login_mappings.get(self._default_server_group)

        if uid2login_mapping is None:
            return None

        entry = uid2login_mapping.get(p_uid)

        if entry is None:
            return None

        return entry.login

    def get_uid_by_login(self, p_login, p_server_group=DEFAULT_SERVER_GROUP):

        login2uid_mapping = self._login2uid_mappings.get(p_server_group)

        if login2uid_mapping is None:
            login2uid_mapping = self._login2uid_mappings.get(self._default_server_group)

        if login2uid_mapping is None:
            return None

        entry = login2uid_mapping.get(p_login)

        if entry is None:
            return None

        return entry.uid

    def read_from_configuration(self, p_login_mapping_section_handler:LoginMappingSectionHandler):

        for section in p_login_mapping_section_handler._login_mapping_sections.values():
            for mapping_entry in section.mapping_entries:
                single_entries = mapping_entry.split(",")

                for entry in single_entries:
                    match = MAPPING_ENTRY_PATTERN.match(entry)

                    if match is None:
                        msg = "Invalid logging mapping '{entry}' for host group {group}"
                        raise configuration.ConfigurationException(msg.format(entry=entry, group=section.server_group))

                    login_uid_mapping_entry = LoginUidMappingEntry(match.group(1), int(match.group(2)))
                    self.add_entry(p_server_group=section.server_group,
                                   p_login_uid_mapping_entry=login_uid_mapping_entry)
