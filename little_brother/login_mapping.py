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

DEFAULT_SERVER_GROUP = "default-group"

LoginUidMappingEntry = collections.namedtuple('LoginUidMappingEntry', ['login', 'uid'])


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


    def add_entry(self, p_login_uid_mapping_entry, p_server_group=DEFAULT_SERVER_GROUP):

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

    def get_login_by_uid(self, p_uid, p_server_group=DEFAULT_SERVER_GROUP):

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
