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

import copy
import datetime

from little_brother import constants
from little_brother.persistence.persistent_time_extension import TimeExtension
from python_base_app import tools

RULE_TOO_EARLY = 1
RULE_TOO_LATE = 2
RULE_TIME_OF_DAY = (RULE_TOO_EARLY | RULE_TOO_LATE)
RULE_TIME_PER_DAY = 4
RULE_DAY_BLOCKED = 8
RULE_ACTIVITY_DURATION = 16
RULE_MIN_BREAK = 32

RULE_FREE_PLAY = 64
RULE_TIME_EXTENSION = 128

# Rules covered by this mask result in play time being granted
# Note: granting has higher priority than denying
RULE_GRANT_PLAYTIME_MASK = RULE_FREE_PLAY | \
                           RULE_TIME_EXTENSION

# Rules covered by this mask result in play time being denied
RULE_DENY_PLAYTIME_MASK = RULE_TIME_OF_DAY | \
                          RULE_TIME_PER_DAY | \
                          RULE_DAY_BLOCKED | \
                          RULE_ACTIVITY_DURATION | \
                          RULE_MIN_BREAK

INFO_REMAINING_PLAYTIME = 256
INFO_REMAINING_PLAYTIME_THIS_SESSION = 512

INFO_MASK = INFO_REMAINING_PLAYTIME | INFO_REMAINING_PLAYTIME_THIS_SESSION

# Dummy function to trigger extraction by pybabel...
_ = lambda x: x


def apply_override(p_rule_set, p_rule_override):
    rule_set = p_rule_set

    if p_rule_override is not None:
        rule_set = copy.copy(p_rule_set)

        if p_rule_override.max_time_per_day is not None:
            rule_set.max_time_per_day = p_rule_override.max_time_per_day
            rule_set.max_time_per_day_class = constants.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE

        if p_rule_override.min_time_of_day is not None:
            rule_set.min_time_of_day = p_rule_override.min_time_of_day
            rule_set.min_time_of_day_class = constants.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE

        if p_rule_override.max_time_of_day is not None:
            rule_set.max_time_of_day = p_rule_override.max_time_of_day
            rule_set.max_time_of_day_class = constants.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE

        if p_rule_override.min_break is not None:
            rule_set.min_break = p_rule_override.min_break
            rule_set.min_break_class = constants.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE

        if p_rule_override.free_play:
            rule_set.free_play = True
            rule_set.free_play_class = constants.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE

        if p_rule_override.max_activity_duration is not None:
            rule_set.max_activity_duration = p_rule_override.max_activity_duration
            rule_set.max_activity_duration_class = constants.CSS_CLASS_EMPHASIZE_RULE_OVERRIDE

    return rule_set


class RuleResultInfo(object):

    def __init__(self, p_default_rule_set=None, p_rule_override=None,
                 p_user: str = None, p_locale: str = None):

        self.default_rule_set = p_default_rule_set

        if p_default_rule_set is not None and p_rule_override is not None:
            self.effective_rule_set = apply_override(p_rule_set=p_default_rule_set, p_rule_override=p_rule_override)

        else:
            self.effective_rule_set = p_default_rule_set

        self.user = p_user
        self.locale = p_locale
        self.free_play = False
        self.applying_rule_text_templates = []
        self.applying_rules = 0
        self.break_minutes_left = 0
        self.approaching_logout_rules = 0
        self.minutes_left_today = None
        self.minutes_left_in_session = None
        self.session_end_datetime: datetime.datetime = None
        self.time_extension_active = False
        self.minutes_left_in_time_extension = None
        self.time_extension_start_datetime = None
        self.time_extension_end_datetime = None

    @property
    def args(self):
        return {
            'minutes_left_in_session': self.get_minutes_left_in_session(),
            'minutes_left_today': self.minutes_left_today,
            'session_end_datetime': self.session_end_datetime,
            'user': self.user,
            'break_minutes_left': self.break_minutes_left
        }

    def     set_approaching_logout_rule(self, p_rule):

        self.approaching_logout_rules = self.approaching_logout_rules | p_rule

    def set_minutes_left_in_session(self, p_minutes_left: int) -> int:

        p_minutes_left = max(p_minutes_left, 0)

        if self.minutes_left_in_session is None or (p_minutes_left < self.minutes_left_in_session):
            self.minutes_left_in_session = p_minutes_left

        return self.get_minutes_left_in_session()

    def set_minutes_left_today(self, p_minutes_left):

        p_minutes_left = max(p_minutes_left, 0)

        if self.minutes_left_today is None or p_minutes_left < self.minutes_left_today:
            self.minutes_left_today = p_minutes_left

    def set_session_end_datetime(self, p_session_end_datetime):

        if self.session_end_datetime is None or p_session_end_datetime < self.session_end_datetime:
            self.session_end_datetime = p_session_end_datetime

    def get_minutes_left_in_session(self):

        if  self.free_play:
            return None

        if self.minutes_left_in_session is None:
            return self.minutes_left_in_time_extension

        elif self.minutes_left_in_time_extension is None:
            return self.minutes_left_in_session

        return max(self.minutes_left_in_session, self.minutes_left_in_time_extension)

    def activity_granted(self):

        return self.applying_rules & RULE_GRANT_PLAYTIME_MASK > 0

    def skip_negative_checks(self):

        return self.applying_rules & RULE_FREE_PLAY > 0

    def activity_allowed(self):

        return (self.applying_rules & RULE_GRANT_PLAYTIME_MASK > 0) or \
               (self.applying_rules & RULE_DENY_PLAYTIME_MASK == 0)

    def limited_session_time(self):

        return self.get_minutes_left_in_session() is not None

    def add_time_extension_meta_data(self, p_reference_time: datetime.datetime,
                                     p_active_time_extension: TimeExtension):

        if p_active_time_extension is None:
            self.time_extension_active = False
            self.minutes_left_in_time_extension = None
            return

        self.applying_rules = self.applying_rules | RULE_TIME_EXTENSION

        self.time_extension_start_datetime = p_active_time_extension.start_datetime
        self.time_extension_end_datetime = p_active_time_extension.end_datetime
        seconds_in_extension = \
            (p_active_time_extension.end_datetime - p_active_time_extension.start_datetime).total_seconds()
        self.applying_rule_text_templates.append(
            (_("Active time extension ({duration}) until {hh_mm}"),
             {
                 "duration": tools.get_duration_as_string(p_seconds=seconds_in_extension, p_include_seconds=False),
                 "hh_mm": p_active_time_extension.end_datetime.strftime("%H:%M")
             }))

        time_left_in_seconds = (p_active_time_extension.end_datetime - p_reference_time).total_seconds()
        self.minutes_left_in_time_extension = max(int((time_left_in_seconds + 30) / 60), 0)

    def check_approaching_logout(self, p_warning_before_logout: int, p_rule: int):

        if self.get_minutes_left_in_session() <= p_warning_before_logout:
            self.set_approaching_logout_rule(p_rule=p_rule)

    def datetime_is_permitted_by_extension(self, p_datetime: datetime.datetime):

        if not self.time_extension_active:
            return False

        return p_datetime >= self.time_extension_start_datetime and p_datetime < self.time_extension_end_datetime
