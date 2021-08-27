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

from little_brother import process_info

EVENT_TYPE_START_MASTER = "START_MASTER"
EVENT_TYPE_START_CLIENT = "START_CLIENT"
EVENT_TYPE_STOP_CLIENT = "STOP_CLIENT"
EVENT_TYPE_LOGIN_NOT_PERMITTED = "LOGIN_NOT_PERMITTED"
EVENT_TYPE_LOGIN_PERMITTED = "LOGIN_PERMITTED"
EVENT_TYPE_KILL_PROCESS = "KILL_PROCESS"
EVENT_TYPE_UPDATE_CONFIG = "UPDATE_CONFIG"
EVENT_TYPE_UPDATE_LOGIN_MAPPING = "UPDATE_LOGIN_MAPPING"
EVENT_TYPE_PROCESS_START = "PROCESS_START"
EVENT_TYPE_PROHIBITED_PROCESS = "PROHIBITED_PROCESS"
EVENT_TYPE_PROCESS_DOWNTIME = "PROCESS_DOWNTIME"
EVENT_TYPE_PROCESS_END = "PROCESS_END"

EVENT_TYPE_DUMMY_1 = "DUMMY1"


def create_process_info_from_event(p_event):
    return process_info.ProcessInfo(
        p_hostname=p_event.hostname,
        p_hostlabel=p_event.hostlabel,
        p_pid=p_event.pid,
        p_username=p_event.username,
        p_processhandler=p_event.processhandler,
        p_processname=p_event.processname,
        p_start_time=p_event.process_start_time,
        p_percent=p_event.percent)


class AdminEvent(object):

    def __init__(self, p_hostname=None,
                 p_username=None,
                 p_pid=None,
                 p_processhandler=None,
                 p_processname=None,
                 p_event_type=None,
                 p_event_time=None,
                 p_process_start_time=None,
                 p_text=None,
                 p_locale=None,
                 p_payload=None,
                 p_downtime=0,
                 p_percent=100,
                 p_hostlabel=None,
                 p_delay=0):
        if p_event_time is None:
            p_event_time = datetime.datetime.now()

        self.hostname = p_hostname
        self.username = p_username
        self.pid = p_pid
        self.processhandler = p_processhandler
        self.processname = p_processname
        self.event_type = p_event_type
        self.event_time = p_event_time
        self.process_start_time = p_process_start_time
        self.text = p_text
        self.locale = p_locale
        self.payload = p_payload
        self.downtime = p_downtime
        self.percent = p_percent
        self.hostlabel = p_hostlabel
        self.delay = p_delay

    def __str__(self):
        return "AdminEvent (type=%s, host=%s, user=%s, process=%s, PID=%s)" % (
            self.event_type, self.hostname, self.username, self.processname,
            str(self.pid) if self.pid is not None else "-")

    def __eq__(self, p_other):
        return (self.hostname == p_other.hostname and
                self.username == p_other.username and
                self.processhandler == p_other.processhandler and
                self.pid == p_other.pid and
                self.event_type == p_other.event_type and
                self.text == p_other.text and
                self.payload == p_other.payload)

    def get_key(self):
        return process_info.get_key(p_hostname=self.hostname, p_pid=self.pid, p_start_time=self.process_start_time)
