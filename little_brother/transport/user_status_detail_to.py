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

# See https://stackoverflow.com/questions/3877947/self-referencing-classes-in-python
from typing_extensions import Self


class UserStatusDetailTO:

    def __init__(self,
                 p_history_label: str | None,
                 p_duration_in_seconds: int,
                 p_downtime_in_seconds: int | None,
                 p_min_time_in_iso_8601: str,
                 p_max_time_in_iso_8601: str,
                 p_host_infos: str,
                 p_user_status_details: list[Self] = None):

        self.history_label = p_history_label
        self.duration_in_seconds = p_duration_in_seconds
        self.downtime_in_seconds = p_downtime_in_seconds
        self.min_time_in_iso_8601 = p_min_time_in_iso_8601
        self.max_time_in_iso_8601 = p_max_time_in_iso_8601
        self.host_infos = p_host_infos
        self.user_status_details = p_user_status_details
