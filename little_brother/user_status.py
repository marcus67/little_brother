# -*- coding: utf-8 -*-

# Copyright (C) 2019-2021  Marcus Rickert
#
# See https://github.com/marcus67/little_brother_taskbar
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


class UserStatus(object):

    def __init__(self, p_username=None):

        self.username = p_username
        self.minutes_left_in_session = None
        self.activity_allowed = False
        self.logged_in = False
        self.locale = None
        self.notification = None

        # Since LittleBrother version 0.3.13
        self.warning_time_without_send_events = None
        self.maximum_time_without_send_events = None

        # Since LittleBrother 0.4.1
        self.monitoring_active = False

        # Since LittleBrother 0.4.6
        self.optional_time_available = None
        self.ruleset_check_interval = None
