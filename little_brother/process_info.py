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

from python_base_app import tools


def get_key(p_hostname, p_pid, p_start_time):
    if p_pid is not None:
        return "%s|%d|%s" % (p_hostname, p_pid, p_start_time.strftime("%s"))

    else:
        return "%s|NONE|%s" % (p_hostname, p_start_time.strftime("%s"))


class ProcessInfo(object):

    def __init__(self, p_hostname=None, p_username=None, p_processhandler=None, p_processname=None, p_pid=None,
                 p_start_time=None, p_end_time=None, p_downtime=0, p_percent=100, p_hostlabel=None,
                 p_cmd_line=None):
        self.id = None
        self.hostname = p_hostname
        self.hostlabel = p_hostlabel if p_hostlabel is not None else p_hostname
        self.username = p_username
        self.processhandler = p_processhandler
        self.processname = p_processname
        self.pid = p_pid
        self.start_time = p_start_time
        self.end_time = p_end_time
        self.downtime = p_downtime
        self.percent = p_percent
        self.cmd_line = p_cmd_line

    def is_active(self):
        return self.end_time is None

    def is_valid(self):
        return (
                self.hostname is not None and
                self.username is not None and
                self.processhandler is not None and
                # self.pid is not None and
                # self.processname is not None and
                self.start_time is not None and
                # entries with start time after end time will confuse the statistics module
                (self.end_time is None or
                 self.end_time is not None and self.end_time >= self.start_time)
        )

    def get_key(self):
        return get_key(p_hostname=self.hostname, p_pid=self.pid, p_start_time=self.start_time)

    def __str__(self):

        fmt = "ProcessInfo (host={host}, user={user}, process={process}, PID={pid}, epoch={epoch})"
        return fmt.format(host=self.hostname, user=self.username, process=self.processname,
                          pid=tools.int_to_string(self.pid), epoch=self.start_time.strftime("%s"))
