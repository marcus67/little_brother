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

from python_base_app import custom_fields
from python_base_app import custom_form
from python_base_app import tools


def get_key(p_username, p_reference_date):
    return "%s|%s" % (p_username, p_reference_date.strftime("%s"))


class RuleOverride(object):

    def __init__(self, p_username, p_reference_date, p_max_time_per_day=None,
                 p_min_time_of_day=None, p_max_time_of_day=None,
                 p_min_break=None, p_free_play=False, p_max_activity_duration=None):
        self.username = p_username
        self.reference_date = p_reference_date
        self.max_time_per_day = p_max_time_per_day
        self.min_time_of_day = p_min_time_of_day
        self.max_time_of_day = p_max_time_of_day
        self.min_break = p_min_break
        self.free_play = p_free_play
        self.max_activity_duration = p_max_activity_duration

    def get_key(self):
        return get_key(p_username=self.username, p_reference_date=self.reference_date)

    def __str__(self):
        min_time = tools.get_time_as_string(p_timestamp=self.min_time_of_day)
        max_time = tools.get_time_as_string(p_timestamp=self.max_time_of_day)
        date = tools.get_date_as_string(p_date=self.reference_date)
        max_time_per_day = tools.get_duration_as_string(p_seconds=self.max_time_per_day)
        min_break = tools.get_duration_as_string(p_seconds=self.min_break)
        max_activity_duration = tools.get_duration_as_string(p_seconds=self.max_activity_duration)

        fmt = "Rule override (user={user}, date={date}, time-of-day=[{min_time} to {max_time}], "\
              "max-time-per-day:{max_time_per_day}, min-break:{min_break}, "\
              "max-activity-duration:{max_activity_duration} free-play:{free_play})"
        return fmt.format(user=self.username, date=date, min_time=min_time, max_time=max_time,
                          max_time_per_day=max_time_per_day, min_break=min_break,
                          max_activity_duration=max_activity_duration, free_play=self.free_play)


class RuleOverrideForm(custom_form.ModelForm):
    min_time_of_day = custom_fields.TimeField("MinTimeOfDay")
    max_time_of_day = custom_fields.TimeField("MaxTimeOfDay")
    max_time_per_day = custom_fields.DurationField("MaxTimePerDay")
    min_break = custom_fields.DurationField("MinBreak")
    free_play = custom_fields.BooleanField("FreePlay")
    max_activity_duration = custom_fields.DurationField("MaxActivityDuration")
