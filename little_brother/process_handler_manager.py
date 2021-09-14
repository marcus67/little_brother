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
import os.path
import socket

from little_brother import admin_event
from little_brother import dependency_injection
from little_brother import process_info
from little_brother.admin_data_handler import AdminDataHandler
from little_brother.admin_event import AdminEvent
from little_brother.api.master_connector import MasterConnector
from little_brother.app_control_config_model import AppControlConfigModel
from little_brother.event_handler import EventHandler
from little_brother.language import Language
from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn
from little_brother.persistence.session_context import SessionContext
from little_brother.process_handler import ProcessHandler
from little_brother.prometheus import PrometheusClient
from little_brother.rule_handler import RuleResultInfo
from little_brother.user_locale_handler import UserLocaleHandler
from little_brother.user_manager import UserManager
from python_base_app import log_handling

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


class ProcessHandlerManager(PersistenceDependencyInjectionMixIn):

    def __init__(self,
                 p_config,
                 p_is_master,
                 p_login_mapping,
                 p_language:Language,
                 p_process_handlers=None):

        super().__init__()

        self._logger = log_handling.get_logger(self.__class__.__name__)

        self._config: AppControlConfigModel = p_config
        self._is_master = p_is_master
        self._process_handlers = p_process_handlers
        self._login_mapping = p_login_mapping
        self._language = p_language

        self._event_handler = None
        self._rule_handler = None
        self._master_connector = None
        self._prometheus_client = None
        self._user_manager = None

        self._user_locale_handler = UserLocaleHandler()
        self._admin_data_handler = None

        if self._config.hostname is None:
            self._host_name = socket.getfqdn()

        else:
            self._host_name = self._config.hostname

        self._process_regex_map = None
        self._prohibited_process_regex_map = None

        self._locale_dir = os.path.join(os.path.dirname(__file__), "translations")

        self._logout_warnings = {}

    @property
    def admin_data_handler(self) -> AdminDataHandler:

        if self._admin_data_handler is None:
            self._admin_data_handler = dependency_injection.container[AdminDataHandler]

        return self._admin_data_handler

    @property
    def prometheus_client(self) -> PrometheusClient:

        if self._prometheus_client is None:
            self._prometheus_client = dependency_injection.container[PrometheusClient]

        return self._prometheus_client

    @property
    def master_connector(self) -> MasterConnector:

        if self._master_connector is None:
            self._master_connector = dependency_injection.container[MasterConnector]

        return self._master_connector

    @property
    def event_handler(self) -> EventHandler:

        if self._event_handler is None:
            self._event_handler = dependency_injection.container[EventHandler]

        return self._event_handler

    @property
    def user_manager(self) -> UserManager:

        if self._user_manager is None:
            self._user_manager = dependency_injection.container[UserManager]

        return self._user_manager

    @property
    def process_regex_map(self):

        with SessionContext(p_persistence=self.persistence) as session_context:
            if self._process_regex_map is None:
                self._process_regex_map = {}

                for user in self.user_entity_manager.users(session_context):
                    self._process_regex_map[user.username] = user.regex_process_name_pattern

        return self._process_regex_map

    @property
    def prohibited_process_regex_map(self):

        with SessionContext(p_persistence=self.persistence) as session_context:
            if self._prohibited_process_regex_map is None:
                self._prohibited_process_regex_map = {}

                for user in self.user_entity_manager.users(session_context):
                    self._prohibited_process_regex_map[user.username] = user.regex_prohibited_process_name_pattern

        return self._prohibited_process_regex_map

    def reset_process_patterns(self):
        self._process_regex_map = None
        self._prohibited_process_regex_map = None

    def register_events(self):
        self.event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_PROHIBITED_PROCESS, p_handler=self.handle_event_prohibited_process)
        self.event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_PROCESS_START, p_handler=self.handle_event_process_start)
        self.event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_PROCESS_DOWNTIME, p_handler=self.handle_event_process_downtime)
        self.event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_PROCESS_END, p_handler=self.handle_event_process_end)
        self.event_handler.register_event_handler(
            p_event_type=admin_event.EVENT_TYPE_KILL_PROCESS, p_handler=self.handle_event_kill_process)

    def get_process_handler(self, p_id:str, p_raise_exception=False):

        handler = self._process_handlers.get(p_id)

        if handler is None and p_raise_exception:
            fmt = "Unknown process handler '{handler_id}'"
            raise RuntimeError(fmt.format(handler_id=p_id))

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

        if self._is_master:
            rule_result_info = self.admin_data_handler.get_current_rule_result_info(
                p_reference_time=datetime.datetime.now(), p_process_infos=self.get_process_infos(),
                p_username=p_event.username)

            if rule_result_info is not None and rule_result_info.activity_allowed():
                with SessionContext(p_persistence=self.persistence) as session_context:

                    if rule_result_info.limited_session_time():
                        self.user_manager.issue_notification(
                            p_session_context=session_context,
                            p_username=p_event.username,
                            p_message=self._language.get_text_limited_session_start(p_locale=rule_result_info.locale,
                                                                                    p_variables=rule_result_info.args))
                    else:
                        self.user_manager.issue_notification(
                            p_session_context=session_context,
                            p_username=p_event.username,
                            p_message=self._language.get_text_unlimited_session_start(p_locale=rule_result_info.locale,
                                                                                      p_variables=rule_result_info.args))

    def handle_event_prohibited_process(self, p_event:AdminEvent):

        process_handler = self.get_process_handler(p_id=p_event.processhandler)

        if process_handler is None:
            msg = "Received event for process handler of type id '{id}' which is not registered -> discarding event"
            self._logger.warning(msg.format(id=p_event.processhandler))
            return

        if self._is_master:
            rule_result_info = self.admin_data_handler.get_current_rule_result_info(
                p_reference_time=datetime.datetime.now(), p_process_infos=self.get_process_infos(),
                p_username=p_event.username)

            if rule_result_info is not None and rule_result_info.activity_allowed():
                with SessionContext(p_persistence=self.persistence) as session_context:

                    variables = rule_result_info.args
                    variables['process_name'] = p_event.processname

                    self.user_manager.issue_notification(
                        p_session_context=session_context,
                        p_username=p_event.username,
                        p_message=self._language.get_text_prohibited_process(p_locale=rule_result_info.locale,
                                                                             p_variables=variables))

                    self.queue_event_kill_process(
                        p_hostname=p_event.hostname,
                        p_username=p_event.username,
                        p_processhandler=process_handler.id,
                        p_pid=p_event.pid,
                        p_process_start_time=p_event.process_start_time,
                        p_delay=0)

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

    def scan_processes(self, p_process_handler:ProcessHandler, p_reference_time=None, p_queue_events=True):  # @DontTrace

        if p_reference_time is None:
            p_reference_time = datetime.datetime.now()

        with SessionContext(p_persistence=self.persistence) as session_context:
            events = p_process_handler.scan_processes(
                p_session_context=session_context,
                p_server_group=self._config.server_group, p_login_mapping=self._login_mapping,
                p_host_name=self._host_name,
                p_process_regex_map=self.process_regex_map,
                p_prohibited_process_regex_map=self.prohibited_process_regex_map,
                p_reference_time=p_reference_time)

            if p_queue_events:
                self.event_handler.queue_events(p_events=events, p_to_master=True)

                if not self._is_master:
                    self.event_handler.queue_events_locally(p_events=events)

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
            if pinfo.end_time is None and pinfo.hostname != self._host_name:
                self.queue_event_historic_process_start(p_pinfo=pinfo)
                counter = counter + 1

        fmt = "Sent %d historic process infos to slaves" % counter
        self._logger.info(fmt)

    def queue_event_historic_process_start(self, p_pinfo):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_PROCESS_START,
            p_hostname=p_pinfo.hostname,
            p_pid=p_pinfo.pid,
            p_username=p_pinfo.username,
            p_process_start_time=p_pinfo.start_time)
        self.event_handler.queue_event(p_event=event, p_is_action=True)

    def queue_artificial_activation_events(self):

        for handler in self._process_handlers.values():
            events = handler.get_artificial_activation_events()

            fmt = "Artificially activating {process_count} active processes on handler {handler_id}"
            self._logger.info(fmt.format(process_count=len(events), handler_id=handler.id))

            self.event_handler.queue_events(p_events=events, p_to_master=True)

    def queue_artificial_kill_events(self):

        for handler in self._process_handlers.values():
            events = handler.get_artificial_kill_events()

            fmt = "Artificially killing {process_count} active processes on handler {handler_id}"
            self._logger.info(fmt.format(process_count=len(events), handler_id=handler.id))

            self.event_handler.queue_events(p_events=events, p_to_master=False)

    def queue_event_kill_process(self, p_hostname, p_username, p_processhandler, p_pid, p_process_start_time,
                                 p_delay=None):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_KILL_PROCESS,
            p_hostname=p_hostname,
            p_username=p_username,
            p_processhandler=p_processhandler,
            p_pid=p_pid,
            p_process_start_time=p_process_start_time,
            p_delay=p_delay if p_delay is not None else self._config.kill_process_delay)
        self.event_handler.queue_event(p_event=event, p_is_action=True)

    def handle_downtime(self, p_downtime):

        for process_handler in self._process_handlers.values():
            events = process_handler.get_downtime_corrected_admin_events(p_downtime=p_downtime)

            self.event_handler.queue_events(p_events=events, p_to_master=True)

    def check_issue_logout_warning(self, p_username, p_rule_result_info: RuleResultInfo):

        issue_warning = False
        notification = None

        current_warning = self._logout_warnings.get(p_username)

        if p_rule_result_info.approaching_logout_rules > 0:
            if current_warning is None or p_rule_result_info.get_minutes_left_in_session() != current_warning:
                issue_warning = True
                self._logout_warnings[p_username] = p_rule_result_info.get_minutes_left_in_session()
                notification = self._language.pick_text_for_approaching_logout(p_rule_result_info=p_rule_result_info)

        elif current_warning is not None:
            self._logout_warnings[p_username] = None
            issue_warning = True

        if issue_warning:
            with SessionContext(p_persistence=self.persistence) as session_context:
                self.user_manager.issue_notification(p_session_context=session_context,
                                                     p_username=p_username, p_message=notification)

    def reset_logout_warning(self, p_username):

        if p_username in self._logout_warnings:
            del self._logout_warnings[p_username]

    def handle_rule_result_info(self, p_rule_result_info, p_stat_info, p_user):

        if p_rule_result_info.activity_allowed():
            self.check_issue_logout_warning(p_username=p_user.username, p_rule_result_info=p_rule_result_info)

        else:
            fmt = "Process %s" % str(p_rule_result_info.effective_rule_set)
            self._logger.debug(fmt)

            for (hostname, processes) in p_stat_info.currently_active_host_processes.items():

                fmt = "User %s has %d active process(es) on host %s" % (
                    p_user.username, len(processes), hostname)
                self._logger.debug(fmt)

                process_killed = False

                for processhandler_id, pid, process_start_time in processes:
                    processhandler = self._process_handlers.get(processhandler_id)

                    if processhandler is not None and processhandler.can_kill_processes():
                        if self.prometheus_client is not None:
                            self.prometheus_client.count_forced_logouts(p_username=p_user.username)

                        self.queue_event_kill_process(
                            p_hostname=hostname,
                            p_username=p_user.username,
                            p_processhandler=processhandler_id,
                            p_pid=pid,
                            p_process_start_time=process_start_time)
                        process_killed = True

                if process_killed:
                    with SessionContext(p_persistence=self.persistence) as session_context:
                        self.user_manager.issue_notification(
                            p_session_context=session_context,
                            p_username=p_user.username,
                            p_message=self._language.pick_text_for_ruleset(p_rule_result_info=p_rule_result_info))

                    self.reset_logout_warning(p_username=p_user.username)
