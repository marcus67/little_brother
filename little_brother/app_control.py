# -*- coding: utf-8 -*-

# Copyright (C) 2019-2021  Marcus Rickert
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
import gettext
import os.path
import socket
import sys
import time

import prometheus_client

from little_brother import admin_event
from little_brother import client_stats
from little_brother import constants
from little_brother import dependency_injection
from little_brother import login_mapping
from little_brother import process_info
from little_brother import process_statistics
from little_brother import rule_handler
from little_brother import rule_override
from little_brother import settings
from little_brother import user_status
from little_brother.admin_data_handler import AdminDataHandler
from little_brother.app_control_config_model import AppControlConfigModel
from little_brother.client_info import ClientInfo
from little_brother.event_handler import EventHandler
from little_brother.master_connector import MasterConnector
from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn
from little_brother.persistence.persistent_user import User
from little_brother.persistence.session_context import SessionContext
from little_brother.rule_handler import RuleHandler
from little_brother.user_locale_handler import UserLocaleHandler
from python_base_app import log_handling
from python_base_app import tools

DEFAULT_SCAN_ACTIVE = True
DEFAULT_ADMIN_LOOKAHEAD_IN_DAYS = 7  # days
DEFAULT_PROCESS_LOOKUP_IN_DAYS = 7  # days
DEFAULT_HISTORY_LENGTH_IN_DAYS = 180  # days
DEFAULT_MIN_ACTIVITY_DURATION = 60  # seconds
DEFAULT_CHECK_INTERVAL = 5  # seconds
DEFAULT_INDEX_REFRESH_INTERVAL = 60  # seconds
DEFAULT_TOPOLOGY_REFRESH_INTERVAL = 60  # seconds
DEFAULT_MAXIMUM_CLIENT_PING_INTERVAL = 60  # seconds
DEFAULT_WARNING_TIME_WITHOUT_SEND_EVENTS = 3 * DEFAULT_CHECK_INTERVAL  # seconds
DEFAULT_MAXIMUM_TIME_WITHOUT_SEND_EVENTS = 10 * DEFAULT_CHECK_INTERVAL  # minutes
DEFAULT_KILL_PROCESS_DELAY = 10  # seconds
DEFAULT_TIME_EXTENSION_PERIODS = "-30,-15,-5,5,10,15,30,45,60"

ALEMBIC_VERSION_INIT_GUI_CONFIGURATION = ""

SECTION_NAME = "AppControl"

LAST_VERSION_WITHOUT_CLIENT_STAT_SUPPORT = "0.3.8"
MINIMUM_VERSION_WITH_CLIENT_STAT_SUPPORT = "0.3.9"

CSS_CLASS_MAXIMUM_PING_EXCEEDED = "node_inactive"
CSS_CLASS_SLAVE_VERSION_OUTDATED = "node_outdated"

# Dummy function to trigger extraction by pybabel...
_ = lambda x, y=None: x


class AppControl(PersistenceDependencyInjectionMixIn):

    def __init__(self, p_config,
                 p_debug_mode,
                 p_process_handlers=None,
                 p_device_handler=None,
                 p_notification_handlers=None,
                 p_prometheus_client=None,
                 p_user_handler=None,
                 p_login_mapping=None,
                 p_locale_helper=None):

        super().__init__()

        self._config: AppControlConfigModel = p_config
        self._debug_mode = p_debug_mode
        self._process_handlers = p_process_handlers
        self._device_handler = p_device_handler

        self._rule_handler = None
        self._notification_handlers = p_notification_handlers
        self._master_connector = None
        self._prometheus_client = p_prometheus_client
        self._user_handler = p_user_handler
        self._locale_helper = p_locale_helper
        self._time_last_successful_send_events = tools.get_current_time()
        self._user_locale_handler = UserLocaleHandler()
        self._admin_data_handler = None

        if self._config.hostname is None:
            self._host_name = socket.getfqdn()

        else:
            self._host_name = self._config.hostname

        self._event_handler = EventHandler(p_host_name=self._host_name, p_is_master=self.is_master())

        dependency_injection.container[EventHandler] = self._event_handler

        self._event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_PROCESS_START, p_handler=self.handle_event_process_start)
        self._event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_PROCESS_DOWNTIME, p_handler=self.handle_event_process_downtime)
        self._event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_PROCESS_END, p_handler=self.handle_event_process_end)
        self._event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_KILL_PROCESS, p_handler=self.handle_event_kill_process)
        self._event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_SPEAK, p_handler=self.handle_event_speak)
        self._event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_START_CLIENT, p_handler=self.handle_event_start_client)
        self._event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_START_MASTER, p_handler=self.handle_event_start_master)
        self._event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_UPDATE_CONFIG, p_handler=self.handle_event_update_config)
        self._event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_UPDATE_LOGIN_MAPPING, p_handler=self.handle_event_update_login_mapping)

        # self._session_context = persistence.SessionContext(p_persistence=self.persistence, p_register=True)

        if p_login_mapping is None:
            p_login_mapping = login_mapping.LoginMapping(p_default_server_group=self._config.server_group)

        self._logger = log_handling.get_logger(self.__class__.__name__)

        self._usernames_not_found = []
        self._usernames = []
        self._process_regex_map = None
        # self._uid_map = {}
        # self._username_map = p_login_mapping

        self._logout_warnings = {}

        with SessionContext(p_persistence=self.persistence) as session_context:
            self.reset_users(p_session_context=session_context)

        self._could_not_send = False

        self._client_infos = {}
        self._user_status = {}

        self.init_labels_and_notifications()
        self._locale_dir = os.path.join(os.path.dirname(__file__), "translations")
        self._login_mapping = p_login_mapping
        self._login_mapping_received = self.is_master()

        self._start_time = time.time()

    @property
    def rule_handler(self) -> RuleHandler:

        if self._rule_handler is None:
            self._rule_handler = dependency_injection.container[RuleHandler]

        return self._rule_handler

    @property
    def admin_data_handler(self) -> AdminDataHandler:

        if self._admin_data_handler is None:
            self._admin_data_handler = dependency_injection.container[AdminDataHandler]

        return self._admin_data_handler

    @property
    def master_connector(self) -> MasterConnector:

        if self._master_connector is None:
            self._master_connector = dependency_injection.container[MasterConnector]

        return self._master_connector

    def reset_users(self, p_session_context):
        self._process_regex_map = None
        self._usernames_not_found.extend(self.user_entity_manager.user_map(p_session_context=p_session_context).keys())

        fmt = "Watching usernames: %s" % ",".join(self._usernames_not_found)
        self._logger.info(fmt)

    def get_number_of_monitored_users_function(self):
        return lambda: self.get_number_of_monitored_users()

    @property
    def usernames(self):
        return self._usernames

    @property
    def check_interval(self):
        return self._config.check_interval

    def init_labels_and_notifications(self):

        self.text_no_time_left = _("{user}, you do not have computer time left today.\nYou will be logged out.")
        self.text_no_time_left_approaching = _(
            "{user}, you only have {minutes_left_before_logout} minutes left today.\nPlease, log out.")
        self.text_no_time_left_in_time_extension = _(
            "{user}, you only have {minutes_left_before_logout} minutes left in your time extension.\nPlease, log out.")
        self.text_no_time_today = _("{user}, you do not have any computer time today.\nYou will be logged out.")
        self.text_too_early = _("{user}, it is too early to use the computer.\nYou will be logged out.")
        self.text_too_late = _("{user}, it is too late to use the computer.\nYou will be logged out.")
        self.text_too_late_approaching = _(
            "{user}, in {minutes_left_before_logout} minutes it will be too late to use the computer.\nPlease, log out.")
        self.text_need_break = _("{user}, you have to take a break.\nYou will be logged out.")
        self.text_need_break_approaching = _(
            "{user}, in {minutes_left_before_logout} minutes you will have to take a break.\nPlease, log out.")
        self.text_min_break = _(
            "{user}, your break will only be over in {break_minutes_left} minutes.\nYou will be logged out.")
        self.text_limited_session_start = _(
            "Hello {user}, you will be allowed to play for {minutes_left_in_session} minutes\nin this session.")
        self.text_unlimited_session_start = _("Hello {user}, you have unlimited playtime in this session.")

    def set_user_configs(self, p_user_configs):

        with SessionContext(p_persistence=self.persistence) as session_context:

            session = session_context.get_session()

            # Delete all locally known users since the message from the master will not contain users
            # that have been deleted on the master. These might otherwise remain active on the client.
            for user in self.user_entity_manager.users(p_session_context=session_context):
                session.delete(user)

            session.commit()

            for username, user_config in p_user_configs.items():
                user = self.user_entity_manager.get_by_username(p_session_context=session_context, p_username=username)

                if user is None:
                    user = User()
                    user.username = username
                    session.add(user)

                user.process_name_pattern = user_config[constants.JSON_PROCESS_NAME_PATTERN]
                user.active = user_config[constants.JSON_ACTIVE]

                fmt = "Set config for {user}"
                self._logger.info(fmt.format(user=str(user)))

            session.commit()
            self.reset_users(p_session_context=session_context)

    @property
    def process_regex_map(self):

        with SessionContext(p_persistence=self.persistence) as session_context:
            if self._process_regex_map is None:
                self._process_regex_map = {}

                for user in self.user_entity_manager.users(session_context):
                    self._process_regex_map[user.username] = user.regex_process_name_pattern

        return self._process_regex_map

    def retrieve_user_mappings(self):

        if len(self._usernames_not_found) > 0:
            usernames_found = []

            for username in self._usernames_not_found:
                uid = self._login_mapping.get_uid_by_login(p_server_group=self._config.server_group,
                                                           p_login=username)

                if uid is None and self._login_mapping_received:
                    uid = self._user_handler.get_uid(p_username=username)

                    if uid is not None:
                        new_entry = login_mapping.LoginUidMappingEntry(username, uid)
                        self._login_mapping.add_entry(p_server_group=self._config.server_group,
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

    def is_master(self):

        if self.master_connector is None:
            # This is for test cases which do not instantiate a master connector
            return True

        else:
            return self.master_connector._config.host_url is None

    def set_prometheus_http_requests_summary(self, p_hostname, p_service, p_duration):

        if self._prometheus_client is not None:
            # try to resolve ip addresses
            p_hostname = tools.get_dns_name_by_ip_address(p_ip_address=p_hostname)
            self._prometheus_client.set_http_requests_summary(p_hostname=p_hostname,
                                                              p_service=p_service,
                                                              p_duration=p_duration)

    def get_number_of_monitored_users(self):

        count = 0

        with SessionContext(p_persistence=self.persistence) as session_context:
            for user in self.user_entity_manager.users(session_context):
                if user.active and user.username in self._usernames:
                    count += 1

        return count

    def set_metrics(self):

        with SessionContext(p_persistence=self.persistence) as session_context:
            if self._prometheus_client is not None:
                self._prometheus_client.set_uptime(p_hostname="master", p_uptime=time.time() - self._start_time)

                self._prometheus_client.set_number_of_monitored_users(self.get_number_of_monitored_users())
                self._prometheus_client.set_number_of_configured_users(
                    len(self.user_entity_manager.user_map(session_context)))

                if self._config.scan_active:
                    self._prometheus_client.set_monitored_host(self._host_name, True)

                latest_ping_time = tools.get_current_time() + \
                                   datetime.timedelta(seconds=-self._config.maximum_client_ping_interval)

                for hostname, client_info in self._client_infos.items():
                    active = client_info.last_message > latest_ping_time
                    self._prometheus_client.set_monitored_host(hostname, active)

                if self._device_handler is not None:
                    self._prometheus_client.set_number_of_monitored_devices(
                        self._device_handler.get_number_of_monitored_devices())

                    for device_info in self._device_handler.device_infos.values():
                        self._prometheus_client.set_device_active(
                            device_info.device_name, 1 if device_info.is_up else 0)
                        self._prometheus_client.set_device_response_time(
                            device_info.device_name, device_info.response_time)
                        self._prometheus_client.set_device_moving_average_response_time(
                            device_info.device_name, device_info.moving_average_response_time)

                else:
                    self._prometheus_client.set_number_of_monitored_devices(0)

                for client_info in self._client_infos.values():
                    if client_info.client_stats is not None:
                        self._prometheus_client.set_client_stats(p_hostname=client_info.host_name,
                                                                 p_client_stats=client_info.client_stats)

    def check(self):

        self.retrieve_user_mappings()

        reference_time = datetime.datetime.now()

        self._event_handler.process_queue()

        if self.is_master():
            self.process_rules(p_reference_time=reference_time)
            self._event_handler.process_queue()
            self.set_metrics()

        else:
            self.send_events()
            self.check_network()
            self._event_handler.process_queue()

    def check_network(self):

        time_since_last_send = int((tools.get_current_time() - self._time_last_successful_send_events).total_seconds())

        if self._config.warning_time_without_send_events <= time_since_last_send < self._config.maximum_time_without_send_events:
            msg = "No successful send events for {seconds} seconds"
            self._logger.warning(msg.format(seconds=time_since_last_send))

        elif time_since_last_send >= self._config.maximum_time_without_send_events:
            self.queue_artificial_kill_events()

    def start(self):

        if self.is_master():
            fmt = "Starting application in MASTER mode"
            self._logger.info(fmt)

            self.load_historic_process_infos()
            self.send_historic_process_infos()
            self.admin_data_handler.load_rule_overrides()
        #             self.queue_broadcast_event_start_master()

        else:
            fmt = "Starting application in SLAVE mode communication with master at URL {master_url}"
            self._logger.info(fmt.format(master_url=self.master_connector._get_api_url()))

            self.queue_event_start_client()

        fmt = "Using fully qualified domain name '%s' for process infos" % self._host_name
        self._logger.info(fmt)

    def stop(self):

        for handler in self._process_handlers.values():
            events = handler.get_artificial_termination_events()

            fmt = "Artificially terminating {process_count} active processes on {handler_id}"
            self._logger.info(fmt.format(process_count=len(events), handler_id=handler.id))

            self._event_handler.queue_events(p_events=events, p_to_master=True)

        self._event_handler.process_queue()

        if not self.is_master():
            self.send_events()

    def clean_history(self):

        history_length_in_days = self._config.history_length_in_days

        msg = "Deleting historic entries older than {days} days..."
        self._logger.info(msg.format(days=history_length_in_days))

        with SessionContext(p_persistence=self.persistence) as session_context:
            self.rule_override_entity_manager.delete_historic_entries(p_session_context=session_context,
                                                                      p_history_length_in_days=history_length_in_days)
            self.process_info_entity_manager.delete_historic_entries(p_session_context=session_context,
                                                                     p_history_length_in_days=history_length_in_days)
            self.admin_event_entity_manager.delete_historic_entries(p_session_context=session_context,
                                                                    p_history_length_in_days=history_length_in_days)

    def get_process_handler(self, p_id, p_raise_exception=False):

        handler = self._process_handlers.get(p_id)

        if handler is None and p_raise_exception:
            fmt = "Unknown process handler '{handler_id}'"
            raise Exception(fmt.format(handler_id=p_id))

        return handler

    def handle_event_process_downtime(self, p_event):

        pinfo, updated = self.get_process_handler(p_id=p_event.processhandler).handle_event_process_downtime(p_event)

        if self.persistence is not None and updated:
            with SessionContext(p_persistence=self.persistence) as session_context:
                self.process_info_entity_manager.update_process_info(
                    p_session_context=session_context, p_process_info=pinfo)

    def handle_event_process_start(self, p_event):

        process_handler = self.get_process_handler(p_id=p_event.processhandler)

        if process_handler is None:
            msg = "Received event for process handler of type id '{id}' which is not registered -> discarding event"
            self._logger.warning(msg.format(id=p_event.processhandler))
            return

        pinfo, updated = process_handler.handle_event_process_start(p_event)

        if updated:
            if self.persistence is not None:
                with SessionContext(p_persistence=self.persistence) as session_context:
                    self.process_info_entity_manager.update_process_info(
                        p_session_context=session_context, p_process_info=pinfo)

        else:
            if self.persistence is not None:
                with SessionContext(p_persistence=self.persistence) as session_context:
                    self.process_info_entity_manager.write_process_info(
                        p_session_context=session_context, p_process_info=pinfo)

        if self.is_master():
            rule_result_info = self.admin_data_handler.get_current_rule_result_info(
                p_reference_time=datetime.datetime.now(), p_process_infos=self.get_process_infos(),
                p_username=p_event.username)

            if rule_result_info.activity_allowed():
                if rule_result_info.limited_session_time():
                    self.queue_event_speak(
                        p_hostname=p_event.hostname,
                        p_username=p_event.username,
                        p_text=self.pick_text_for_ruleset(p_rule_result_info=rule_result_info,
                                                          p_text=self.text_limited_session_start))

                else:
                    self.queue_event_speak(
                        p_hostname=p_event.hostname,
                        p_username=p_event.username,
                        p_text=self.pick_text_for_ruleset(p_rule_result_info=rule_result_info,
                                                          p_text=self.text_unlimited_session_start))

    def handle_event_process_end(self, p_event):

        pinfo = self.get_process_handler(p_id=p_event.processhandler).handle_event_process_end(p_event)

        if pinfo is None:
            return

        if self.persistence is not None:
            with SessionContext(p_persistence=self.persistence) as session_context:
                self.process_info_entity_manager.update_process_info(
                    p_session_context=session_context, p_process_info=pinfo)

    def handle_event_kill_process(self, p_event):

        return self.get_process_handler(
            p_id=p_event.processhandler).handle_event_kill_process(p_event, p_server_group=self._config.server_group,
                                                                   p_login_mapping=self._login_mapping)

    def handle_event_speak(self, p_event):

        with SessionContext(p_persistence=self.persistence) as session_context:
            if p_event.locale is None:
                user_locale = self._user_locale_handler.get_user_locale(p_session_context=session_context,
                                                                        p_username=p_event.username)

            else:
                user_locale = p_event.locale

            for notification_handler in self._notification_handlers:
                notification_handler.notify(p_text=p_event.text, p_locale=user_locale)

    def handle_event_update_config(self, p_event):

        if constants.JSON_USER_CONFIG in p_event.payload:
            # New mode (version >= 0.3.13)
            user_config_payload = p_event.payload[constants.JSON_USER_CONFIG]
            self._config.maximum_time_without_send_events = p_event.payload.get(
                constants.JSON_MAXIMUM_TIME_WITHOUT_SEND)

        else:
            # Compatibilty mode (version < 0.3.13)
            user_config_payload = p_event.payload

        user_configs = {}

        for username, user_config in user_config_payload.items():
            user_configs[username] = user_config

        self.set_user_configs(p_user_configs=user_configs)

    def handle_event_update_login_mapping(self, p_event):

        self._login_mapping.from_json(p_json=p_event.payload)

        server_group_names = ', '.join(self._login_mapping.get_server_group_names())
        fmt = "Received login mapping for server group(s) {group_names}"
        self._logger.info(fmt.format(group_names=server_group_names))
        self._login_mapping_received = True

    def update_client_info(self, p_hostname, p_client_stats=None):

        client_info = self._client_infos.get(p_hostname)

        if client_info is None:
            client_info = ClientInfo(p_host_name=p_hostname, p_client_stats=p_client_stats, p_is_master=False,
                                     p_maximum_client_ping_interval=self._config.maximum_client_ping_interval,
                                     p_master_version=self.get_client_version(),
                                     )
            self._client_infos[p_hostname] = client_info

        client_info.last_message = tools.get_current_time()
        client_info.client_stats = p_client_stats

    def handle_event_start_client(self, p_event):

        self.update_client_info(p_event.hostname)
        self.send_config_to_slave(p_event.hostname)
        self.send_login_mapping_to_slave(p_event.hostname)
        self.send_historic_process_infos()

    def handle_event_start_master(self):

        self.queue_artificial_activation_events()

    def send_config_to_slave(self, p_hostname):

        config = {}

        with SessionContext(p_persistence=self.persistence) as session_context:
            user_config = {
                user.username: {constants.JSON_PROCESS_NAME_PATTERN: user.process_name_pattern,
                                constants.JSON_ACTIVE: user.active}
                for user in self.user_entity_manager.users(p_session_context=session_context)
            }

        config[constants.JSON_USER_CONFIG] = user_config
        config[constants.JSON_MAXIMUM_TIME_WITHOUT_SEND] = self._config.maximum_time_without_send_events

        self.queue_event_update_config(p_hostname=p_hostname, p_config=config)

    def send_config_to_all_slaves(self):

        for client in self._client_infos.values():
            self.send_config_to_slave(p_hostname=client.host_name)

    def send_login_mapping_to_slave(self, p_hostname):

        self.queue_event_update_login_mapping(p_hostname=p_hostname,
                                              p_login_mapping=self._login_mapping.to_json())

    def process_event(self, p_event):

        new_events = []
        fmt = "Processing {event}"
        self._logger.debug(fmt.format(event=p_event))

        if p_event.event_type == admin_event.EVENT_TYPE_PROCESS_START:
            self.handle_event_process_start(p_event=p_event)

        elif p_event.event_type == admin_event.EVENT_TYPE_PROCESS_DOWNTIME:
            self.handle_event_process_downtime(p_event=p_event)

        elif p_event.event_type == admin_event.EVENT_TYPE_PROCESS_END:
            self.handle_event_process_end(p_event=p_event)

        elif p_event.event_type == admin_event.EVENT_TYPE_KILL_PROCESS:
            new_events = self.handle_event_kill_process(p_event=p_event)

        elif p_event.event_type == admin_event.EVENT_TYPE_SPEAK:
            self.handle_event_speak(p_event=p_event)

        elif p_event.event_type == admin_event.EVENT_TYPE_START_CLIENT:
            self.handle_event_start_client(p_event=p_event)

        elif p_event.event_type == admin_event.EVENT_TYPE_START_MASTER:
            self.handle_event_start_master()

        elif p_event.event_type == admin_event.EVENT_TYPE_UPDATE_CONFIG:
            self.handle_event_update_config(p_event=p_event)

        elif p_event.event_type == admin_event.EVENT_TYPE_UPDATE_LOGIN_MAPPING:
            self.handle_event_update_login_mapping(p_event=p_event)

        else:
            raise Exception("Invalid event type '%s' found" % p_event.event_type)

        if self.persistence is not None:
            with SessionContext(p_persistence=self.persistence) as session_context:
                self.admin_event_entity_manager.log_admin_event(p_session_context=session_context,
                                                                p_admin_event=p_event)

        return new_events

    def scan_processes(self, p_process_handler, p_reference_time=None, p_queue_events=True):  # @DontTrace

        if p_reference_time is None:
            p_reference_time = datetime.datetime.now()

        with SessionContext(p_persistence=self.persistence) as session_context:
            events = p_process_handler.scan_processes(
                p_session_context=session_context,
                p_server_group=self._config.server_group, p_login_mapping=self._login_mapping,
                p_host_name=self._host_name,
                p_process_regex_map=self.process_regex_map,
                p_reference_time=p_reference_time)

            if p_queue_events:
                self._event_handler.queue_events(p_events=events, p_to_master=True)

                if not self.is_master():
                    self._event_handler.queue_events_locally(p_events=events)

    def get_process_infos(self):

        process_infos = {}

        for handler in self._process_handlers.values():
            process_infos.update(handler.process_infos)

        return process_infos

    def load_historic_process_infos(self):

        with SessionContext(p_persistence=self.persistence) as session_context:
            pinfos = self.process_info_entity_manager.load_process_infos(
                p_session_context=session_context, p_lookback_in_days=self._config.process_lookback_in_days + 1)

        counter_open_end_time = 0

        for pinfo in pinfos:

            if pinfo.end_time is None:
                end_time = None

            else:
                end_time = pinfo.end_time

            new_pinfo = process_info.ProcessInfo(
                p_hostname=pinfo.hostname,
                p_hostlabel=pinfo.hostlabel,
                p_pid=pinfo.pid,
                p_processhandler=pinfo.processhandler,
                p_username=pinfo.username,
                p_processname=pinfo.processname,
                p_start_time=pinfo.start_time,
                p_downtime=pinfo.downtime,
                p_percent=pinfo.percent,
                p_end_time=end_time)

            if not new_pinfo.is_valid():
                fmt = "Loaded {process_info} is invalid -> ignore"
                self._logger.warning(fmt.format(process_info=str(new_pinfo)))
                continue

            if new_pinfo.end_time is None:
                counter_open_end_time = counter_open_end_time + 1

            process_handler = self.get_process_handler(p_id=new_pinfo.processhandler, p_raise_exception=False)

            if process_handler is not None:
                process_handler.add_historic_process(p_process_info=new_pinfo)

        fmt = "Loaded %d historic process infos from database looking back %s days (%d of which had no end time)" % (
            len(pinfos), self._config.process_lookback_in_days, counter_open_end_time)
        self._logger.info(fmt)

    def send_historic_process_infos(self):

        counter = 0

        for pinfo in self.get_process_infos().values():
            if pinfo.end_time is None:
                if pinfo.hostname != self._host_name:
                    self.queue_event_historic_process_start(p_pinfo=pinfo)
                    counter = counter + 1

        fmt = "Sent %d historic process infos to slaves" % counter
        self._logger.info(fmt)

    def pick_text_for_ruleset(self, p_rule_result_info, p_text=None):

        t = gettext.translation('messages', localedir=self._locale_dir,
                                languages=[p_rule_result_info.locale], fallback=True)

        if p_text is not None:
            return t.gettext(p_text).format(**p_rule_result_info.args)

        elif p_rule_result_info.applying_rules & rule_handler.RULE_TIME_PER_DAY:
            return t.gettext(self.text_no_time_left).format(**p_rule_result_info.args)

        elif p_rule_result_info.applying_rules & rule_handler.RULE_DAY_BLOCKED:
            return t.gettext(self.text_no_time_today).format(**p_rule_result_info.args)

        elif p_rule_result_info.applying_rules & rule_handler.RULE_TOO_EARLY:
            return t.gettext(self.text_too_early).format(**p_rule_result_info.args)

        elif p_rule_result_info.applying_rules & rule_handler.RULE_TOO_LATE:
            return t.gettext(self.text_too_late).format(**p_rule_result_info.args)

        elif p_rule_result_info.applying_rules & rule_handler.RULE_ACTIVITY_DURATION:
            return t.gettext(self.text_need_break).format(**p_rule_result_info.args)

        elif p_rule_result_info.applying_rules & rule_handler.RULE_MIN_BREAK:
            return t.gettext(self.text_min_break).format(**p_rule_result_info.args)

        else:
            fmt = "pick_text_for_ruleset(): cannot derive text for rule result %d" % p_rule_result_info.applying_rules
            self._logger.warning(fmt)
            return ""

    def pick_text_for_approaching_logout(self, p_rule_result_info):

        t = gettext.translation('messages', localedir=self._locale_dir,
                                languages=[p_rule_result_info.locale], fallback=True)

        if p_rule_result_info.approaching_logout_rules & rule_handler.RULE_ACTIVITY_DURATION:
            return t.gettext(self.text_need_break_approaching).format(**p_rule_result_info.args)

        elif p_rule_result_info.approaching_logout_rules & rule_handler.RULE_TOO_LATE:
            return t.gettext(self.text_too_late_approaching).format(**p_rule_result_info.args)

        elif p_rule_result_info.approaching_logout_rules & rule_handler.RULE_TIME_PER_DAY:
            return t.gettext(self.text_no_time_left_approaching).format(**p_rule_result_info.args)

        elif p_rule_result_info.approaching_logout_rules & rule_handler.RULE_TIME_EXTENSION:
            return t.gettext(self.text_no_time_left_in_time_extension).format(**p_rule_result_info.args)

        else:
            fmt = "pick_text_for_approaching_logout(): cannot derive text for rule result {mask}"
            self._logger.warning(fmt.format(mask=p_rule_result_info.approaching_logout_rules))
            return ""

    def get_current_user_status(self, p_username):

        current_user_status = self._user_status.get(p_username)

        if current_user_status is None:
            current_user_status = user_status.UserStatus(p_username=p_username)
            self._user_status[p_username] = current_user_status

        current_user_status.warning_time_without_send_events = self._config.warning_time_without_send_events
        current_user_status.maximum_time_without_send_events = self._config.maximum_time_without_send_events

        with SessionContext(p_persistence=self.persistence) as session_context:
            current_user_status.locale = self._user_locale_handler.get_user_locale(
                p_session_context=session_context, p_username=p_username)

        return current_user_status

    def process_rules(self, p_reference_time):

        fmt = "Processing rules START..."
        self._logger.debug(fmt)

        with SessionContext(p_persistence=self.persistence) as session_context:
            users_stat_infos = process_statistics.get_process_statistics(
                p_process_infos=self.get_process_infos(),
                p_reference_time=p_reference_time,
                p_max_lookback_in_days=self._config.process_lookback_in_days,
                p_user_map=self.user_entity_manager.user_map(session_context),
                p_min_activity_duration=self._config.min_activity_duration)

            active_time_extensions = self.time_extension_entity_manager.get_active_time_extensions(
                p_session_context=session_context, p_reference_datetime=tools.get_current_time())

            for user in self.user_entity_manager.users(session_context):
                if user.active and user.username in self._usernames:

                    user_active = False

                    user_locale = self._user_locale_handler.get_user_locale(
                        p_username=user.username, p_session_context=session_context)

                    rule_set = self.rule_handler.get_active_ruleset(
                        p_rule_sets=user.rulesets, p_reference_date=p_reference_time.date())

                    stat_infos = users_stat_infos.get(user.username)

                    if stat_infos is not None:
                        stat_info = stat_infos.get(rule_set.context)

                        if stat_info is not None:
                            self._logger.debug(str(stat_info))

                            key_rule_override = rule_override.get_key(p_username=user.username,
                                                                      p_reference_date=p_reference_time.date())
                            override = self.admin_data_handler.rule_overrides.get(key_rule_override)

                            if rule_override is not None:
                                self._logger.debug(str(override))

                            active_rule_set = self.rule_handler.get_active_ruleset(
                                p_reference_date=p_reference_time, p_rule_sets=user.rulesets)

                            rule_result_info = self.rule_handler.process_ruleset(
                                p_active_rule_set=active_rule_set,
                                p_stat_info=stat_info,
                                p_active_time_extension=active_time_extensions.get(user.username),
                                p_reference_time=p_reference_time,
                                p_rule_override=override,
                                p_locale=user_locale)

                            current_user_status = self.get_current_user_status(p_username=user.username)

                            if rule_result_info.limited_session_time():
                                current_user_status.minutes_left_in_session = rule_result_info.get_minutes_left_in_session()

                            else:
                                current_user_status.minutes_left_in_session = None

                            current_user_status.activity_allowed = rule_result_info.activity_allowed()
                            user_active = stat_info.current_activity is not None
                            current_user_status.logged_in = user_active

                            if not rule_result_info.activity_allowed():
                                fmt = "Process %s" % str(rule_result_info.effective_rule_set)
                                self._logger.debug(fmt)

                                for (hostname, processes) in stat_info.currently_active_host_processes.items():

                                    fmt = "User %s has %d active process(es) on host %s" % (
                                        user.username, len(processes), hostname)
                                    self._logger.debug(fmt)

                                    process_killed = False

                                    for processhandler_id, pid, process_start_time in processes:
                                        processhandler = self._process_handlers.get(processhandler_id)

                                        if processhandler is not None and processhandler.can_kill_processes():
                                            if self._prometheus_client is not None:
                                                self._prometheus_client.count_forced_logouts(p_username=user.username)

                                            self.queue_event_kill_process(
                                                p_hostname=hostname,
                                                p_username=user.username,
                                                p_processhandler=processhandler_id,
                                                p_pid=pid,
                                                p_process_start_time=process_start_time)
                                            process_killed = True

                                    if process_killed:
                                        self.queue_event_speak(
                                            p_hostname=hostname,
                                            p_username=user.username,
                                            p_text=self.pick_text_for_ruleset(p_rule_result_info=rule_result_info))

                                        self.reset_logout_warning(p_username=user.username)

                            elif rule_result_info.approaching_logout_rules > 0:
                                for (hostname, processes) in stat_info.currently_active_host_processes.items():
                                    self.issue_logout_warning(p_hostname=hostname, p_username=user.username,
                                                              p_rule_result_info=rule_result_info)

                    if self._prometheus_client is not None:
                        self._prometheus_client.set_user_active(p_username=user.username, p_is_active=user_active)

        fmt = "Processing rules END..."
        self._logger.debug(fmt)

    def issue_logout_warning(self, p_hostname, p_username, p_rule_result_info):

        current_warning = self._logout_warnings.get(p_username)
        issue_warning = False

        if current_warning is None:
            current_warning = p_rule_result_info.minutes_left_before_logout
            issue_warning = True
            self._logout_warnings[p_username] = current_warning

        if p_rule_result_info.minutes_left_before_logout < current_warning:
            issue_warning = True

        if issue_warning:
            self._logout_warnings[p_username] = p_rule_result_info.minutes_left_before_logout
            self.queue_event_speak(
                p_hostname=p_hostname,
                p_username=p_username,
                p_text=self.pick_text_for_approaching_logout(p_rule_result_info=p_rule_result_info))

    def reset_logout_warning(self, p_username):

        if p_username in self._logout_warnings:
            del self._logout_warnings[p_username]

    ################################################################################################################################
    ################################################################################################################################
    ################################################################################################################################

    def queue_event_speak(self, p_hostname, p_username, p_text):

        current_user_status = self.get_current_user_status(p_username=p_username)

        current_user_status.notification = p_text

        with SessionContext(p_persistence=self.persistence) as session_context:
            locale = self._user_locale_handler.get_user_locale(p_username=p_username, p_session_context=session_context)

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_SPEAK,
            p_hostname=p_hostname,
            p_username=p_username,
            p_text=p_text,
            p_locale=locale)
        self._event_handler.queue_event(p_event=event, p_is_action=True)

    def queue_event_start_client(self):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_START_CLIENT,
            p_hostname=self._host_name)
        self._event_handler.queue_event(p_event=event, p_to_master=True)

    #     def queue_broadcast_event_start_master(self):
    #
    #         for hostname in self._client_infos.keys():
    #             event = admin_event.AdminEvent(
    #                 p_event_type=admin_event.EVENT_TYPE_START_MASTER,
    #                 p_hostname=hostname)
    #             self._event_handler.queue_event(p_event=event, p_is_action=True)

    def queue_event_kill_process(self, p_hostname, p_username, p_processhandler, p_pid, p_process_start_time):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_KILL_PROCESS,
            p_hostname=p_hostname,
            p_username=p_username,
            p_processhandler=p_processhandler,
            p_pid=p_pid,
            p_process_start_time=p_process_start_time,
            p_delay=self._config.kill_process_delay)
        self._event_handler.queue_event(p_event=event, p_is_action=True)

    def queue_event_update_config(self, p_hostname, p_config):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_UPDATE_CONFIG,
            p_hostname=p_hostname,
            p_payload=p_config)
        self._event_handler.queue_event(p_event=event, p_is_action=True)

    def queue_event_update_login_mapping(self, p_hostname, p_login_mapping):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_UPDATE_LOGIN_MAPPING,
            p_hostname=p_hostname,
            p_payload=p_login_mapping)
        self._event_handler.queue_event(p_event=event, p_is_action=True)

    def queue_event_historic_process_start(self, p_pinfo):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_PROCESS_START,
            p_hostname=p_pinfo.hostname,
            p_pid=p_pinfo.pid,
            p_username=p_pinfo.username,
            p_process_start_time=p_pinfo.start_time)
        self._event_handler.queue_event(p_event=event, p_is_action=True)

    def queue_artificial_activation_events(self):

        for handler in self._process_handlers.values():
            events = handler.get_artificial_activation_events()

            fmt = "Artificially activating {process_count} active processes on handler {handler_id}"
            self._logger.info(fmt.format(process_count=len(events), handler_id=handler.id))

            self._event_handler.queue_events(p_events=events, p_to_master=True)

    def queue_artificial_kill_events(self):

        for handler in self._process_handlers.values():
            events = handler.get_artificial_kill_events()

            fmt = "Artificially killing {process_count} active processes on handler {handler_id}"
            self._logger.info(fmt.format(process_count=len(events), handler_id=handler.id))

            self._event_handler.queue_events(p_events=events, p_to_master=False)

    def get_unmonitored_users(self, p_session_context):

        return [username for username in self._user_handler.list_users() if
                username not in self.user_entity_manager.user_map(p_session_context)]

    def get_unmonitored_devices(self, p_user, p_session_context):

        monitored_devices = [user2device.device.device_name for user2device in p_user.devices]
        return [device for device in self.device_entity_manager.devices(p_session_context)
                if device.device_name not in monitored_devices]

    def get_topology_infos(self, p_session_context):

        topology_infos = [info for info in self._client_infos.values()]

        master_stats = self.get_client_stats()
        master_info = ClientInfo(p_is_master=True, p_host_name=self._host_name, p_client_stats=master_stats)

        topology_infos.append(master_info)

        sorted_infos = sorted(topology_infos, key=lambda info: (0 if info.is_master else 1, info.host_name))
        return sorted_infos

    def get_client_version(self):
        return settings.settings['version']

    def get_client_stats(self):

        a_client_stats = client_stats.ClientStats(
            p_version=self.get_client_version(),
            p_revision=settings.extended_settings['debian_package_revision'],
            p_python_version="{major}.{minor}.{micro}".format(major=sys.version_info.major,
                                                              minor=sys.version_info.minor,
                                                              micro=sys.version_info.micro),
            p_running_in_docker=tools.running_in_docker()
        )

        if not self.is_master():
            # Use the Prometheus Client ProcessCollector to retrieve run time stats for CPU and memory usage
            # to be consistent with the stats collected on the master.

            collector = prometheus_client.process_collector.PROCESS_COLLECTOR
            stats = collector.collect()

            for stat in stats:
                if stat.name == 'process_resident_memory_bytes':
                    a_client_stats.resident_memory_bytes = stat.samples[0].value

                elif stat.name == 'process_start_time_seconds':
                    a_client_stats.start_time_seconds = stat.samples[0].value

                elif stat.name == 'process_cpu_seconds':
                    a_client_stats.cpu_seconds_total = stat.samples[0].value

        return a_client_stats

    def send_events(self):

        try:
            result = self.master_connector.send_events(p_hostname=self._host_name,
                                                       p_events=self._event_handler.get_outgoing_events(),
                                                       p_client_stats=self.get_client_stats())
            self._time_last_successful_send_events = tools.get_current_time()

            if self._could_not_send:
                self.queue_artificial_activation_events()
                self._could_not_send = False

            if result is not None:
                self._event_handler.receive_events(p_json_data=result)

        except Exception as e:

            fmt = "Exception '{estr}' while sending events to master"
            self._logger.error(fmt.format(estr=str(e)))

            self._could_not_send = True

            if self._debug_mode:
                fmt = "Propagating exception due to debug_mode=True"
                self._logger.warn(fmt)
                raise e

    def receive_client_stats(self, p_json_data):

        return tools.objectify_dict(p_dict=p_json_data, p_class=client_stats.ClientStats)

    def handle_downtime(self, p_downtime):

        for process_handler in self._process_handlers.values():
            events = process_handler.get_downtime_corrected_admin_events(p_downtime=p_downtime)

            self._event_handler.queue_events(p_events=events, p_to_master=True)

    def get_user_status(self, p_username):

        user = self.user_entity_manager.user_map(p_session_context=SessionContext(self.persistence)).get(
            p_username)

        if user is not None and user.active:
            return self._user_status.get(p_username)

        else:
            return None

    def add_monitored_user(self, p_username):

        if not p_username in self._usernames:
            self._usernames_not_found.append(p_username)
            fmt = "Adding new monitored user '{username}'"
            self._logger.info(fmt.format(username=p_username))

    def add_new_user(self, p_session_context, p_username, p_locale=None):

        self.user_entity_manager.add_new_user(p_session_context=p_session_context, p_username=p_username,
                                              p_locale=p_locale)
        self.add_monitored_user(p_username=p_username)
        self.send_config_to_all_slaves()
