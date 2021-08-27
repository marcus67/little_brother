# -*- coding: utf-8 -*-

# Copyright (C) 2019-2021  Marcus Rickert
#
# See https://github.com/marcus67/little_brother_taskbar
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

from little_brother import admin_event, login_mapping
from little_brother import dependency_injection
from little_brother.event_handler import EventHandler
from little_brother.login_mapping import LoginMapping
from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn
from little_brother.persistence.persistent_user import User
from little_brother.persistence.session_context import SessionContext
from little_brother.user_locale_handler import UserLocaleHandler
from little_brother.user_status import UserStatus
from python_base_app import log_handling
from python_base_app.base_user_handler import BaseUserHandler


class UserManager(PersistenceDependencyInjectionMixIn):

    def __init__(self, p_config, p_login_mapping, p_server_group, p_is_master):

        super().__init__()
        self._logger = log_handling.get_logger(self.__class__.__name__)

        self._process_regex_map = None

        self._user_handler = None
        self._event_handler = None

        self._server_group = p_server_group
        self._is_master = p_is_master
        self._config = p_config
        self._usernames_not_found = []
        self._usernames = []

        if p_login_mapping is None:
            p_login_mapping = LoginMapping(p_default_server_group=p_server_group)

        self._login_mapping = p_login_mapping

        self._user_status = {}

        self._login_mapping_received = self._is_master
        self._user_locale_handler = UserLocaleHandler()

    @property
    def event_handler(self) -> EventHandler:

        if self._event_handler is None:
            self._event_handler = dependency_injection.container[EventHandler]

        return self._event_handler

    @property
    def user_handler(self) -> BaseUserHandler:

        if self._user_handler is None:
            self._user_handler = dependency_injection.container[BaseUserHandler]

        return self._user_handler

    @property
    def usernames(self):
        return self._usernames

    def register_events(self):
        self.event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_UPDATE_LOGIN_MAPPING, p_handler=self.handle_event_update_login_mapping)

    def reset_users(self, p_session_context):
        self._process_regex_map = None
        self._usernames_not_found.extend(self.user_entity_manager.user_map(p_session_context=p_session_context).keys())

        fmt = "Watching usernames: %s" % ",".join(self._usernames_not_found)
        self._logger.info(fmt)

    def handle_event_update_login_mapping(self, p_event):

        self._login_mapping.from_json(p_json=p_event.payload)

        server_group_names = ', '.join(self._login_mapping.get_server_group_names())
        fmt = "Received login mapping for server group(s) {group_names}"
        self._logger.info(fmt.format(group_names=server_group_names))
        self._login_mapping_received = True

    def retrieve_user_mappings(self):

        if len(self._usernames_not_found) > 0:
            usernames_found = []

            for username in self._usernames_not_found:
                uid = self._login_mapping.get_uid_by_login(p_server_group=self._server_group,
                                                           p_login=username)

                if uid is None and self._login_mapping_received:
                    uid = self.user_handler.get_uid(p_username=username)

                    if uid is not None:
                        new_entry = login_mapping.LoginUidMappingEntry(username, uid)
                        self._login_mapping.add_entry(p_server_group=self._server_group,
                                                      p_login_uid_mapping_entry=new_entry)

                if uid is not None:
                    usernames_found.append(username)
                    if username not in self._usernames:
                        self._usernames.append(username)

                    fmt = "Found user information for user '{user}': UID={uid}"
                    self._logger.info(fmt.format(user=username, uid=uid))

                else:
                    fmt = "Cannot find user information for user '{user}', will retry later..."
                    self._logger.warning(fmt.format(user=username))

            for username in usernames_found:
                self._usernames_not_found.remove(username)

            if len(self._usernames_not_found) == 0:
                fmt = "Retrieved user information for all {user_count} users"
                self._logger.info(fmt.format(user_count=len(self._usernames)))

    def get_number_of_monitored_users(self):

        count = 0

        with SessionContext(p_persistence=self.persistence) as session_context:
            for user in self.user_entity_manager.users(session_context):
                if user.active and user.username in self._usernames:
                    count += 1

        return count

    def queue_event_update_login_mapping(self, p_hostname, p_login_mapping):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_UPDATE_LOGIN_MAPPING,
            p_hostname=p_hostname,
            p_payload=p_login_mapping)
        self.event_handler.queue_event(p_event=event, p_is_action=True)

    def send_login_mapping_to_slave(self, p_hostname):

        self.queue_event_update_login_mapping(p_hostname=p_hostname,
                                              p_login_mapping=self._login_mapping.to_json())

    def get_current_user_status(self, p_session_context: SessionContext, p_username: str):

        current_user_status = self._user_status.get(p_username)

        if current_user_status is None:
            current_user_status = UserStatus(p_username=p_username)
            self._user_status[p_username] = current_user_status

        current_user_status.warning_time_without_send_events = self._config.warning_time_without_send_events
        current_user_status.maximum_time_without_send_events = self._config.maximum_time_without_send_events

        current_user_status.locale = self._user_locale_handler.get_user_locale(
            p_session_context=p_session_context, p_username=p_username)

        user: User = self.user_entity_manager.user_map(p_session_context=p_session_context).get(p_username)

        current_user_status.monitoring_active = user.active if user is not None else False

        return current_user_status

    def add_monitored_user(self, p_username):

        if p_username not in self._usernames:
            self._usernames_not_found.append(p_username)
            fmt = "Adding new monitored user '{username}'"
            self._logger.info(fmt.format(username=p_username))

    def issue_notification(self, p_session_context, p_username, p_message):

        current_user_status = self.get_current_user_status(p_session_context=p_session_context, p_username=p_username)
        current_user_status.notification = p_message
