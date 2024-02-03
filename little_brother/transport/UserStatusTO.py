# -*- coding: utf-8 -*-

# Copyright (C) 2019-24  Marcus Rickert
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

class UserStatusTO:

    def __init__(self, p_username: str,
                 p_full_name: str,
                 p_context_label: str,
                 p_todays_activity_duration_in_seconds: int,
                 p_max_time_per_day_in_seconds: int,
                 p_todays_downtime_in_seconds: int,
                 p_free_play: bool,
                 p_activity_permitted: bool,
                 p_previous_activity_start_time_in_iso_8601: str,
                 p_previous_activity_end_time_in_iso_8601: str,
                 p_current_activity_start_time_in_iso_8601: str,
                 p_current_activity_duration_in_seconds: int):

        self.username = p_username
        self.full_name = p_full_name
        self.context_label = p_context_label
        self.todays_activity_duration_in_seconds = p_todays_activity_duration_in_seconds
        self.max_time_per_day_in_seconds = p_max_time_per_day_in_seconds
        self.todays_downtime_in_seconds = p_todays_downtime_in_seconds
        self.free_play = p_free_play
        self.activity_permitted = p_activity_permitted
        self.previous_activity_start_time_in_iso_8601 = p_previous_activity_start_time_in_iso_8601
        self.previous_activity_end_time_in_iso_8601 = p_previous_activity_end_time_in_iso_8601
        self.current_activity_start_time_in_iso_8601 = p_current_activity_start_time_in_iso_8601
        self.current_activity_duration_in_seconds = p_current_activity_duration_in_seconds
