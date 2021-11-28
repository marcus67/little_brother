# -*- coding: utf-8 -*-

# Copyright (C) 2020-2021  Marcus Rickert
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

import prometheus_client

BUILT_IN_METRIC_RESIDENT_MEMORY_BYTES = 'process_resident_memory_bytes'
BUILT_IN_METRIC_PROCESS_START_TIME_SECONDS = 'process_start_time_seconds'
BUILT_IN_METRIC_PROCESS_CPU_SECONDS = 'process_cpu_seconds'

class ClientStats(object):
    def __init__(self, p_version=None, p_revision=None, p_python_version=None,
                 p_running_in_docker=None, p_running_in_snap=None):
        self.version = p_version
        self.revision = p_revision
        self.python_version = p_python_version
        self.running_in_docker = p_running_in_docker
        self.running_in_snap = p_running_in_snap
        self.resident_memory_bytes = 0.0
        self.start_time_seconds = 0.0
        self.cpu_seconds_total = 0.0

def find_built_in_metric(p_name):

    return prometheus_client.REGISTRY._names_to_collectors.get(p_name)
