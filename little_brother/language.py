# -*- coding: utf-8 -*-

# Copyright (C) 2019-2021  Marcus Rickert
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

import gettext
import os

from little_brother import rule_result_info
from python_base_app import log_handling

_ = lambda x, y=None: x


class Language:

    def __init__(self):

        self._logger = log_handling.get_logger(self.__class__.__name__)

        self.init_labels_and_notifications()
        self._locale_dir = os.path.join(os.path.dirname(__file__), "translations")

    def init_labels_and_notifications(self):

        self.text_no_time_left = _("{user}, you do not have computer time left today.\nYou will be logged out.")
        self.text_no_time_left_approaching = _(
            "{user}, you only have {minutes_left_in_session} minutes left today.\nPlease, log out.")
        self.text_no_time_left_in_time_extension = _(
            "{user}, you only have {minutes_left_in_session} minutes left in your time extension.\nPlease, log out.")
        self.text_no_time_today = _("{user}, you do not have any computer time today.\nYou will be logged out.")
        self.text_too_early = _("{user}, it is too early to use the computer.\nYou will be logged out.")
        self.text_too_late = _("{user}, it is too late to use the computer.\nYou will be logged out.")
        self.text_too_late_approaching = _(
            "{user}, in {minutes_left_in_session} minutes it will be too late to use the computer.\nPlease, log out.")
        self.text_need_break = _("{user}, you have to take a break.\nYou will be logged out.")
        self.text_need_break_approaching = _(
            "{user}, in {minutes_left_in_session} minutes you will have to take a break.\nPlease, log out.")
        self.text_min_break = _(
            "{user}, your break will only be over in {break_minutes_left} minutes.\nYou will be logged out.")
        self.text_limited_session_start = _(
            "Hello {user}, you will be allowed to play for {minutes_left_in_session} minutes\nin this session.")
        self.text_unlimited_session_start = _("Hello {user}, you have unlimited playtime in this session.")
        self.text_prohibited_process = _("{user}, you are not allowed to use {process_name} with this account. "
                                         "The program will be terminated.")

    def get_text_limited_session_start(self, p_locale, p_variables):

        t = gettext.translation('messages', localedir=self._locale_dir,
                                languages=[p_locale], fallback=True)
        return t.gettext(self.text_limited_session_start).format(**p_variables)

    def get_text_unlimited_session_start(self, p_locale, p_variables):

        t = gettext.translation('messages', localedir=self._locale_dir,
                                languages=[p_locale], fallback=True)
        return t.gettext(self.text_unlimited_session_start).format(**p_variables)

    def get_text_prohibited_process(self, p_locale, p_variables):

        t = gettext.translation('messages', localedir=self._locale_dir,
                                languages=[p_locale], fallback=True)
        return t.gettext(self.text_prohibited_process).format(**p_variables)

    def pick_text_for_ruleset(self, p_rule_result_info):

        t = gettext.translation('messages', localedir=self._locale_dir,
                                languages=[p_rule_result_info.locale], fallback=True)

        if p_rule_result_info.applying_rules & rule_result_info.RULE_TIME_PER_DAY:
            return t.gettext(self.text_no_time_left).format(**p_rule_result_info.args)

        elif p_rule_result_info.applying_rules & rule_result_info.RULE_DAY_BLOCKED:
            return t.gettext(self.text_no_time_today).format(**p_rule_result_info.args)

        elif p_rule_result_info.applying_rules & rule_result_info.RULE_TOO_EARLY:
            return t.gettext(self.text_too_early).format(**p_rule_result_info.args)

        elif p_rule_result_info.applying_rules & rule_result_info.RULE_TOO_LATE:
            return t.gettext(self.text_too_late).format(**p_rule_result_info.args)

        elif p_rule_result_info.applying_rules & rule_result_info.RULE_ACTIVITY_DURATION:
            return t.gettext(self.text_need_break).format(**p_rule_result_info.args)

        elif p_rule_result_info.applying_rules & rule_result_info.RULE_MIN_BREAK:
            return t.gettext(self.text_min_break).format(**p_rule_result_info.args)

        else:
            fmt = "pick_text_for_ruleset(): cannot derive text for rule result %d" % p_rule_result_info.applying_rules
            self._logger.warning(fmt)
            return ""

    def pick_text_for_approaching_logout(self, p_rule_result_info):

        t = gettext.translation('messages', localedir=self._locale_dir,
                                languages=[p_rule_result_info.locale], fallback=True)

        if p_rule_result_info.approaching_logout_rules & rule_result_info.RULE_ACTIVITY_DURATION:
            return t.gettext(self.text_need_break_approaching).format(**p_rule_result_info.args)

        elif p_rule_result_info.approaching_logout_rules & rule_result_info.RULE_TOO_LATE:
            return t.gettext(self.text_too_late_approaching).format(**p_rule_result_info.args)

        elif p_rule_result_info.approaching_logout_rules & rule_result_info.RULE_TIME_PER_DAY:
            return t.gettext(self.text_no_time_left_approaching).format(**p_rule_result_info.args)

        elif p_rule_result_info.approaching_logout_rules & rule_result_info.RULE_TIME_EXTENSION:
            return t.gettext(self.text_no_time_left_in_time_extension).format(**p_rule_result_info.args)

        else:
            fmt = "pick_text_for_approaching_logout(): cannot derive text for rule result {mask}"
            self._logger.warning(fmt.format(mask=p_rule_result_info.approaching_logout_rules))
            return ""
