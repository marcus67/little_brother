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
import shlex
import subprocess

from little_brother import admin_event
from little_brother import process_handler
from python_base_app import configuration
from python_base_app import log_handling
from python_base_app import stats
from python_base_app import tools

SECTION_NAME = "ClientDeviceHandler"

CLIENT_DEVICE_SECTION_PREFIX = "ClientDevice"

DEFAULT_PING_COMMAND = "/bin/ping"
DEFAULT_MIN_ACTIVITY_DURATION = 60  # seconds
DEFAULT_MAX_ACTIVE_PING_DELAY = 100  # milliseconds
DEFAULT_PING_RESULT_REGEX = r"rtt min/avg/max/mdev = [\d\.]+/([\d\.]+)/[\d\.]+/[\d\.]+ ms"
DEFAULT_SAMPLE_SIZE = 10


class ClientDeviceHandlerConfigModel(process_handler.ProcessHandlerConfigModel):

    def __init__(self):
        super(ClientDeviceHandlerConfigModel, self).__init__(p_section_name=SECTION_NAME)

        self.ping_command = DEFAULT_PING_COMMAND
        self.ping_result_regex = DEFAULT_PING_RESULT_REGEX


class ClientDeviceConfigModel(configuration.ConfigModel):

    def __init__(self, p_section_name):
        super(ClientDeviceConfigModel, self).__init__(p_section_name=p_section_name)

        self.name = None
        self.username = None
        self.hostname = None

        self.min_activity_duration = DEFAULT_MIN_ACTIVITY_DURATION
        self.max_active_ping_delay = DEFAULT_MAX_ACTIVE_PING_DELAY
        self.sample_size = DEFAULT_SAMPLE_SIZE

    def __str__(self):
        return "ClientDevice (name=%s, user=%s, host=%s)" % (self.name, self.username, self.hostname)


class ClientDeviceSectionHandler(configuration.ConfigurationSectionHandler):

    def __init__(self):
        super(ClientDeviceSectionHandler, self).__init__(p_section_prefix=CLIENT_DEVICE_SECTION_PREFIX)
        self.client_device_configs = {}

    def handle_section(self, p_section_name):
        client_device_section = ClientDeviceConfigModel(p_section_name=p_section_name)

        self.scan(p_section=client_device_section)
        tools.check_config_value(p_config=client_device_section, p_config_attribute_name="username")
        tools.check_config_value(p_config=client_device_section, p_config_attribute_name="hostname")

        configs = self.client_device_configs.get(client_device_section.name)

        if configs is None:
            configs = []
            self.client_device_configs[client_device_section.name] = client_device_section

        configs.append(client_device_section)


class ClientDeviceHandler(process_handler.ProcessHandler):

    def __init__(self, p_config, p_client_device_configs):

        super().__init__(p_config=p_config)
        self._client_device_configs = p_client_device_configs

        try:
            self.ping_result_regex = re.compile(self._config.ping_result_regex)

        except Exception:
            fmt = "Invalid regular expression '{regex}' in [{section}]ping_result_regex"
            raise configuration.ConfigurationException(
                fmt.format(regex=self._config.ping_result_regex, section=SECTION_NAME))

        self._logger = log_handling.get_logger(self.__class__.__name__)

        self._process_infos = {}
        self._device_infos = {}
        self._process_info_candidates = {}

    # https://stackoverflow.com/questions/2953462/pinging-servers-in-python
    def ping(self, p_host):
        """
        Returns True if host (str) responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
        """

        fmt = "{ping_command} -w 1 {c_option} {host}"
        raw_command = fmt.format(ping_command=self._config.ping_command,
                                 # Ping command count option as function of OS
                                 c_option='-n 1' if tools.is_windows() else '-c 1',
                                 host=shlex.quote(p_host))

        command = shlex.split(raw_command)
        delay = None

        fmt = "Executing command {cmd} in Popen"
        self._logger.debug(fmt.format(cmd=command))

        proc = subprocess.Popen(command, stdout=subprocess.PIPE)

        for line in proc.stdout:
            result = self.ping_result_regex.match(line.decode("UTF-8"))

            if result:
                delay = float(result.group(1))
                break

        fmt = "Host {host} is {status}"
        self._logger.debug(
            fmt.format(host=p_host, status="responding (%.1f ms)" % delay if delay is not None else "down"))

        return delay

    def ping_device(self, p_client_device_config):

        fmt = "Pinging {device}..."
        self._logger.debug(fmt.format(device=str(p_client_device_config)))
        delay = self.ping(p_client_device_config.hostname)

        if delay is not None:

            moving_average = self._device_infos.get(p_client_device_config.hostname)

            if moving_average is None:
                moving_average = stats.MovingAverage(p_sample_size=p_client_device_config.sample_size)
                self._device_infos[p_client_device_config.hostname] = moving_average

            moving_average.add_value(delay)

            average = moving_average.get_value()
            fmt = "Moving average={delay:.0f}"
            self._logger.debug(fmt.format(delay=average))

            device_is_up = average < p_client_device_config.max_active_ping_delay

        else:
            self._device_infos[p_client_device_config.hostname] = None
            device_is_up = False

        fmt = "{device} is {status}"
        self._logger.debug(fmt.format(device=str(p_client_device_config), status="up" if device_is_up else "down"))

        return device_is_up

    def get_current_active_pinfo(self, p_hostname):

        max_start_time = None
        most_recent_pinfo = None

        for pinfo in self._process_infos.values():
            if pinfo.hostname == p_hostname:
                if max_start_time is None or pinfo.start_time > max_start_time:
                    max_start_time = pinfo.start_time
                    most_recent_pinfo = pinfo

        if most_recent_pinfo is not None:
            if most_recent_pinfo.end_time is None:
                return most_recent_pinfo

        return None

    def scan_processes(self, p_reference_time, p_server_group, p_login_mapping, p_host_name, p_process_regex_map):

        current_device_infos = {}
        events = []

        for device_config in self._client_device_configs.values():
            device_is_up = self.ping_device(p_client_device_config=device_config)

            if device_is_up:
                current_device_infos[device_config.hostname] = device_config

            else:
                if device_config.hostname in self._process_info_candidates:
                    del (self._process_info_candidates[device_config.hostname])

        for hostname, device_config in current_device_infos.items():
            current_pinfo = self.get_current_active_pinfo(hostname)

            if current_pinfo is None:
                if hostname in self._process_info_candidates:
                    event = self._process_info_candidates[hostname]

                    uptime = (p_reference_time - event.process_start_time).total_seconds()

                    if uptime > device_config.min_activity_duration:
                        events.append(event)
                        del (self._process_info_candidates[hostname])

                else:
                    event = admin_event.AdminEvent(
                        p_event_type=admin_event.EVENT_TYPE_PROCESS_START,
                        p_hostname=hostname,
                        p_processhandler=self.id,
                        p_username=device_config.username,
                        p_process_start_time=p_reference_time)
                    self._process_info_candidates[hostname] = event

        for pinfo in self._process_infos.values():
            # If the end time of a current entry is None AND the process was started on the local host AND
            # the process is no longer running THEN send an EVENT_TYPE_PROCESS_END event!
            if pinfo.end_time is None and pinfo.hostname not in current_device_infos:
                event = self.create_admin_event_process_end_from_pinfo(p_pinfo=pinfo, p_reference_time=p_reference_time)
                events.append(event)

        return events
