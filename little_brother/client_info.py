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

from packaging import version

from little_brother.client_stats import ClientStats
from python_base_app import tools

LAST_VERSION_WITHOUT_CLIENT_STAT_SUPPORT = "0.3.8"
MINIMUM_VERSION_WITH_CLIENT_STAT_SUPPORT = "0.3.9"

CSS_CLASS_MAXIMUM_PING_EXCEEDED = "node_inactive"
CSS_CLASS_SLAVE_VERSION_OUTDATED = "node_outdated"

def _(x):
    return x

class ClientInfo(object):

    def __init__(self, p_is_master, p_host_name, p_client_stats: ClientStats, p_maximum_client_ping_interval=None,
                 p_master_version=None):
        self.is_master = p_is_master
        self.host_name = p_host_name
        self.client_stats = p_client_stats
        self.maximum_client_ping_interval = p_maximum_client_ping_interval
        self.last_message = None
        self.master_version = p_master_version
        self.start_event_sent = False

    @property
    def runtime(self):

        if self.client_stats is None:
            return ""

        if self.client_stats.running_in_docker:
            return "(Docker)"

        elif self.client_stats.running_in_snap:
            return "(Snap)"

        return ""

    @property
    def node_type(self):
        return _("Master") if self.is_master else _("Slave")

    @property
    def seconds_without_ping(self):
        if self.last_message is None:
            return None

        return (tools.get_current_time() - self.last_message).seconds

    @property
    def last_message_string(self):

        some_seconds_without_ping = self.seconds_without_ping

        if some_seconds_without_ping is None:
            return _("n/a")

        return tools.get_duration_as_string(some_seconds_without_ping)

    @property
    def last_message_class(self):
        if self.last_message is None:
            return ""

        if self.maximum_client_ping_interval is not None:
            seconds_without_ping = (tools.get_current_time() - self.last_message).seconds

            if seconds_without_ping > self.maximum_client_ping_interval:
                return CSS_CLASS_MAXIMUM_PING_EXCEEDED

        return ""

    @property
    def version_string(self):
        if self.client_stats is not None and self.client_stats.version is not None:
            return self.client_stats.version

        return "<" + MINIMUM_VERSION_WITH_CLIENT_STAT_SUPPORT

    @property
    def version_class(self):
        if self.master_version is not None:
            if self.client_stats is not None and self.client_stats.version is not None:
                client_version = self.client_stats.version

            else:
                client_version = LAST_VERSION_WITHOUT_CLIENT_STAT_SUPPORT

            if version.parse(client_version) < version.parse(self.master_version):
                return CSS_CLASS_SLAVE_VERSION_OUTDATED

        return ""
