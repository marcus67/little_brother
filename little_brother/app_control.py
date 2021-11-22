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
import socket
import sys
import time

import prometheus_client

from little_brother import admin_event
from little_brother import client_stats
from little_brother import constants
from little_brother import dependency_injection
from little_brother import process_statistics
from little_brother import rule_override
from little_brother import settings
from little_brother.admin_data_handler import AdminDataHandler
from little_brother.api.master_connector import MasterConnector
from little_brother.app_control_config_model import AppControlConfigModel
from little_brother.client_info import ClientInfo
from little_brother.event_handler import EventHandler
from little_brother.language import Language
from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn
from little_brother.persistence.persistent_user import User
from little_brother.persistence.session_context import SessionContext
from little_brother.process_handler_manager import ProcessHandlerManager
from little_brother.prometheus import PrometheusClient
from little_brother.rule_handler import RuleHandler
from little_brother.user_locale_handler import UserLocaleHandler
from little_brother.user_manager import UserManager
from python_base_app import log_handling
from python_base_app import tools
from python_base_app.base_user_handler import BaseUserHandler

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
                 p_login_mapping=None,
                 p_locale_helper=None):

        super().__init__()

        self._logger = log_handling.get_logger(self.__class__.__name__)

        self._config: AppControlConfigModel = p_config
        self._debug_mode = p_debug_mode
        self._process_handlers = p_process_handlers
        self._device_handler = p_device_handler

        self._rule_handler = None
        self._notification_handlers = p_notification_handlers
        self._master_connector = None
        self._prometheus_client = None
        self._user_handler = None
        self._locale_helper = p_locale_helper
        self._time_last_successful_send_events = tools.get_current_time()
        self._user_locale_handler = UserLocaleHandler()
        self._admin_data_handler = None
        self._process_regex_map = None

        if self._config.hostname is None:
            self._host_name = socket.getfqdn()

        else:
            self._host_name = self._config.hostname

        self._event_handler = EventHandler(p_host_name=self._host_name, p_is_master=self.is_master())
        dependency_injection.container[EventHandler] = self._event_handler

        self._event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_START_CLIENT, p_handler=self.handle_event_start_client)
        self._event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_START_MASTER, p_handler=self.handle_event_start_master)
        self._event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_UPDATE_CONFIG, p_handler=self.handle_event_update_config)

        self._language = Language()

        self._process_handler_manager = ProcessHandlerManager(
            p_config=self._config, p_process_handlers=self._process_handlers, p_is_master=self.is_master(),
            p_login_mapping=p_login_mapping, p_language=self._language)

        dependency_injection.container[ProcessHandlerManager] = self._process_handler_manager

        self._user_manager = UserManager(p_config=self._config,
                                         p_login_mapping=p_login_mapping,
                                         p_server_group=self._config.server_group,
                                         p_is_master=self.is_master())
        dependency_injection.container[UserManager] = self._user_manager

        with SessionContext(p_persistence=self.persistence) as session_context:
            self._user_manager.reset_users(p_session_context=session_context)

        self._could_not_send = False
        self._client_infos = {}
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

    @property
    def user_handler(self) -> BaseUserHandler:

        if self._user_handler is None:
            self._user_handler = dependency_injection.container[BaseUserHandler]

        return self._user_handler

    @property
    def prometheus_client(self) -> PrometheusClient:

        if self._prometheus_client is None:
            self._prometheus_client = dependency_injection.container[PrometheusClient]

        return self._prometheus_client

    @property
    def check_interval(self):
        return self._config.check_interval

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
                user.prohibited_process_name_pattern = user_config.get(constants.JSON_PROHIBITED_PROCESS_NAME_PATTERN)
                user.active = user_config[constants.JSON_ACTIVE]

                fmt = "Set config for {user}"
                self._logger.info(fmt.format(user=str(user)))

            session.commit()
            self._user_manager.reset_users(p_session_context=session_context)
            self._process_handler_manager.reset_process_patterns()

    @property
    def process_regex_map(self):

        with SessionContext(p_persistence=self.persistence) as session_context:
            if self._process_regex_map is None:
                self._process_regex_map = {}

                for user in self.user_entity_manager.users(session_context):
                    self._process_regex_map[user.username] = user.regex_process_name_pattern

        return self._process_regex_map

    def is_master(self):

        if self.master_connector is None:
            # This is for test cases which do not instantiate a master connector
            return True

        else:
            return self.master_connector._config.host_url is None

    def set_prometheus_http_requests_summary(self, p_hostname, p_service, p_duration):

        if self.prometheus_client is not None:
            # try to resolve ip addresses
            p_hostname = tools.get_dns_name_by_ip_address(p_ip_address=p_hostname)
            self.prometheus_client.set_http_requests_summary(p_hostname=p_hostname,
                                                              p_service=p_service,
                                                              p_duration=p_duration)

    def set_metrics(self):

        with SessionContext(p_persistence=self.persistence) as session_context:
            if self.prometheus_client is not None:
                self.prometheus_client.set_uptime(p_hostname="master", p_uptime=time.time() - self._start_time)

                self.prometheus_client.set_number_of_monitored_users(
                    self._user_manager.get_number_of_monitored_users())
                self.prometheus_client.set_number_of_configured_users(
                    len(self.user_entity_manager.user_map(session_context)))

                if self._config.scan_active:
                    self.prometheus_client.set_monitored_host(self._host_name, True)

                latest_ping_time = tools.get_current_time() + \
                                   datetime.timedelta(seconds=-self._config.maximum_client_ping_interval)

                for hostname, client_info in self._client_infos.items():
                    active = client_info.last_message > latest_ping_time
                    self.prometheus_client.set_monitored_host(hostname, active)

                if self._device_handler is not None:
                    self.prometheus_client.set_number_of_monitored_devices(
                        self._device_handler.get_number_of_monitored_devices())

                    for device_info in self._device_handler.device_infos.values():
                        self.prometheus_client.set_device_active(
                            device_info.device_name, 1 if device_info.is_up else 0)
                        self.prometheus_client.set_device_response_time(
                            device_info.device_name, device_info.response_time)
                        self.prometheus_client.set_device_moving_average_response_time(
                            device_info.device_name, device_info.moving_average_response_time)

                else:
                    self.prometheus_client.set_number_of_monitored_devices(0)

                for client_info in self._client_infos.values():
                    if client_info.client_stats is not None:
                        self.prometheus_client.set_client_stats(p_hostname=client_info.host_name,
                                                                 p_client_stats=client_info.client_stats)

    def check(self):

        self._user_manager.retrieve_user_mappings()

        reference_time = datetime.datetime.now()

        self._event_handler.process_queue()

        if self.is_master():
            self.process_rule_sets_for_all_users(p_reference_time=reference_time)
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
            self._process_handler_manager.queue_artificial_kill_events()

    def start(self):

        if self.is_master():
            fmt = "Starting application in MASTER mode"
            self._logger.info(fmt)

            self._process_handler_manager.load_historic_process_infos()
            self._process_handler_manager.send_historic_process_infos()
            self.admin_data_handler.load_rule_overrides()
        #             self.queue_broadcast_event_start_master()

        else:
            fmt = "Starting application in SLAVE mode communicating with master at URL {master_url}"
            self._logger.info(fmt.format(master_url=self.master_connector._get_api_url()))

            self.queue_event_start_client()

        fmt = "Using fully qualified domain name '%s' for process infos" % self._host_name
        self._logger.info(fmt)

        self._process_handler_manager.register_events()
        self._user_manager.register_events()

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

    def handle_event_update_config(self, p_event):

        if constants.JSON_USER_CONFIG in p_event.payload:
            # New mode (version >= 0.3.13)
            user_config_payload = p_event.payload[constants.JSON_USER_CONFIG]
            self._config.maximum_time_without_send_events = p_event.payload.get(
                constants.JSON_MAXIMUM_TIME_WITHOUT_SEND)

        else:
            # Compatibility mode (version < 0.3.13)
            user_config_payload = p_event.payload

        user_configs = {}

        for username, user_config in user_config_payload.items():
            user_configs[username] = user_config

        self.set_user_configs(p_user_configs=user_configs)

    def update_client_info(self, p_hostname, p_client_stats=None, p_suppress_send_state_update=False):

        client_info = self._client_infos.get(p_hostname)

        if client_info is None:
            client_info = ClientInfo(p_host_name=p_hostname, p_client_stats=p_client_stats, p_is_master=False,
                                     p_maximum_client_ping_interval=self._config.maximum_client_ping_interval,
                                     p_master_version=self.get_client_version(),
                                     )
            self._client_infos[p_hostname] = client_info
            self.send_config_to_slave(p_hostname)
            self._user_manager.send_login_mapping_to_slave(p_hostname)

        client_info.last_message = tools.get_current_time()
        client_info.client_stats = p_client_stats

    def handle_event_start_client(self, p_event):

        self.update_client_info(p_event.hostname, p_suppress_send_state_update=True)
        self.send_config_to_slave(p_event.hostname)
        self._user_manager.send_login_mapping_to_slave(p_event.hostname)
        self._process_handler_manager.send_historic_process_infos()

    def handle_event_start_master(self, p_event):

        self._process_handler_manager.queue_artificial_activation_events()

    def send_config_to_slave(self, p_hostname):

        config = {}

        with SessionContext(p_persistence=self.persistence) as session_context:
            user_config = {
                user.username: {constants.JSON_PROCESS_NAME_PATTERN: user.process_name_pattern,
                                constants.JSON_PROHIBITED_PROCESS_NAME_PATTERN: user.prohibited_process_name_pattern,
                                constants.JSON_ACTIVE: user.active}
                for user in self.user_entity_manager.users(p_session_context=session_context)
            }

        config[constants.JSON_USER_CONFIG] = user_config
        config[constants.JSON_MAXIMUM_TIME_WITHOUT_SEND] = self._config.maximum_time_without_send_events

        self.queue_event_update_config(p_hostname=p_hostname, p_config=config)

    def send_config_to_all_slaves(self):

        for client in self._client_infos.values():
            self.send_config_to_slave(p_hostname=client.host_name)

    def process_rule_sets_for_all_users(self, p_reference_time):

        fmt = "Processing rules for all users START..."
        self._logger.debug(fmt)

        with SessionContext(p_persistence=self.persistence) as session_context:
            users_stat_infos = process_statistics.get_process_statistics(
                p_process_infos=self._process_handler_manager.get_process_infos(),
                p_reference_time=p_reference_time,
                p_max_lookback_in_days=self._config.process_lookback_in_days,
                p_user_map=self.user_entity_manager.user_map(session_context),
                p_min_activity_duration=self._config.min_activity_duration)

            active_time_extensions = self.time_extension_entity_manager.get_active_time_extensions(
                p_session_context=session_context, p_reference_datetime=tools.get_current_time())

            for user in self.user_entity_manager.users(session_context):
                if user.active and user.username in self._user_manager.usernames:

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

                            rule_result_info = self.rule_handler.process_rule_sets_for_user(
                                p_rule_sets=user.rulesets,
                                p_stat_info=stat_info,
                                p_active_time_extension=active_time_extensions.get(user.username),
                                p_reference_time=p_reference_time,
                                p_rule_override=override,
                                p_locale=user_locale)

                            self.update_current_user_status(rule_result_info, session_context, stat_info, user)
                            self._process_handler_manager.handle_rule_result_info(rule_result_info, stat_info, user)
                            user_active = stat_info.current_activity is not None

                    if self.prometheus_client is not None:
                        self.prometheus_client.set_user_active(p_username=user.username, p_is_active=user_active)

        fmt = "Processing rules for all users END..."
        self._logger.debug(fmt)

    def update_current_user_status(self, p_rule_result_info, p_session_context, p_stat_info, p_user):
        current_user_status = self._user_manager.get_current_user_status(
            p_session_context=p_session_context, p_username=p_user.username)

        if p_stat_info.current_activity_start_time is not None and \
                p_rule_result_info.limited_session_time():
            current_user_status.minutes_left_in_session = \
                p_rule_result_info.get_minutes_left_in_session()

        else:
            current_user_status.minutes_left_in_session = None

        current_user_status.activity_allowed = p_rule_result_info.activity_allowed()
        current_user_status.logged_in = p_stat_info.current_activity is not None

    ###################################################################################################################
    ###################################################################################################################
    ###################################################################################################################

    def queue_event_start_client(self):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_START_CLIENT,
            p_hostname=self._host_name)
        self._event_handler.queue_event(p_event=event, p_to_master=True)

    def queue_broadcast_event_start_master(self):

        for hostname, client_info in self._client_infos.items():
            if not client_info.start_event_sent:
                event = admin_event.AdminEvent(
                    p_event_type=admin_event.EVENT_TYPE_START_MASTER,
                    p_hostname=hostname)
                self._event_handler.queue_event(p_event=event, p_is_action=True)
                client_info.start_event_sent = True

    def queue_event_update_config(self, p_hostname, p_config):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_UPDATE_CONFIG,
            p_hostname=p_hostname,
            p_payload=p_config)
        self._event_handler.queue_event(p_event=event, p_is_action=True)

    def queue_event_historic_process_start(self, p_pinfo):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_PROCESS_START,
            p_hostname=p_pinfo.hostname,
            p_pid=p_pinfo.pid,
            p_username=p_pinfo.username,
            p_process_start_time=p_pinfo.start_time)
        self._event_handler.queue_event(p_event=event, p_is_action=True)

    def get_unmonitored_users(self, p_session_context):

        return [username for username in self.user_handler.list_users() if
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
            p_running_in_docker=tools.running_in_docker(),
            p_running_in_snap=tools.running_in_snap()
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

        outgoing_events = self._event_handler.get_outgoing_events()

        try:
            fmt = "Sending {number} event(s) to master"
            self._logger.debug(fmt.format(number=len(outgoing_events)))
            result = self.master_connector.send_events(p_hostname=self._host_name,
                                                       p_events=outgoing_events,
                                                       p_client_stats=self.get_client_stats())
            self._time_last_successful_send_events = tools.get_current_time()

            if self._could_not_send:
                self._process_handler_manager.queue_artificial_activation_events()
                self._could_not_send = False

            if result is not None:
                self._event_handler.receive_events(p_json_data=result)

        except Exception as e:

            fmt = "Exception '{estr}' while sending events to master. Requeueing events..."
            self._logger.error(fmt.format(estr=str(e)))
            self._event_handler.queue_outgoing_events(p_events=outgoing_events)

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

    def add_new_user(self, p_session_context, p_username, p_locale=None):

        self.user_entity_manager.add_new_user(p_session_context=p_session_context, p_username=p_username,
                                              p_locale=p_locale)
        self._user_manager.add_monitored_user(p_username=p_username)
        self.send_config_to_all_slaves()
