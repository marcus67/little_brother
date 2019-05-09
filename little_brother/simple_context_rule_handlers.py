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

from little_brother import context_rule_handler
from python_base_app import configuration

# Dummy function to trigger extraction by pybabel...
_ = lambda x: x

DEFAULT_CONTEXT_RULE_HANDLER_NAME = _("default")
WEEKDAY_CONTEXT_RULE_HANDLER_NAME = _("weekday")

VALID_ACTIVE_DAY_CHARACTERS = "1YX"

WEEKDAY_PREDEFINED_DETAILS = {
    _("weekend"): "-----11",
    _("weekdays"): "11111--",
    _("mondays"): "1------",
    _("tuesdays"): "-1-----",
    _("wednesdays"): "--1----",
    _("thursdays"): "---1---",
    _("fridays"): "----1--",
    _("saturdays"): "-----1-",
    _("sundays"): "------1",
}


class DefaultContextRuleHandler(context_rule_handler.AbstractContextRuleHandler):

    def __init__(self):
        super().__init__(p_context_name=DEFAULT_CONTEXT_RULE_HANDLER_NAME)

    def is_active(self, p_reference_date, p_details):
        return True


class WeekdayContextRuleHandler(context_rule_handler.AbstractContextRuleHandler):

    def __init__(self):

        super().__init__(p_context_name=WEEKDAY_CONTEXT_RULE_HANDLER_NAME)

    def is_active(self, p_reference_date, p_details):

        if p_details is None:
            raise configuration.ConfigurationException("Weekday context without context details")

        p_details = p_details.lower()

        if p_details in WEEKDAY_PREDEFINED_DETAILS:
            weekday_string = WEEKDAY_PREDEFINED_DETAILS[p_details]

        elif len(p_details) == 7:
            weekday_string = p_details

        else:
            fmt = "invalid context details '{details}' for context {name}"
            raise configuration.ConfigurationException(fmt.format(details=p_details, name=self.context_name))

        time_tuple = p_reference_date.timetuple()

        return weekday_string[time_tuple.tm_wday] in VALID_ACTIVE_DAY_CHARACTERS
