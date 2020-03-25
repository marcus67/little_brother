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
import re

from python_base_app import configuration
from python_base_app import log_handling
from python_base_app import tools

SECTION_NAME = "RuleHandler"

RULE_SET_SECTION_PREFIX = "RuleSet"

REGEX_TIME_OF_DAY = re.compile("([0-9]+)(:([0-9]+))?")

DEFAULT_PRIORITY = 1

RULE_TOO_EARLY = 1
RULE_TOO_LATE = 2
RULE_TIME_OF_DAY = (RULE_TOO_EARLY | RULE_TOO_LATE)
RULE_TIME_PER_DAY = 4
RULE_DAY_BLOCKED = 8
RULE_ACTIVITY_DURATION = 16
RULE_MIN_BREAK = 32

DEFAULT_RULESET_LABEL = "default"
DEFAULT_PROCESS_PATTERN = "systemd|.*sh"

CSS_CLASS_EMPHASIZE_RULE_OVERRIDE = "rule-override"

# Dummy function to trigger extraction by pybabel...F
_ = lambda x: x


class RuleHandlerConfigModel(configuration.ConfigModel):

    def __init__(self):
        super(RuleHandlerConfigModel, self).__init__(p_section_name=SECTION_NAME)

        self.warning_before_logout = 5  # minutes


class RuleSetConfigModel(configuration.ConfigModel):

    def __init__(self, p_section_name=None):

        super(RuleSetConfigModel, self).__init__(p_section_name=p_section_name)
        self.context = configuration.NONE_STRING
        self.context_details = configuration.NONE_STRING
        self.context_label = configuration.NONE_STRING
        self.priority = DEFAULT_PRIORITY
        self.username = None
        self.process_name_pattern = DEFAULT_PROCESS_PATTERN
        self.min_time_of_day = configuration.NONE_STRING
        self.max_time_of_day = configuration.NONE_STRING
        self.max_time_per_day = configuration.NONE_STRING
        self.max_activity_duration = configuration.NONE_STRING
        self.min_break = configuration.NONE_STRING
        self.scan_devices = True
        self.locale = None
        self.free_play = False

        self.min_time_of_day_class = ""
        self.max_time_of_day_class = ""
        self.max_time_per_day_class = ""
        self.min_break_class = ""
        self.free_play_class = ""

        self._regex_process_name_pattern = None

    @property
    def label(self):
        if self.context_label is not None:
            return self.context_label

        if self.context_details is not None:
            return self.context_details

        if self.context is not None:
            return self.context

        return DEFAULT_RULESET_LABEL

    @property
    def regex_process_name_pattern(self):

        if self._regex_process_name_pattern is None:
            try:
                self._regex_process_name_pattern = re.compile(self.process_name_pattern)

            except Exception as e:
                raise configuration.ConfigurationException("Invalid process REGEX pattern '%s' (Exception: %s)" % (
                    self.process_name_pattern, str(e)))

        return self._regex_process_name_pattern

    def __str__(self):
        min_time = self.min_time_of_day.strftime("%H:%M") if self.min_time_of_day is not None else "-"
        max_time = self.max_time_of_day.strftime("%H:%M") if self.max_time_of_day is not None else "-"
        max_time_per_day = str(self.max_time_per_day) if self.max_time_per_day is not None else "-"
        max_duration = str(self.max_activity_duration) if self.max_activity_duration is not None else "-"
        min_break = str(self.min_break) if self.min_break is not None else "-"
        return "Rule set (user=%s, context=%s, time-of-day=[%s to %s], max-time-per-day:%s, max-duration=%s, min-break=%s, free-play=%i)" % (
            self.username, self.context, min_time, max_time, max_time_per_day, max_duration, min_break, self.free_play)

    def post_process(self):

        self.min_time_of_day = RuleSetSectionHandler.read_time_of_day(p_time_of_day=self.min_time_of_day)
        self.max_time_of_day = RuleSetSectionHandler.read_time_of_day(p_time_of_day=self.max_time_of_day)

        if (self.min_time_of_day is not None and self.max_time_of_day is not None
                and self.min_time_of_day >= self.max_time_of_day):
            msg = "Maximum time of day '{max_time_of_day}' must be later than minimum time of day '{min_time_of_day}'" \
                  " for user '{user}' and context '{context}'"
            raise configuration.ConfigurationException(
                msg.format(
                    min_time_of_day=tools.get_time_as_string(self.min_time_of_day),
                    max_time_of_day=tools.get_time_as_string(self.max_time_of_day),
                    user=self.username,
                    context=self.label))

        self.max_time_per_day = tools.get_string_as_duration(p_string=self.max_time_per_day)
        self.max_activity_duration = tools.get_string_as_duration(
            p_string=self.max_activity_duration)
        self.min_break = tools.get_string_as_duration(p_string=self.min_break)



class RuleSetSectionHandler(configuration.ConfigurationSectionHandler):

    def __init__(self):

        super(RuleSetSectionHandler, self).__init__(p_section_prefix=RULE_SET_SECTION_PREFIX)
        self.rule_set_configs = {}

    def handle_section(self, p_section_name):

        rule_set_section = RuleSetConfigModel(p_section_name=p_section_name)

        self.scan(p_section=rule_set_section)
        tools.check_config_value(p_config=rule_set_section, p_config_attribute_name="username")

        rule_set_section.post_process()

        configs = self.rule_set_configs.get(rule_set_section.username)

        if configs is None:
            configs = []
            self.rule_set_configs[rule_set_section.username] = configs

        configs.append(rule_set_section)


    @staticmethod
    def read_time_of_day(p_time_of_day):

        if p_time_of_day is None:
            return None

        result = REGEX_TIME_OF_DAY.match(p_time_of_day)

        if result is None:
            raise configuration.ConfigurationException("Invalid time of day format: '%s'. Use HH[:MM]" % p_time_of_day)

        hours = int(result.group(1))

        if result.group(3) is None:
            minutes = 0

        else:
            minutes = int(result.group(3))

        return datetime.time(hour=hours, minute=minutes)


class RuleResultInfo(object):

    def __init__(self):

        self.applying_rule_text_templates = []
        self.applying_rules = 0
        self.break_minutes_left = 0
        self.approaching_logout_rules = 0
        self.minutes_left_in_session = None
        self.minutes_left_before_logout = None
        self.default_rule_set = None
        self.effective_rule_set = None
        self.args = {}

    def set_approaching_logout_rule(self, p_rule, p_minutes_left):

        self.approaching_logout_rules = self.approaching_logout_rules | p_rule

        if self.minutes_left_before_logout is None or p_minutes_left < self.minutes_left_before_logout:
            self.minutes_left_before_logout = p_minutes_left
            self.args['minutes_left_before_logout'] = p_minutes_left

    def set_minutes_left_in_session(self, p_minutes_left):

        if self.minutes_left_in_session is None or p_minutes_left < self.minutes_left_in_session:
            self.minutes_left_in_session = p_minutes_left
            self.args['minutes_left_in_session'] = p_minutes_left

    def get_minutes_left_in_session(self):

        return self.args.get('minutes_left_in_session')

    def activity_allowed(self):

        return self.applying_rules == 0

    def limited_session_time(self):

        return self.minutes_left_in_session is not None


def apply_override(p_rule_set, p_rule_override):
    rule_set = p_rule_set

    if p_rule_override is not None:
        rule_set = copy.copy(p_rule_set)

        if p_rule_override.max_time_per_day is not None:
            rule_set.max_time_per_day = p_rule_override.max_time_per_day
            rule_set.max_time_per_day_class = CSS_CLASS_EMPHASIZE_RULE_OVERRIDE

        if p_rule_override.min_time_of_day is not None:
            rule_set.min_time_of_day = p_rule_override.min_time_of_day
            rule_set.min_time_of_day_class = CSS_CLASS_EMPHASIZE_RULE_OVERRIDE

        if p_rule_override.max_time_of_day is not None:
            rule_set.max_time_of_day = p_rule_override.max_time_of_day
            rule_set.max_time_of_day_class = CSS_CLASS_EMPHASIZE_RULE_OVERRIDE

        if p_rule_override.min_break is not None:
            rule_set.min_break = p_rule_override.min_break
            rule_set.min_break_class = CSS_CLASS_EMPHASIZE_RULE_OVERRIDE

        if p_rule_override.free_play:
            rule_set.free_play = True
            rule_set.free_play_class = CSS_CLASS_EMPHASIZE_RULE_OVERRIDE

        if p_rule_override.max_activity_duration is not None:
            rule_set.max_activity_duration = p_rule_override.max_activity_duration
            rule_set.max_activity_duration_class = CSS_CLASS_EMPHASIZE_RULE_OVERRIDE

    return rule_set


class RuleHandler(object):

    def __init__(self, p_config, p_rule_set_configs):

        self._config = p_config
        self._rule_set_configs = p_rule_set_configs
        self._context_rule_handlers = {}
        self._default_context_rule_handler_name = None

        self._logger = log_handling.get_logger(self.__class__.__name__)

    def register_context_rule_handler(self, p_context_rule_handler, p_default=False):
        self._context_rule_handlers[p_context_rule_handler.context_name] = p_context_rule_handler

        if p_default:
            self._default_context_rule_handler_name = p_context_rule_handler.context_name

    def get_active_ruleset_config(self, p_username, p_reference_date):

        active_ruleset_config = None
        max_priority = None

        ruleset_configs = self._rule_set_configs.get(p_username)

        if ruleset_configs is not None:
            for c_config in ruleset_configs:
                active = False

                context_name = c_config.context or self._default_context_rule_handler_name

                context_rule_handler = self._context_rule_handlers.get(context_name)

                if context_rule_handler is None:
                    raise configuration.ConfigurationException("invalid rule set context '%s'" % c_config.context)

                active = context_rule_handler.is_active(p_reference_date=p_reference_date,
                                                        p_details=c_config.context_details)

                if active:
                    if max_priority is None or c_config.priority > max_priority:
                        max_priority = c_config.priority
                        active_ruleset_config = c_config

        return active_ruleset_config

    def check_time_of_day(self, p_rule_set, p_stat_info, p_rule_result_info):

        if p_rule_set.free_play:
            return

        if p_rule_set.min_time_of_day is not None and p_stat_info.reference_time.timetz() < p_rule_set.min_time_of_day:
            p_rule_result_info.applying_rules = p_rule_result_info.applying_rules | RULE_TOO_EARLY

            p_rule_result_info.applying_rule_text_templates.append(
                (_("No activity before {hh_mm} hours"), {"hh_mm": p_rule_set.min_time_of_day.strftime("%H:%M")})
            )

        if p_rule_set.max_time_of_day is not None:
            if p_stat_info.reference_time.timetz() > p_rule_set.max_time_of_day:
                p_rule_result_info.applying_rules = p_rule_result_info.applying_rules | RULE_TOO_LATE
                p_rule_result_info.applying_rule_text_templates.append(
                    (_("No activity after {hh_mm} hours"), {"hh_mm": p_rule_set.max_time_of_day.strftime("%H:%M")})
                )

            max_time_of_day_as_date = datetime.datetime.combine(datetime.date.today(), p_rule_set.max_time_of_day)
            time_left_in_minutes = int((max_time_of_day_as_date - p_stat_info.reference_time).total_seconds() + 30 / 60)
            p_rule_result_info.set_minutes_left_in_session(p_minutes_left=time_left_in_minutes)

            if time_left_in_minutes <= self._config.warning_before_logout:
                p_rule_result_info.set_approaching_logout_rule(p_rule=RULE_TOO_LATE,
                                                               p_minutes_left=time_left_in_minutes)

    def check_time_per_day(self, p_rule_set, p_stat_info, p_rule_result_info):

        if p_rule_set.free_play:
            return

        if p_rule_set.max_time_per_day is not None:
            if p_stat_info.todays_activity_duration >= p_rule_set.max_time_per_day:
                if p_rule_set.max_time_per_day == 0:
                    p_rule_result_info.applying_rules = p_rule_result_info.applying_rules | RULE_DAY_BLOCKED
                    p_rule_result_info.applying_rule_text_templates.append(
                        (_("Day blocked: no activity permitted"), {})
                    )

                else:
                    p_rule_result_info.applying_rules = p_rule_result_info.applying_rules | RULE_TIME_PER_DAY
                    p_rule_result_info.applying_rule_text_templates.append(
                        (_("Activity limited to {hh_mm} per day"),
                         {"hh_mm": tools.get_duration_as_string(p_seconds=p_rule_set.max_time_per_day,
                                                                p_include_seconds=False)})
                    )

            if p_rule_set.max_time_per_day > 0:
                time_left_in_minutes = int(
                    (p_rule_set.max_time_per_day - p_stat_info.todays_activity_duration + 30) / 60)
                p_rule_result_info.set_minutes_left_in_session(p_minutes_left=time_left_in_minutes)

                if time_left_in_minutes <= self._config.warning_before_logout:
                    p_rule_result_info.set_approaching_logout_rule(p_rule=RULE_TIME_PER_DAY,
                                                                   p_minutes_left=time_left_in_minutes)

    def check_activity_duration(self, p_rule_set, p_stat_info, p_rule_result_info):

        if p_rule_set.free_play:
            return

        if p_rule_set.max_activity_duration is not None:
            current_activity_duration = p_stat_info.current_activity_duration

            if current_activity_duration is not None:
                if current_activity_duration > p_rule_set.max_activity_duration:
                    p_rule_result_info.applying_rules = p_rule_result_info.applying_rules | RULE_ACTIVITY_DURATION
                    p_rule_result_info.applying_rule_text_templates.append(
                        (_("No activity exceeding {hh_mm}"),
                         {"hh_mm": tools.get_duration_as_string(p_seconds=p_rule_set.max_activity_duration,
                                                                p_include_seconds=False)})
                    )

                else:
                    time_left_in_minutes = int((p_rule_set.max_activity_duration - current_activity_duration + 30) / 60)
                    p_rule_result_info.args['minutes_left_before_logout'] = time_left_in_minutes
                    p_rule_result_info.set_minutes_left_in_session(p_minutes_left=time_left_in_minutes)

                    if time_left_in_minutes <= self._config.warning_before_logout:
                        p_rule_result_info.set_approaching_logout_rule(p_rule=RULE_ACTIVITY_DURATION,
                                                                       p_minutes_left=time_left_in_minutes)

    @staticmethod
    def check_min_break(p_rule_set, p_stat_info, p_rule_result_info):

        if p_rule_set.free_play:
            return

        if p_rule_set.min_break is not None and p_rule_set.max_activity_duration is not None:
            seconds_since_last_activity = p_stat_info.seconds_since_last_activity

            if p_stat_info.previous_activity_duration is not None:
                fraction_used = min(1.0 * p_stat_info.previous_activity_duration / p_rule_set.max_activity_duration,
                                    1.0)
                min_relative_break = fraction_used * p_rule_set.min_break

            else:
                min_relative_break = p_rule_set.min_break

            if seconds_since_last_activity is not None and seconds_since_last_activity < min_relative_break:
                p_rule_result_info.applying_rules = p_rule_result_info.applying_rules | RULE_MIN_BREAK
                p_rule_result_info.applying_rule_text_templates.append(
                    (_("Minimum break time {hh_mm} not reached"),
                     {"hh_mm": tools.get_duration_as_string(p_seconds=p_rule_set.min_break)})
                )
                p_rule_result_info.break_minutes_left = int(
                    (min_relative_break - seconds_since_last_activity + 30) / 60)
                p_rule_result_info.args['break_minutes_left'] = p_rule_result_info.break_minutes_left

        return 0

    def process_ruleset(self, p_stat_info, p_reference_time, p_rule_override, p_locale):

        rule_result_info = RuleResultInfo()

        rule_set = self.get_active_ruleset_config(p_username=p_stat_info.username, p_reference_date=p_reference_time)
        rule_result_info.default_rule_set = rule_set
        rule_result_info.effective_rule_set = apply_override(p_rule_set=rule_set, p_rule_override=p_rule_override)

        rule_result_info.args["user"] = p_stat_info.username
        rule_result_info.locale = p_locale

        if rule_set is not None:
            self.check_time_of_day(p_rule_set=rule_result_info.effective_rule_set, p_stat_info=p_stat_info,
                                   p_rule_result_info=rule_result_info)
            self.check_time_per_day(p_rule_set=rule_result_info.effective_rule_set, p_stat_info=p_stat_info,
                                    p_rule_result_info=rule_result_info)
            self.check_activity_duration(p_rule_set=rule_result_info.effective_rule_set, p_stat_info=p_stat_info,
                                         p_rule_result_info=rule_result_info)
            self.check_min_break(p_rule_set=rule_result_info.effective_rule_set, p_stat_info=p_stat_info,
                                 p_rule_result_info=rule_result_info)

        if not rule_result_info.activity_allowed():
            fmt = "Activity prohibited for user %s: applying rules(s) %d" % (
            p_stat_info.username, rule_result_info.applying_rules)
            self._logger.debug(fmt)

        return rule_result_info
