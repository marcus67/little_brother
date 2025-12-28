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


class RuleSetTO:

    def __init__(self,
                 p_min_time_of_day_in_iso_8601: str = None,
                 p_max_time_of_day_in_iso_8601: str = None,
                 p_max_time_per_day_in_seconds: int = None,
                 p_min_break_in_seconds: int = None,
                 p_max_activity_duration_in_seconds: int = None,
                 p_free_play: bool = None,
                 p_label: str = None):

        self.label = p_label
        self.min_time_of_day_in_iso_8601 = p_min_time_of_day_in_iso_8601
        self.max_time_of_day_in_iso_8601 = p_max_time_of_day_in_iso_8601
        self.max_time_per_day_in_seconds = p_max_time_per_day_in_seconds
        self.min_break_in_seconds = p_min_break_in_seconds
        self.max_activity_duration_in_seconds = p_max_activity_duration_in_seconds
        self.free_play = p_free_play
