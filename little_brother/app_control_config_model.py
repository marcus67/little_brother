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

from little_brother import login_mapping
from little_brother import settings
from python_base_app import configuration

DEFAULT_SCAN_ACTIVE = True
DEFAULT_ADMIN_LOOKAHEAD_IN_DAYS = 7  # days
DEFAULT_PROCESS_LOOKUP_IN_DAYS = 7  # days
DEFAULT_HISTORY_LENGTH_IN_DAYS = 180  # days
DEFAULT_MIN_ACTIVITY_DURATION = 60  # seconds
DEFAULT_CHECK_INTERVAL = 5  # seconds
DEFAULT_INDEX_REFRESH_INTERVAL = 60  # seconds
DEFAULT_TOPOLOGY_REFRESH_INTERVAL = 60  # seconds
DEFAULT_LOCALE = "en_US"
DEFAULT_MAXIMUM_CLIENT_PING_INTERVAL = 60  # seconds
DEFAULT_WARNING_TIME_WITHOUT_SEND_EVENTS = 3 * DEFAULT_CHECK_INTERVAL  # seconds
DEFAULT_MAXIMUM_TIME_WITHOUT_SEND_EVENTS = 10 * DEFAULT_CHECK_INTERVAL  # minutes
DEFAULT_KILL_PROCESS_DELAY = 10  # seconds
DEFAULT_TIME_EXTENSION_PERIODS = "-30,-15,-5,5,10,15,30,45,60"
DEFAULT_UPDATE_CHANNEL = settings.MASTER_BRANCH_NAME

SECTION_NAME = "AppControl"


class AppControlConfigModel(configuration.ConfigModel):

    def __init__(self):
        super().__init__(p_section_name=SECTION_NAME)

        self.process_lookback_in_days = DEFAULT_PROCESS_LOOKUP_IN_DAYS
        self.history_length_in_days = DEFAULT_HISTORY_LENGTH_IN_DAYS
        self.admin_lookahead_in_days = DEFAULT_ADMIN_LOOKAHEAD_IN_DAYS
        self.server_group = login_mapping.DEFAULT_SERVER_GROUP
        self.hostname = configuration.NONE_STRING
        self.scan_active = DEFAULT_SCAN_ACTIVE
        self.check_interval = DEFAULT_CHECK_INTERVAL
        self.min_activity_duration = DEFAULT_MIN_ACTIVITY_DURATION
        self.user_mappings = [configuration.NONE_STRING]
        self.index_refresh_interval = DEFAULT_INDEX_REFRESH_INTERVAL
        self.topology_refresh_interval = DEFAULT_TOPOLOGY_REFRESH_INTERVAL
        self.maximum_client_ping_interval = DEFAULT_MAXIMUM_CLIENT_PING_INTERVAL
        self.maximum_time_without_send_events = DEFAULT_MAXIMUM_TIME_WITHOUT_SEND_EVENTS
        self.warning_time_without_send_events = DEFAULT_WARNING_TIME_WITHOUT_SEND_EVENTS
        self.kill_process_delay = DEFAULT_KILL_PROCESS_DELAY
        self.time_extension_periods = DEFAULT_TIME_EXTENSION_PERIODS
        self.update_channel = DEFAULT_UPDATE_CHANNEL

        self._time_extension_periods_list = None

    @property
    def time_extension_periods_list(self):

        if self._time_extension_periods_list is None:
            try:
                self._time_extension_periods_list = [int(entry) for entry in self.time_extension_periods.split(",")]

            except Exception as e:
                msg = "Invalid list of time extension periods '{periods}' (Exception: {exception})"
                raise configuration.ConfigurationException(
                    msg.format(periods=self.time_extension_periods, exception=str(e)))

        return self._time_extension_periods_list
