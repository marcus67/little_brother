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

import datetime
import gettext
import locale
import pwd
import queue
import re
import socket

from python_base_app import configuration
from python_base_app import log_handling
from python_base_app import tools
from python_base_app import view_info

from little_brother import admin_event
from little_brother import constants, process_statistics
from little_brother import german_vacation_context_rule_handler
from little_brother import login_mapping
from little_brother import process_info
from little_brother import rule_handler
from little_brother import rule_override
from little_brother import simple_context_rule_handlers
from little_brother import user_status


DEFAULT_SCAN_ACTIVE = True
DEFAULT_ADMIN_LOOKAHEAD_IN_DAYS = 7  # days
DEFAULT_PROCESS_LOOKUP_IN_DAYS = 7  # days
DEFAULT_MIN_ACTIVITY_DURATION = 60  # seconds
DEFAULT_CHECK_INTERVAL = 5  # seconds
DEFAULT_LOCALE = "en_US"

SECTION_NAME = "AppControl"

# Dummy function to trigger extraction by pybabel...
_ = lambda x, y=None: x


class AppControlConfigModel(configuration.ConfigModel):

    def __init__(self):
        super(AppControlConfigModel, self).__init__(p_section_name=SECTION_NAME)

        self.process_lookback_in_days = DEFAULT_PROCESS_LOOKUP_IN_DAYS
        self.admin_lookahead_in_days = DEFAULT_ADMIN_LOOKAHEAD_IN_DAYS
        self.server_group = login_mapping.DEFAULT_SERVER_GROUP
        self.hostname = configuration.NONE_STRING
        self.scan_active = DEFAULT_SCAN_ACTIVE
        self.check_interval = DEFAULT_CHECK_INTERVAL
        self.min_activity_duration = DEFAULT_MIN_ACTIVITY_DURATION
        self.user_mappings = [configuration.NONE_STRING]


class ClientInfo(object):

    def __init__(self, p_host_name):
        self.host_name = p_host_name
        self.last_message = None


class AppControl(object):

    def __init__(self, p_config,
                 p_debug_mode,
                 p_process_handlers,
                 p_persistence,
                 p_rule_handler,
                 p_notification_handlers,
                 p_master_connector,
                 p_rule_set_configs,
                 p_login_mapping=None):

        if p_login_mapping is None:
            p_login_mapping = login_mapping.LoginMapping()

        self._config = p_config
        self._debug_mode = p_debug_mode
        self._process_handlers = p_process_handlers
        self._persistence = p_persistence
        self._rule_handler = p_rule_handler
        self._notification_handlers = p_notification_handlers
        self._master_connector = p_master_connector

        self._logger = log_handling.get_logger(self.__class__.__name__)

        self._usernames_not_found = []
        self._usernames = []
        self._process_regex_map = None
        # self._uid_map = {}
        # self._username_map = p_login_mapping
        self._login_mapping = login_mapping.LoginMapping(p_default_server_group=self._config.server_group)

        self._logout_warnings = {}

        if self._rule_handler is not None:
            self.register_rule_context_handlers()

        self.set_rule_set_configs(p_rule_set_configs=p_rule_set_configs)

        fmt = "Watching usernames: %s" % ",".join(self._usernames)
        self._logger.info(fmt)

        self._event_queue = queue.Queue()
        self._outgoing_events = []
        self._could_not_send = False

        self._client_infos = {}
        self._rule_overrides = {}
        self._user_status = {}

        if self._config.hostname is None:
            self._host_name = socket.getfqdn()

        else:
            self._host_name = self._config.hostname

        self.init_labels_and_notifications()

    @property
    def check_interval(self):
        return self._config.check_interval

    def init_labels_and_notifications(self):

        self.history_labels = [(_('{days} days ago'), {"days": day}) for day in
                               range(0, self._config.process_lookback_in_days + 1)]

        self.history_labels[0] = (_('Today'), {"days": 0})
        self.history_labels[1] = (_('Yesterday'), {"days": 1})

        self.text_no_time_left = _("{user}, you do not have computer time left today. You will be logged out.")
        self.text_no_time_left_approaching = _(
            "{user}, you only have {minutes_left_before_logout} minutes left today. Please, log out.")
        self.text_no_time_today = _("{user}, you do not have any computer time today. You will be logged out.")
        self.text_too_early = _("{user}, it is too early to use the computer. You will be logged out.")
        self.text_too_late = _("{user}, it is too late to use the computer. You will be logged out.")
        self.text_too_late_approaching = _(
            "{user}, in {minutes_left_before_logout} minutes it will be too late to use the computer. Please, log out.")
        self.text_need_break = _("{user}, you have to take a break. You will be logged out.")
        self.text_need_break_approaching = _(
            "{user}, in {minutes_left_before_logout} minutes you will have to take a break. Please, log out.")
        self.text_min_break = _(
            "{user}, your break will only be over in {break_minutes_left} minutes. You will be logged out.")
        self.text_limited_session_start = _(
            "Hello {user}, you will be allowed to play for {minutes_left_in_session} minutes in this session.")
        self.text_unlimited_session_start = _("Hello {user}, you have unlimited playtime in this session.")

    def register_rule_context_handlers(self):

        self._rule_handler.register_context_rule_handler(simple_context_rule_handlers.DefaultContextRuleHandler(),
                                                         p_default=True)
        self._rule_handler.register_context_rule_handler(simple_context_rule_handlers.WeekdayContextRuleHandler())
        self._rule_handler.register_context_rule_handler(
            german_vacation_context_rule_handler.GermanVacationContextRuleHandler())

    def set_rule_set_configs(self, p_rule_set_configs):

        self._rule_set_configs = p_rule_set_configs
        self._process_regex_map = None
        self._usernames_not_found.extend(p_rule_set_configs.keys())

    @property
    def process_regex_map(self):

        if self._process_regex_map is None:
            self._process_regex_map = {}

            for username, ruleset_configs in self._rule_set_configs.items():
                pattern = "(%s)" % ")|(".join(
                    [ruleset_config.process_name_pattern for ruleset_config in ruleset_configs])
                self._process_regex_map[username] = re.compile(pattern)

        return self._process_regex_map

    def retrieve_user_mappings(self):

        if len(self._usernames_not_found) > 0:

            usernames_found = []

            for username in self._usernames_not_found:
                try:
                    uid = self._login_mapping.get_uid_by_login(p_server_group=self._config.server_group,
                                                               p_login=username)

                    if uid is None:
                        user = pwd.getpwnam(username)
                        uid = user.pw_uid
                        new_entry = login_mapping.LoginUidMappingEntry(username, uid)
                        self._login_mapping.add_entry(p_server_group=self._config.server_group,
                                                      p_login_uid_mapping_entry=new_entry)

                    usernames_found.append(username)
                    self._usernames.append(username)

                    fmt = "Found user information for user '{user}': UID={uid}"
                    self._logger.info(fmt.format(user=username, uid=uid))

                except KeyError:
                    fmt = "Cannot find user information for user '{user}', will retry later..."
                    self._logger.warning(fmt.format(user=username))

            for username in usernames_found:
                self._usernames_not_found.remove(username)

            if len(self._usernames_not_found) == 0:
                fmt = "Retrieved user information for all {user_count} users"
                self._logger.info(fmt.format(user_count=len(self._usernames)))

    def is_master(self):

        return self._master_connector._config.host_url is None

    def check(self):

        self.retrieve_user_mappings()

        reference_time = datetime.datetime.now()

        self.process_queue()

        if self.is_master():
            self.process_rules(p_reference_time=reference_time)
            self.process_queue()

        else:
            self.send_events()
            self.process_queue()

    def start(self):

        if self.is_master():
            fmt = "Starting application in MASTER mode"
            self._logger.info(fmt)

            self.load_historic_process_infos()
            self.send_historic_process_infos()
            self.load_rule_overrides()
        #             self.queue_broadcast_event_start_master()

        else:
            fmt = "Starting application in SLAVE mode communication with master at URL {master_url}"
            self._logger.info(fmt.format(master_url=self._master_connector._get_api_url()))

            self.queue_event_start_client()

        fmt = "Using fully qualified domain name '%s' for process infos" % self._host_name
        self._logger.info(fmt)

    def stop(self):

        for handler in self._process_handlers.values():
            events = handler.get_artificial_termination_events()

            fmt = "Artificially terminating {process_count} active processes on {handler_id}"
            self._logger.info(fmt.format(process_count=len(events), handler_id=handler.id))

            self.queue_events(p_events=events, p_to_master=True)

        self.process_queue()

        if not self.is_master():
            self.send_events()

    def queue_event(self, p_event, p_to_master=False, p_is_action=False):

        if p_is_action:
            if p_event.hostname == self._host_name:
                self.queue_event_locally(p_event=p_event)

            else:
                self.queue_event_for_send(p_event=p_event)

        else:
            if p_to_master == self.is_master():
                self.queue_event_locally(p_event=p_event)

            else:
                self.queue_event_for_send(p_event=p_event)

    def queue_event_locally(self, p_event):

        fmt = "Queue locally: {event}"
        self._logger.debug(fmt.format(event=p_event))

        self._event_queue.put(p_event)

    def queue_event_for_send(self, p_event):

        if p_event in self._outgoing_events:
            fmt = "Already in outgoing queue: {event}"
            self._logger.info(fmt.format(event=p_event))
            return

        fmt = "Queue for send: {event}"
        self._logger.debug(fmt.format(event=p_event))

        self._outgoing_events.append(p_event)

    def queue_events(self, p_events, p_to_master=False, p_is_action=False):

        for event in p_events:
            self.queue_event(p_event=event, p_to_master=p_to_master, p_is_action=p_is_action)

    def queue_events_locally(self, p_events):

        for event in p_events:
            self.queue_event_locally(p_event=event)

    def queue_outgoing_event(self, p_event):

        self._outgoing_events.append(p_event)

    def get_process_handler(self, p_id, p_raise_exception=False):

        handler = self._process_handlers.get(p_id)

        if handler is None and p_raise_exception:
            fmt = "Unknown process handler '{handler_id}'"
            raise Exception(fmt.format(handler_id=p_id))

        return handler

    def handle_event_process_downtime(self, p_event):

        pinfo, updated = self.get_process_handler(p_id=p_event.processhandler).handle_event_process_downtime(p_event)

        if self._persistence is not None and updated:
            self._persistence.update_process_info(p_process_info=pinfo)

    def handle_event_process_start(self, p_event):

        pinfo, updated = self.get_process_handler(p_id=p_event.processhandler).handle_event_process_start(p_event)

        if updated:
            if self._persistence is not None:
                self._persistence.update_process_info(p_process_info=pinfo)

        else:
            if self._persistence is not None:
                self._persistence.write_process_info(p_process_info=pinfo)

        if self.is_master():
            rule_result_info = self.get_current_rule_result_info(p_reference_time=datetime.datetime.now(),
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

        if self._persistence is not None:
            self._persistence.update_process_info(p_process_info=pinfo)

    def handle_event_kill_process(self, p_event):

        return self.get_process_handler(
            p_id=p_event.processhandler).handle_event_kill_process(p_event, p_server_group=self._config.server_group,
                                                                   p_login_mapping=self._login_mapping)

    def handle_event_speak(self, p_event):

        if p_event.locale is None:
            user_locale = self.get_user_locale(p_username=p_event.username)

        else:
            user_locale = p_event.locale

        for notification_handler in self._notification_handlers:
            notification_handler.notify(p_text=p_event.text, p_locale=user_locale)

    def get_user_locale(self, p_username):

        configs = self._rule_set_configs.get(p_username)

        if configs is not None:
            for rule_set in configs:
                if rule_set.locale is not None:
                    return rule_set.locale

        default_locale = locale.getdefaultlocale()

        if default_locale is not None:
            # The first entry of the tuple is the language code
            # See https://docs.python.org/3.6/library/locale.html
            return default_locale[0]

        return DEFAULT_LOCALE

    def handle_event_update_config(self, p_event):

        rule_set_configs = {}

        for username, json_rulesets in p_event.payload.items():
            rulesets = [tools.objectify_dict(p_dict=json_ruleset, p_class=rule_handler.RuleSetConfigModel)
                        for json_ruleset in json_rulesets]

            rule_set_configs[username] = rulesets

            fmt = "Received rule set config for user {username}"
            self._logger.info(fmt.format(username=username))

        self.set_rule_set_configs(p_rule_set_configs=rule_set_configs)

    def handle_event_update_login_mapping(self, p_event):

        self._login_mapping.from_json(p_json=p_event.payload)

        server_group_names = ', '.join(self._login_mapping.get_server_group_names())
        fmt = "Received login mapping for server group(s) {group_names}"
        self._logger.info(fmt.format(group_names=server_group_names))

    def update_client_info(self, p_event):

        client_info = self._client_infos.get(p_event.hostname)

        if client_info is None:
            client_info = ClientInfo(p_host_name=p_event.hostname)
            self._client_infos[p_event.hostname] = client_info

        client_info.last_message = p_event.event_time

    def handle_event_start_client(self, p_event):

        self.update_client_info(p_event)
        self.send_config_to_slave(p_event.hostname)
        self.send_login_mapping_to_slave(p_event.hostname)
        self.send_historic_process_infos()

    def handle_event_start_master(self):

        self.queue_artificial_activation_events()

    def send_config_to_slave(self, p_hostname):

        config = {
            username: [{constants.JSON_USERNAME: ruleset.username,
                        constants.JSON_PROCESS_NAME_PATTERN: ruleset.process_name_pattern
                        }
                       for ruleset in rulesets
                       ]
            for username, rulesets in self._rule_set_configs.items()
        }

        self.queue_event_update_config(p_hostname=p_hostname, p_config=config)

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

        if self._persistence is not None:
            self._persistence.log_admin_event(p_event)

        return new_events

    def process_queue(self):

        while (self._event_queue.qsize() > 0):
            try:
                event = self._event_queue.get(block=False)

            except queue.Empty:
                return

            new_events = self.process_event(p_event=event)

            if new_events is not None:
                self.queue_events(p_events=new_events, p_to_master=True, p_is_action=False)

    def scan_processes(self, p_process_handler, p_reference_time=None, p_queue_events=True):  # @DontTrace

        if p_reference_time is None:
            p_reference_time = datetime.datetime.now()

        events = p_process_handler.scan_processes(
            p_server_group=self._config.server_group, p_login_mapping=self._login_mapping,
            p_host_name=self._host_name,
            p_process_regex_map=self.process_regex_map,
            p_reference_time=p_reference_time)

        if p_queue_events:
            self.queue_events(p_events=events, p_to_master=True)

            if not self.is_master():
                self.queue_events_locally(p_events=events)

    def get_process_infos(self):

        process_infos = {}

        for handler in self._process_handlers.values():
            process_infos.update(handler.process_infos)

        return process_infos

    def load_historic_process_infos(self):

        pinfos = self._persistence.load_process_infos(p_lookback_in_days=self._config.process_lookback_in_days + 1)

        counter_open_end_time = 0

        for pinfo in pinfos:

            if pinfo.end_time is None:
                end_time = None

            else:
                end_time = pinfo.end_time

            new_pinfo = process_info.ProcessInfo(
                p_hostname=pinfo.hostname,
                p_pid=pinfo.pid,
                p_processhandler=pinfo.processhandler,
                p_username=pinfo.username,
                p_processname=pinfo.processname,
                p_start_time=pinfo.start_time,
                p_downtime=pinfo.downtime,
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

    def update_rule_override(self, p_rule_override):

        fmt = "Updating '{override}'"
        self._logger.debug(fmt.format(override=str(p_rule_override)))

        self._rule_overrides[p_rule_override.get_key()] = p_rule_override

        if self._persistence is not None:
            self._persistence.update_rule_override(p_rule_override=p_rule_override)

    def load_rule_overrides(self):

        overrides = self._persistence.load_rule_overrides(p_lookback_in_days=self._config.process_lookback_in_days + 1)

        for override in overrides:
            new_override = rule_override.RuleOverride(
                p_username=override.username,
                p_reference_date=override.reference_date,
                p_max_time_per_day=override.max_time_per_day,
                p_min_time_of_day=override.min_time_of_day,
                p_max_time_of_day=override.max_time_of_day,
                p_min_break=override.min_break,
                p_max_activity_duration=override.max_activity_duration,
                p_free_play=override.free_play)

            self._rule_overrides[new_override.get_key()] = new_override

        fmt = "Loaded %d rule overrides from database looking back %s days" % (
            len(overrides), self._config.process_lookback_in_days)
        self._logger.info(fmt)

    def pick_text_for_ruleset(self, p_rule_result_info, p_text=None):

        t = gettext.translation('messages', localedir='little_brother/translations',
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

        t = gettext.translation('messages', localedir='little_brother/translations',
                                languages=[p_rule_result_info.locale], fallback=True)

        if p_rule_result_info.approaching_logout_rules & rule_handler.RULE_TIME_PER_DAY:
            return t.gettext(self.text_no_time_left_approaching).format(**p_rule_result_info.args)

        elif p_rule_result_info.approaching_logout_rules & rule_handler.RULE_TOO_LATE:
            return t.gettext(self.text_too_late_approaching).format(**p_rule_result_info.args)

        elif p_rule_result_info.approaching_logout_rules & rule_handler.RULE_ACTIVITY_DURATION:
            return t.gettext(self.text_need_break_approaching).format(**p_rule_result_info.args)

        else:
            fmt = "pick_text_for_approaching_logout(): cannot derive text for rule result %d" % p_rule_result_info.approaching_logout_rules
            self._logger.warning(fmt)
            return ""

    def get_current_rule_result_info(self, p_reference_time, p_username):

        users_stat_infos = process_statistics.get_process_statistics(
            p_process_infos=self.get_process_infos(),
            p_reference_time=p_reference_time,
            p_max_lookback_in_days=1,
            p_rule_set_configs=self._rule_set_configs,
            p_min_activity_duration=self._config.min_activity_duration)

        rule_result_info = None
        user_locale = self.get_user_locale(p_username=p_username)
        rule_set = self._rule_handler.get_active_ruleset_config(p_username=p_username,
                                                                p_reference_date=p_reference_time.date())

        stat_infos = users_stat_infos.get(p_username)

        if stat_infos is not None:
            stat_info = stat_infos.get(rule_set.context)

            if stat_info is not None:
                self._logger.debug(str(stat_info))

                key_rule_override = rule_override.get_key(p_username=p_username,
                                                          p_reference_date=p_reference_time.date())
                override = self._rule_overrides.get(key_rule_override)

                rule_result_info = self._rule_handler.process_ruleset(
                    p_stat_info=stat_info,
                    p_reference_time=p_reference_time,
                    p_rule_override=override,
                    p_locale=user_locale)

        return rule_result_info

    def process_rules(self, p_reference_time):

        fmt = "Processing rules START..."
        self._logger.debug(fmt)

        users_stat_infos = process_statistics.get_process_statistics(
            p_process_infos=self.get_process_infos(),
            p_reference_time=p_reference_time,
            p_max_lookback_in_days=self._config.process_lookback_in_days,
            p_rule_set_configs=self._rule_set_configs,
            p_min_activity_duration=self._config.min_activity_duration)

        for username in self._rule_set_configs.keys():
            if username in self._usernames:
                user_locale = self.get_user_locale(p_username=username)
                rule_set = self._rule_handler.get_active_ruleset_config(p_username=username,
                                                                        p_reference_date=p_reference_time.date())

                stat_infos = users_stat_infos.get(username)

                if stat_infos is not None:
                    stat_info = stat_infos.get(rule_set.context)

                    if stat_info is not None:
                        self._logger.debug(str(stat_info))

                        key_rule_override = rule_override.get_key(p_username=username,
                                                                  p_reference_date=p_reference_time.date())
                        override = self._rule_overrides.get(key_rule_override)

                        if rule_override is not None:
                            self._logger.debug(str(override))

                        rule_result_info = self._rule_handler.process_ruleset(
                            p_stat_info=stat_info,
                            p_reference_time=p_reference_time,
                            p_rule_override=override,
                            p_locale=user_locale)

                        current_user_status = self._user_status.get(username)

                        if current_user_status is None:
                            current_user_status = user_status.UserStatus(p_username=username)
                            self._user_status[username] = current_user_status

                        if (rule_result_info.limited_session_time()):
                            current_user_status.minutes_left_in_session = rule_result_info.get_minutes_left_in_session()

                        else:
                            current_user_status.minutes_left_in_session = None

                        current_user_status.activity_allowed = rule_result_info.activity_allowed()
                        current_user_status.logged_in = stat_info.current_activity is not None


                        if rule_result_info.applying_rules > 0:
                            fmt = "Process %s" % str(rule_result_info.effective_rule_set)
                            self._logger.debug(fmt)

                            for (hostname, processes) in stat_info.currently_active_host_processes.items():

                                fmt = "User %s has %d active process(es) on host %s" % (
                                    username, len(processes), hostname)
                                self._logger.debug(fmt)

                                process_killed = False

                                for processhandler_id, pid, process_start_time in processes:
                                    processhandler = self._process_handlers.get(processhandler_id)

                                    if processhandler is not None and processhandler.can_kill_processes():
                                        self.queue_event_kill_process(
                                            p_hostname=hostname,
                                            p_username=username,
                                            p_processhandler=processhandler_id,
                                            p_pid=pid,
                                            p_process_start_time=process_start_time)
                                        process_killed = True

                                if process_killed:
                                    self.queue_event_speak(
                                        p_hostname=hostname,
                                        p_username=username,
                                        p_text=self.pick_text_for_ruleset(p_rule_result_info=rule_result_info))

                                    self.reset_logout_warning(p_username=username)

                        elif rule_result_info.approaching_logout_rules > 0:
                            for (hostname, processes) in stat_info.currently_active_host_processes.items():
                                self.issue_logout_warning(p_hostname=hostname, p_username=username,
                                                          p_rule_result_info=rule_result_info)

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
            del (self._logout_warnings[p_username])

    ################################################################################################################################
    ################################################################################################################################
    ################################################################################################################################

    def queue_event_speak(self, p_hostname, p_username, p_text):

        locale = self.get_user_locale(p_username=p_username)

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_SPEAK,
            p_hostname=p_hostname,
            p_username=p_username,
            p_text=p_text,
            p_locale=locale)
        self.queue_event(p_event=event, p_is_action=True)

    def queue_event_start_client(self):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_START_CLIENT,
            p_hostname=self._host_name)
        self.queue_event(p_event=event, p_to_master=True)

    #     def queue_broadcast_event_start_master(self):
    #
    #         for hostname in self._client_infos.keys():
    #             event = admin_event.AdminEvent(
    #                 p_event_type=admin_event.EVENT_TYPE_START_MASTER,
    #                 p_hostname=hostname)
    #             self.queue_event(p_event=event, p_is_action=True)

    def queue_event_kill_process(self, p_hostname, p_username, p_processhandler, p_pid, p_process_start_time):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_KILL_PROCESS,
            p_hostname=p_hostname,
            p_username=p_username,
            p_processhandler=p_processhandler,
            p_pid=p_pid,
            p_process_start_time=p_process_start_time)
        self.queue_event(p_event=event, p_is_action=True)

    def queue_event_update_config(self, p_hostname, p_config):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_UPDATE_CONFIG,
            p_hostname=p_hostname,
            p_payload=p_config)
        self.queue_event(p_event=event, p_is_action=True)

    def queue_event_update_login_mapping(self, p_hostname, p_login_mapping):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_UPDATE_LOGIN_MAPPING,
            p_hostname=p_hostname,
            p_payload=p_login_mapping)
        self.queue_event(p_event=event, p_is_action=True)

    def queue_event_historic_process_start(self, p_pinfo):

        event = admin_event.AdminEvent(
            p_event_type=admin_event.EVENT_TYPE_PROCESS_START,
            p_hostname=p_pinfo.hostname,
            p_pid=p_pinfo.pid,
            p_username=p_pinfo.username,
            p_process_start_time=p_pinfo.start_time)
        self.queue_event(p_event=event, p_is_action=True)

    def queue_artificial_activation_events(self):

        for handler in self._process_handlers.values():
            events = handler.get_artificial_activation_events()

            fmt = "Artificially activating {process_count} active processes on handler {handler_id}"
            self._logger.info(fmt.format(process_count=len(events), handler_id=handler.id))

            self.queue_events(p_events=events, p_to_master=True)

    def get_user_infos(self, p_include_history=True):

        user_infos = {}

        reference_time = datetime.datetime.now()

        users_stat_infos = process_statistics.get_process_statistics(
            p_process_infos=self.get_process_infos(),
            p_reference_time=reference_time,
            p_rule_set_configs=self._rule_set_configs,
            p_max_lookback_in_days=self._config.process_lookback_in_days if p_include_history else 1,
            p_min_activity_duration=self._config.min_activity_duration)

        for username in self._rule_set_configs.keys():
            rule_set = self._rule_handler.get_active_ruleset_config(p_username=username,
                                                                    p_reference_date=reference_time.date())
            stat_infos = users_stat_infos.get(username)
            user_locale = self.get_user_locale(p_username=username)

            if stat_infos is not None:
                stat_info = stat_infos.get(rule_set.context)

                if stat_info is not None:
                    self._logger.debug(str(stat_info))

                    key_rule_override = rule_override.get_key(p_username=username,
                                                              p_reference_date=reference_time.date())
                    override = self._rule_overrides.get(key_rule_override)
                    rule_result_info = self._rule_handler.process_ruleset(p_stat_info=stat_info,
                                                                          p_reference_time=reference_time,
                                                                          p_rule_override=override,
                                                                          p_locale=user_locale)

                    activity_permitted = rule_result_info.applying_rules == 0

                    user_infos[username] = {
                        'active_rule_set': rule_set,
                        'active_stat_info': stat_info,
                        'active_rule_result_info': rule_result_info,
                        'max_lookback_in_days': self._config.process_lookback_in_days,
                        'activity_permitted': activity_permitted,
                        'history_labels': self.history_labels
                    }

        return user_infos

    def get_admin_infos(self):

        admin_infos = []

        user_infos = self.get_user_infos(p_include_history=False)

        days = [datetime.date.today() + datetime.timedelta(days=i) for i in
                range(0, self._config.admin_lookahead_in_days + 1)]

        for override in self._rule_overrides.values():
            if not override.reference_date in days and override.reference_date >= datetime.date.today():
                days.append(override.reference_date)

        for username in sorted(self._usernames):
            admin_info = view_info.ViewInfo(p_html_key=username)
            admin_info.username = username

            admin_info.user_info = user_infos.get(username)
            admin_info.day_infos = []

            for reference_date in sorted(days):
                rule_set = self._rule_handler.get_active_ruleset_config(p_username=username,
                                                                        p_reference_date=reference_date)

                if rule_set is not None:
                    key_rule_override = rule_override.get_key(p_username=username, p_reference_date=reference_date)
                    override = self._rule_overrides.get(key_rule_override)

                    if override is None:
                        override = rule_override.RuleOverride(p_reference_date=reference_date, p_username=username)

                    effective_ruleset = rule_handler.apply_override(p_rule_set=rule_set, p_rule_override=override)

                    day_info = view_info.ViewInfo(p_parent=admin_info,
                                                  p_html_key=tools.get_simple_date_as_string(p_date=reference_date))

                    if reference_date == datetime.date.today():
                        day_info.label = (_('Today ({day:%%a})', 'long'), {"day": reference_date})
                        day_info.short_label = (_('Today', 'short'), {"day": reference_date})

                    elif reference_date == datetime.date.today() + datetime.timedelta(days=1):
                        day_info.label = (_('Tomorrow ({day:%%a})', 'long'), {"day": reference_date})
                        day_info.short_label = (_('Tomorrow', 'short'), {"day": reference_date})

                    else:
                        day_info.label = (_("{day:%%Y-%%m-%%d (%%a)}"), {"day": reference_date})
                        day_info.short_label = (_("{day:%%A}"), {"day": reference_date})

                    admin_info.day_infos.append(day_info)

                    day_info.reference_date = reference_date
                    day_info.rule_set = rule_set
                    day_info.override = override
                    day_info.effective_rule_set = effective_ruleset
                    day_info.max_lookahead_in_days = self._config.admin_lookahead_in_days

            admin_infos.append(admin_info)

        return admin_infos

    def send_events(self):

        try:
            result = self._master_connector.send_events(p_hostname=self._host_name, p_events=self._outgoing_events)
            self._outgoing_events = []

            if self._could_not_send:
                self.queue_artificial_activation_events()
                self._could_not_send = False

            if result is not None:
                self.receive_events(p_json_data=result)


        except Exception as e:

            fmt = "Exception '{estr}' while sending events to master"
            self._logger.error(fmt.format(estr=str(e)))

            self._could_not_send = True

            if self._debug_mode:
                fmt = "Propagating exception due to debug_mode=True"
                self._logger.warn(fmt)
                raise e

    def receive_events(self, p_json_data):

        for json_event in p_json_data:
            event = tools.objectify_dict(p_dict=json_event,
                                         p_class=admin_event.AdminEvent,
                                         p_attribute_classes={
                                             "process_start_time": datetime.datetime,
                                             "event_time": datetime.datetime
                                         })
            self.queue_event_locally(p_event=event)

    def get_return_events(self, p_hostname):

        events = [e for e in self._outgoing_events if e.hostname == p_hostname]

        for event in events:
            if self._persistence is not None:
                self._persistence.log_admin_event(p_admin_event=event)
            self._outgoing_events.remove(event)

        return events

    def handle_downtime(self, p_downtime):

        for process_handler in self._process_handlers.values():
            events = process_handler.get_downtime_corrected_admin_events(p_downtime=p_downtime)

            self.queue_events(p_events=events, p_to_master=True)

    def get_user_status(self, p_username):

        return self._user_status.get(p_username)