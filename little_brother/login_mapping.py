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

import re
from typing import Optional

from sqlalchemy.orm import Session

from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn
from little_brother.persistence.persistent_uid_mapping import DEFAULT_SERVER_GROUP, UidMapping
from little_brother.persistence.session_context import SessionContext
from python_base_app import configuration
from python_base_app import tools

LOGIN_MAPPING_SECTION_PREFIX = "LoginMapping"

# LoginUidMappingEntry = collections.namedtuple('LoginUidMappingEntry', ['login', 'uid'])

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
        msg = f"Found login mapping for server group '{login_mapping_section.server_group}': {mappings}"
        self._logger.info(msg)


class LoginMappingSection(configuration.ConfigModel):

    def __init__(self, p_section_name=None):
        super().__init__(p_section_name=p_section_name)

        self.server_group = configuration.NONE_STRING
        self.mapping_entries = [configuration.NONE_STRING]


class LoginMapping(PersistenceDependencyInjectionMixIn):

    def __init__(self, p_default_server_group=DEFAULT_SERVER_GROUP):

        super().__init__()

        self._default_server_group = p_default_server_group

    def get_uid_to_login_mapping(self, p_session_context: SessionContext,
                                 p_server_group: str = DEFAULT_SERVER_GROUP) -> dict[int, str]:

        uid_mappings = self.uid_mapping_entity_manager.get_by_server_group(p_session_context=p_session_context,
                                                                           p_server_group=p_server_group)
        return {entry.uid: entry.username for entry in uid_mappings}

    def get_login_to_uid_mapping(self, p_session_context: SessionContext,
                                 p_server_group: str = DEFAULT_SERVER_GROUP) -> dict[int, str]:

        uid_mappings = self.uid_mapping_entity_manager.get_by_server_group(p_session_context=p_session_context,
                                                                           p_server_group=p_server_group)
        return {entry.username: entry.uid for entry in uid_mappings}

    def to_json(self, p_session_context: SessionContext):

        server_groups = self.uid_mapping_entity_manager.get_server_groups(p_session_context=p_session_context)
        json = [(server_group,
                 [(entry.username, entry.uid) for entry in
                  self.uid_mapping_entity_manager.get_by_server_group(p_session_context=p_session_context,
                                                                      p_server_group=server_group)])
                for server_group in server_groups]
        return json

    def from_json(self, p_session_context: SessionContext, p_json):

        for (server_group, mapping) in p_json:
            for (login, uid) in mapping:
                self.add_entry(p_session_context=p_session_context, p_uid=uid, p_username=login,
                               p_server_group=server_group)

    def get_server_group_names(self, p_session_context: SessionContext):
        return self.uid_mapping_entity_manager.get_server_groups(p_session_context=p_session_context)

    def add_entry(self, p_session_context: SessionContext, p_uid: int, p_username: str,
                  p_server_group: str = DEFAULT_SERVER_GROUP):

        uid_mapping = UidMapping()
        uid_mapping.uid = p_uid
        uid_mapping.username = p_username
        uid_mapping.server_group = p_server_group
        self.uid_mapping_entity_manager.insert_or_update_uid_mapping(p_session_context=p_session_context,
                                                                     p_uid_mapping=uid_mapping)

        session: Session = p_session_context.get_session()
        session.add(uid_mapping)
        session.commit()

    def get_login_by_uid(self, p_session_context: SessionContext, p_uid: int,
                         p_server_group: str = DEFAULT_SERVER_GROUP) -> Optional[str]:

        uid_mapping = self.uid_mapping_entity_manager.get_by_uid_and_server_group(
            p_session_context=p_session_context, p_uid=p_uid, p_server_group=p_server_group)

        if uid_mapping:
            return uid_mapping.username

        else:
            return None

    def get_uid_by_login(self, p_session_context: SessionContext,
                         p_login: str, p_server_group: str = DEFAULT_SERVER_GROUP) -> Optional[int]:

        uid_mapping = self.uid_mapping_entity_manager.get_by_username_and_server_group(
            p_session_context=p_session_context, p_username=p_login, p_server_group=p_server_group)

        if uid_mapping:
            return uid_mapping.uid

        else:
            return None

    def read_from_configuration(self, p_session_context: SessionContext,
                                p_login_mapping_section_handler: LoginMappingSectionHandler):

        for section in p_login_mapping_section_handler._login_mapping_sections.values():
            for mapping_entry in section.mapping_entries:
                single_entries = mapping_entry.split(",")

                for entry in single_entries:
                    match = MAPPING_ENTRY_PATTERN.match(entry)

                    if match is None:
                        msg = f"Invalid logging mapping '{entry}' for host group {section.server_group}"
                        raise configuration.ConfigurationException(msg)

                    uid_mapping = UidMapping()
                    uid_mapping.server_group = section.server_group
                    uid_mapping.uid = int(match.group(2))
                    uid_mapping.username = match.group(1)
                    self.uid_mapping_entity_manager.insert_or_update_uid_mapping(p_session_context=p_session_context,
                                                                                 p_uid_mapping=uid_mapping)
