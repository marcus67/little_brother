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
import subprocess

import psutil
import shlex

from python_base_app import log_handling
from python_base_app import tools
from python_base_app import configuration

from little_brother import admin_event
from little_brother import process_handler
from little_brother import process_info

SECTION_NAME = "ClientProcessHandler"

PROCESS_ID_PATTERN = "pid"
USER_ID_PATTERN = "uid"
SIGNAL_ID_PATTERN = "signal"


class ClientProcessHandlerConfigModel(process_handler.ProcessHandlerConfigModel):

    def __init__(self):
        super(ClientProcessHandlerConfigModel, self).__init__(p_section_name=SECTION_NAME)

        self.sudo_command = "/usr/bin/sudo"

        if tools.is_mac_os():
            self.kill_command_pattern = "/bin/launchctl bootout gui/{uid}"
        else:
            self.kill_command_pattern = "/bin/kill -{signal} {pid}"

        self.kill_delay = 5  # seconds


class ClientProcessHandler(process_handler.ProcessHandler):

    def __init__(self, p_config, p_process_iterator_factory):

        super().__init__(p_config=p_config)
        self._process_iterator_factory = p_process_iterator_factory
        self._logger = log_handling.get_logger(self.__class__.__name__)
        self._process_infos = {}

    @staticmethod
    def can_kill_processes():
        return True

    def handle_event_kill_process(self, p_event, p_server_group=None, p_login_mapping=None):

        fmt = "Kill process %d of user %s on host %s with signal SIGHUP" % (
            p_event.pid, p_event.username, p_event.hostname)
        self._logger.debug(fmt)

        try:
            proc = psutil.Process(pid=p_event.pid)

        except Exception:
            fmt = "handle_event_kill_process(): process %d does not exist (anymore)" % p_event.pid
            self._logger.warning(fmt)
            pinfo = admin_event.create_process_info_from_event(p_event=p_event)
            return [self.create_admin_event_process_end_from_pinfo(p_pinfo=pinfo)]

        uid = p_login_mapping.get_uid_by_login(p_server_group=p_server_group, p_login=p_event.username)

        if uid is None:
            fmt = "handle_event_kill_process: cannot find uid for username '{username}'"
            self._logger.warning(fmt.format(username=p_event.username))

        params = {
            'pid': p_event.pid,
            'username': p_event.username,
            'uid': uid,
            'signal': 'SIGHUP',
            'host': p_event.hostname
        }

        fmt = "Killing process {pid} of user '{username}' on host '{host}'"

        if "{signal}" in self._config.kill_command_pattern:
            fmt = fmt + " with signal {signal}"

        self._logger.info(fmt.format(**params))

        try:
            kill_command = self._config.sudo_command + " " + self._config.kill_command_pattern.format(**params)

        except Exception as e:
            fmt = "Exception '{estr}' while generating kill command"
            raise configuration.ConfigurationException(fmt.format(estr=str(e)))

        fmt = "Executing sudo command '{cmd}'..."
        self._logger.debug(fmt.format(cmd=kill_command))

        cmd_array = shlex.split(kill_command)
        subprocess.run(cmd_array)


        _gone, alive = psutil.wait_procs([proc], timeout=self._config.kill_delay)

        if len(alive) > 0:
            params['signal'] = "SIGKILL"

            fmt = "Second attempt: killing process {pid} of user '{username}' on host '{host}'"

            if "{signal}" in self._config.kill_command_pattern:
                fmt = fmt + " with signal {signal}"

            self._logger.info(fmt.format(**params))

            kill_command = self._config.sudo_command + " " + self._config.kill_command_pattern.format(**params)

            fmt = "Executing sudo command '{cmd}'..."
            self._logger.debug(fmt.format(cmd=kill_command))

            cmd_array = shlex.split(kill_command)
            subprocess.run(cmd_array)

        return []

    def scan_processes(self, p_reference_time, p_server_group, p_login_mapping, p_host_name, p_process_regex_map):

        current_processes = {}
        events = []

        fmt = "Scanning processes..."
        self._logger.debug(fmt)

        for proc in self._process_iterator_factory.process_iter():  # attrs=['pid', 'name', 'username', 'create_time']
            try:
                uids = proc.uids()

                # On Mac OS the process we want to kill has the real user id set to root but the effective user id
                # set to the actual user.
                uid = uids.effective
                username = p_login_mapping.get_login_by_uid(p_server_group=p_server_group, p_uid=uid)

                if username is not None:
                    proc_name = proc.name()

                    if p_process_regex_map[username].match(proc_name):
                        start_time = datetime.datetime.fromtimestamp(proc.create_time(),
                                                                     datetime.timezone.utc).astimezone().replace(
                            tzinfo=None)
                        key = process_info.get_key(p_hostname=p_host_name, p_pid=proc.pid, p_start_time=start_time)
                        current_processes[key] = 1

                        if key in self._process_infos:
                            pinfo = self._process_infos[key]

                            if pinfo.end_time is not None:
                                event = self.create_admin_event_process_start_from_pinfo(p_pinfo=pinfo)
                                events.append(event)

                        else:
                            event = admin_event.AdminEvent(
                                p_event_type=admin_event.EVENT_TYPE_PROCESS_START,
                                p_hostname=p_host_name,
                                p_processhandler=self.id,
                                p_username=username,
                                p_processname=proc.name(),
                                p_process_start_time=start_time,
                                p_pid=proc.pid)
                            events.append(event)

            except psutil.NoSuchProcess as e:
                fmt = "Ignoring exception '{estr}' because process has disappeared"
                self._logger.debug(fmt.format(estr=str(e)))

        for (key, pinfo) in self._process_infos.items():
            # If the end time of a current entry is None AND the process was started on the local host AND
            # the process is no longer running THEN send an EVENT_TYPE_PROCESS_END event!
            if pinfo.end_time is None and pinfo.hostname == p_host_name and key not in current_processes:
                event = self.create_admin_event_process_end_from_pinfo(p_pinfo=pinfo, p_reference_time=p_reference_time)
                events.append(event)

        return events
