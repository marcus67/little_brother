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

import wtforms

from little_brother.context_rule_handler import AbstractContextRuleHandler
from python_base_app import configuration

# Dummy function to trigger extraction by pybabel...
_ = lambda x: x

DEFAULT_CONTEXT_RULE_HANDLER_NAME = _("default")
WEEKPLAN_CONTEXT_RULE_HANDLER_NAME = _("weekplan")

VALID_ACTIVE_DAY_CHARACTERS = "1YX"
VALID_INACTIVE_DAY_CHARACTERS = "0N-"

WEEKPLAN_PREDEFINED_DETAILS = {
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


class DefaultContextRuleHandler(AbstractContextRuleHandler):

    def __init__(self):
        super().__init__(p_context_name=DEFAULT_CONTEXT_RULE_HANDLER_NAME)

    def is_active(self, p_reference_date, p_details):
        return True


class WeekplanContextRuleHandler(AbstractContextRuleHandler):

    def __init__(self):

        super().__init__(p_context_name=WEEKPLAN_CONTEXT_RULE_HANDLER_NAME)

    def is_active(self, p_reference_date, p_details):

        if p_details is None:
            raise configuration.ConfigurationException("Weekday context without context details")

        p_details = p_details.lower()

        if p_details in WEEKPLAN_PREDEFINED_DETAILS:
            weekday_string = WEEKPLAN_PREDEFINED_DETAILS[p_details]

        elif len(p_details) == 7:
            weekday_string = p_details

        else:
            fmt = "invalid context details '{details}' for context {name}"
            raise configuration.ConfigurationException(fmt.format(details=p_details, name=self.context_name))

        time_tuple = p_reference_date.timetuple()

        return weekday_string.upper()[time_tuple.tm_wday] in VALID_ACTIVE_DAY_CHARACTERS

    def get_choices(self):

        return WEEKPLAN_PREDEFINED_DETAILS.keys()

    def validate_context_details(self, p_context_detail):

        if p_context_detail in WEEKPLAN_PREDEFINED_DETAILS:
            return

        invalid = False

        if len(p_context_detail) != 7:
            invalid = True

        else:
            for c in p_context_detail.upper():
                if c not in VALID_ACTIVE_DAY_CHARACTERS + VALID_INACTIVE_DAY_CHARACTERS:
                    invalid = True

        if invalid:
            localized_choices = "'" + "', '".join(
                [self.locale_helper.gettext(p_text=choice) for choice in WEEKPLAN_PREDEFINED_DETAILS.keys()]) + "'"

            fmt = _("Invalid detail '{detail}'. Must be one of {choices} or " \
                    "have length seven characters denoting the days of the week (starting with Monday) and " \
                    "consist of active letters '{valid_active_characters}' " \
                    "and inactive letters '{valid_inactive_characters}'")
            fmt = self.locale_helper.gettext(fmt)
            msg = fmt.format(detail=p_context_detail, choices=localized_choices,
                             valid_active_characters=VALID_ACTIVE_DAY_CHARACTERS,
                             valid_inactive_characters=VALID_INACTIVE_DAY_CHARACTERS)

            raise wtforms.validators.ValidationError(message=str(msg))

    def summary(self, p_context_detail):

        return [_("Selected Days"), ": ", p_context_detail]
