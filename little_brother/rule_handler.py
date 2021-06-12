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
import re

from little_brother import constants
from little_brother import process_statistics
from little_brother import rule_result_info
from little_brother.persistence import persistence
from little_brother.persistence.persistent_rule_set import RuleSet
from little_brother.rule_result_info import RuleResultInfo
from python_base_app import configuration
from python_base_app import log_handling
from python_base_app import tools

SECTION_NAME = "RuleHandler"

RULE_SET_SECTION_PREFIX = "RuleSet"

REGEX_TIME_OF_DAY = re.compile("([0-9]+)(:([0-9]+))?")

DEFAULT_RULESET_LABEL = "default"

# Dummy function to trigger extraction by pybabel...
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
        self.priority = constants.DEFAULT_RULE_SET_PRIORITY
        self.username = None
        self.process_name_pattern = constants.DEFAULT_PROCESS_NAME_PATTERN
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


class RuleHandler(object):

    def __init__(self, p_config, p_persistence):

        self._config = p_config
        self._persistence: persistence.Persistence = p_persistence
        self._context_rule_handlers = {}
        self._default_context_rule_handler_name = None

        self._logger = log_handling.get_logger(self.__class__.__name__)

    def register_context_rule_handler(self, p_context_rule_handler, p_default=False):
        self._context_rule_handlers[p_context_rule_handler.context_name] = p_context_rule_handler

        if p_default:
            self._default_context_rule_handler_name = p_context_rule_handler.context_name

    def get_context_rule_handler_names(self):

        return self._context_rule_handlers.keys()

    def get_context_rule_handler(self, p_context_name):

        return self._context_rule_handlers.get(p_context_name)

    def validate_context_rule_handler_details(self, p_context_name, p_context_details):

        context_rule_handler = self._context_rule_handlers.get(p_context_name)

        if context_rule_handler is not None:
            context_rule_handler.validate_context_details(p_context_details)

    def get_context_rule_handler_choices(self):

        choices = []

        for handler in self._context_rule_handlers.values():
            choices.extend(handler.get_choices())

        return choices

    def get_active_ruleset(self, p_rule_sets, p_reference_date) ->  RuleSet:

        active_ruleset = None
        max_priority = None

        for ruleset in p_rule_sets:
            context_name = ruleset.context or self._default_context_rule_handler_name
            context_rule_handler = self._context_rule_handlers.get(context_name)

            if context_rule_handler is None:
                raise configuration.ConfigurationException("invalid rule set context '%s'" % ruleset.context)

            active = context_rule_handler.is_active(p_reference_date=p_reference_date,
                                                    p_details=ruleset.context_details)

            if active and (max_priority is None or ruleset.priority > max_priority):
                max_priority = ruleset.priority
                active_ruleset = ruleset

        return active_ruleset

    def check_free_play(self, p_rule_set: RuleSetConfigModel, p_rule_result_info: RuleResultInfo):

        if p_rule_set.free_play:
            p_rule_result_info.applying_rules = p_rule_result_info.applying_rules | rule_result_info.RULE_FREE_PLAY
            p_rule_result_info.applying_rule_text_templates.append(
                (_("Free Play"), {})
            )

    def check_time_of_day(self, p_rule_set: RuleSetConfigModel, p_stat_info: process_statistics.ProcessStatisticsInfo,
                          p_rule_result_info: RuleResultInfo):

        if p_rule_result_info.skip_negative_checks():
            # shortcut because granting playtime has higher priority
            return

        if p_rule_set.min_time_of_day is not None and p_stat_info.reference_time.timetz() < p_rule_set.min_time_of_day:
            p_rule_result_info.applying_rules = p_rule_result_info.applying_rules | rule_result_info.RULE_TOO_EARLY

            p_rule_result_info.applying_rule_text_templates.append(
                (_("No activity before {hh_mm} hours"), {"hh_mm": p_rule_set.min_time_of_day.strftime("%H:%M")})
            )
            p_rule_result_info.set_minutes_left_in_session(p_minutes_left=0)

        if p_rule_set.max_time_of_day is not None:
            if p_stat_info.reference_time.timetz() > p_rule_set.max_time_of_day:
                p_rule_result_info.applying_rules = p_rule_result_info.applying_rules | rule_result_info.RULE_TOO_LATE
                p_rule_result_info.applying_rule_text_templates.append(
                    (_("No activity after {hh_mm} hours"), {"hh_mm": p_rule_set.max_time_of_day.strftime("%H:%M")})
                )
                p_rule_result_info.set_minutes_left_in_session(p_minutes_left=0)

            max_time_of_day_as_date = datetime.datetime.combine(datetime.date.today(), p_rule_set.max_time_of_day)
            time_left_in_seconds = (max_time_of_day_as_date - p_stat_info.reference_time).total_seconds()
            time_left_in_minutes = max(int((time_left_in_seconds + 30) / 60), 0)
            p_rule_result_info.set_minutes_left_today(p_minutes_left=time_left_in_minutes)

            #if not p_rule_result_info.activity_granted():
            p_rule_result_info.set_minutes_left_in_session(p_minutes_left=time_left_in_minutes)

            p_rule_result_info.check_approaching_logout(
                p_warning_before_logout=self._config.warning_before_logout, p_rule=rule_result_info.RULE_TOO_LATE)

    def check_time_per_day(self, p_rule_set: RuleSetConfigModel, p_stat_info: process_statistics.ProcessStatisticsInfo,
                           p_rule_result_info: RuleResultInfo):

        if p_rule_result_info.skip_negative_checks():
            # shortcut because granting playtime has higher priority
            return

        if p_rule_set.max_time_per_day is not None:
            todays_activity_duration = p_stat_info.todays_activity_duration

            if todays_activity_duration >= p_rule_set.max_time_per_day:
                if p_rule_set.max_time_per_day == 0:
                    p_rule_result_info.applying_rules = p_rule_result_info.applying_rules | rule_result_info.RULE_DAY_BLOCKED
                    p_rule_result_info.applying_rule_text_templates.append(
                        (_("Day blocked: no activity permitted"), {})
                    )

                else:
                    p_rule_result_info.applying_rules = p_rule_result_info.applying_rules | rule_result_info.RULE_TIME_PER_DAY
                    p_rule_result_info.applying_rule_text_templates.append(
                        (_("Activity limited to {hh_mm} per day"),
                         {"hh_mm": tools.get_duration_as_string(p_seconds=p_rule_set.max_time_per_day,
                                                                p_include_seconds=False)})
                    )

            if p_rule_set.max_time_per_day >= 0:
                time_left_in_seconds = p_rule_set.max_time_per_day - todays_activity_duration
                time_left_in_minutes = int((time_left_in_seconds + 30) / 60)
                p_rule_result_info.set_minutes_left_today(p_minutes_left=time_left_in_minutes)

                p_rule_result_info.set_minutes_left_in_session(p_minutes_left=time_left_in_minutes)
                p_rule_result_info.check_approaching_logout(
                    p_warning_before_logout=self._config.warning_before_logout,
                    p_rule=rule_result_info.RULE_TIME_PER_DAY)

    def check_activity_duration(self, p_rule_set: RuleSetConfigModel,
                                p_stat_info: process_statistics.ProcessStatisticsInfo,
                                p_rule_result_info: RuleResultInfo):

        if p_rule_result_info.skip_negative_checks():
            # shortcut because granting playtime has higher priority
            return

        if p_rule_set.max_activity_duration is not None:
            current_activity_duration = p_stat_info.current_activity_duration

            if current_activity_duration is not None:
                if current_activity_duration > p_rule_set.max_activity_duration:
                    p_rule_result_info.applying_rules = p_rule_result_info.applying_rules | rule_result_info.RULE_ACTIVITY_DURATION
                    p_rule_result_info.applying_rule_text_templates.append(
                        (_("No activity exceeding {hh_mm}"),
                         {"hh_mm": tools.get_duration_as_string(p_seconds=p_rule_set.max_activity_duration,
                                                                p_include_seconds=False)})
                    )

                else:
                    time_left_in_seconds = p_rule_set.max_activity_duration - current_activity_duration
                    time_left_in_minutes = int((time_left_in_seconds + 30) / 60)

                    p_rule_result_info.set_minutes_left_in_session(p_minutes_left=time_left_in_minutes)
                    p_rule_result_info.check_approaching_logout(
                        p_warning_before_logout=self._config.warning_before_logout,
                        p_rule=rule_result_info.RULE_ACTIVITY_DURATION)

    @staticmethod
    def check_min_break(p_rule_set: RuleSetConfigModel, p_stat_info: process_statistics.ProcessStatisticsInfo,
                        p_rule_result_info: RuleResultInfo):

        if p_rule_result_info.skip_negative_checks():
            # shortcut because granting playtime has higher priority
            return

        if p_rule_result_info.datetime_is_permitted_by_extension(p_datetime=p_stat_info.reference_time.timetz()):
            return

        if p_rule_set.min_break is not None and p_rule_set.max_activity_duration is not None:
            seconds_since_last_activity = p_stat_info.seconds_since_last_activity

            if p_stat_info.previous_activity_duration is not None and p_rule_set.max_activity_duration > 0:
                fraction_used = min(1.0 * p_stat_info.previous_activity_duration / p_rule_set.max_activity_duration,
                                    1.0)
                min_relative_break = fraction_used * p_rule_set.min_break

            else:
                min_relative_break = p_rule_set.min_break

            if seconds_since_last_activity is not None and seconds_since_last_activity < min_relative_break:
                seconds_to_go = min_relative_break - seconds_since_last_activity
                p_rule_result_info.applying_rules = p_rule_result_info.applying_rules | rule_result_info.RULE_MIN_BREAK
                p_rule_result_info.applying_rule_text_templates.append(
                    (_("Minimum break time {hh_mm} not reached, {hh_mm_to_go} to go"),
                     {"hh_mm": tools.get_duration_as_string(p_seconds=min_relative_break, p_include_seconds=False),
                      "hh_mm_to_go": tools.get_duration_as_string(p_seconds=seconds_to_go, p_include_seconds=False)})
                )
                p_rule_result_info.break_minutes_left = int(
                    (min_relative_break - seconds_since_last_activity + 30) / 60)

    def check_info_rules(self, p_rule_set: RuleSetConfigModel, p_stat_info: process_statistics.ProcessStatisticsInfo,
                         p_rule_result_info: RuleResultInfo):

        if p_rule_result_info.minutes_left_today is not None:
            p_rule_result_info.applying_rules |= rule_result_info.INFO_REMAINING_PLAYTIME
            p_rule_result_info.applying_rule_text_templates.append(
                (_("Remaining play time today: {hh_mm}"),
                 {"hh_mm": tools.get_duration_as_string(p_seconds=60 * p_rule_result_info.minutes_left_today,
                                                        p_include_seconds=False)})
            )

        current_activity_duration = p_stat_info.current_activity_duration

        if current_activity_duration is not None and p_rule_result_info.get_minutes_left_in_session() is not None:
            p_rule_result_info.applying_rules |= rule_result_info.INFO_REMAINING_PLAYTIME_THIS_SESSION
            p_rule_result_info.applying_rule_text_templates.append(
                (_("Remaining play time in current session: {hh_mm}"),
                 {"hh_mm": tools.get_duration_as_string(
                     p_seconds=60 * p_rule_result_info.get_minutes_left_in_session(), p_include_seconds=False)})
            )

        if p_stat_info.current_activity_start_time is not None and \
                p_rule_result_info.get_minutes_left_in_session() is not None:
            session_end_datetime = \
                p_stat_info.current_activity_start_time + datetime.timedelta(
                    minutes=p_rule_result_info.get_minutes_left_in_session())
            p_rule_result_info.set_session_end_datetime(p_session_end_datetime=session_end_datetime)

        # If no session restriction has been detected so far we use a specific notification for the restriction
        # given by the time extension...
        if p_rule_result_info.skip_negative_checks():
            p_rule_result_info.minutes_left_in_session = None

        else:
            if (p_rule_result_info.minutes_left_in_time_extension is not None and
                    p_rule_result_info.minutes_left_in_session is None):
                p_rule_result_info.check_approaching_logout(p_warning_before_logout=self._config.warning_before_logout,
                                                            p_rule=rule_result_info.RULE_TIME_EXTENSION)

    def process_rule_sets_for_user(self, p_rule_sets, p_stat_info, p_active_time_extension,
                                   p_reference_time, p_rule_override, p_locale):

        active_rule_set = self.get_active_ruleset(p_reference_date=p_reference_time, p_rule_sets=p_rule_sets)

        rule_result_info = RuleResultInfo(p_default_rule_set=active_rule_set,
                                          p_rule_override=p_rule_override,
                                          p_user=p_stat_info.notification_name,
                                          p_locale=p_locale)

        rule_result_info.locale = p_locale

        if active_rule_set is not None:
            rule_result_info.add_time_extension_meta_data(p_active_time_extension=p_active_time_extension,
                                                          p_reference_time=p_reference_time)

            # Rules granting playtime
            self.check_free_play(p_rule_set=rule_result_info.effective_rule_set, p_rule_result_info=rule_result_info)

            # Rules denying playtime
            self.check_time_of_day(p_rule_set=rule_result_info.effective_rule_set, p_stat_info=p_stat_info,
                                   p_rule_result_info=rule_result_info)
            self.check_time_per_day(p_rule_set=rule_result_info.effective_rule_set, p_stat_info=p_stat_info,
                                    p_rule_result_info=rule_result_info)
            self.check_activity_duration(p_rule_set=rule_result_info.effective_rule_set, p_stat_info=p_stat_info,
                                         p_rule_result_info=rule_result_info)
            self.check_min_break(p_rule_set=rule_result_info.effective_rule_set, p_stat_info=p_stat_info,
                                 p_rule_result_info=rule_result_info)

            # This check must be the last in the set because it uses results stored into rule_result_info
            # by the other checks!
            self.check_info_rules(p_rule_set=rule_result_info.effective_rule_set, p_stat_info=p_stat_info,
                                  p_rule_result_info=rule_result_info)

        if not rule_result_info.activity_allowed():
            fmt = "Activity prohibited for user %s: applying rules(s) %d" % (
                p_stat_info.username, rule_result_info.applying_rules)
            self._logger.debug(fmt)

        return rule_result_info
