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

from little_brother import constants
from python_base_app import custom_fields
from python_base_app import custom_form
from python_base_app import pinger

_ = lambda x: x

a_pinger = pinger.Pinger()


# TODO: edit fields should be marked by special color when containing modified (and not yet saved ) value

def regex_validator(_form, field):
    if field.data is not None:
        sub_patterns = field.data.replace('\r', '').split('\n')

        for sub_pattern in sub_patterns:
            if len(sub_pattern.strip()) == 1:
                raise wtforms.validators.ValidationError(_("Sub pattern must be longer than one character"))


class UserForm(custom_form.ModelForm):
    first_name = wtforms.StringField("FirstName")
    last_name = wtforms.StringField("LastName")
    locale = wtforms.SelectField("Locale")
    process_name_pattern = wtforms.TextAreaField("ProcessNamePattern",
                                                 validators=[regex_validator])
    prohibited_process_name_pattern = wtforms.TextAreaField("ProhibitedProcessNamePattern",
                                                 validators=[regex_validator])
    active = custom_fields.BooleanField("Active")


class NewUserForm(custom_form.ModelForm):
    username = wtforms.SelectField("NewUsername")


class NewUser2DeviceForm(custom_form.ModelForm):
    device_id = wtforms.SelectField("NewDeviceId")

# Dummy so that the device HTML page has at least one form
class NewDeviceForm(custom_form.ModelForm):
    pass

# Dummy so that the device HTML page has at least one form
class DummyAdminForm(custom_form.ModelForm):
    pass


def dns_validator(_form, field):
    if not a_pinger.is_valid_ping(field.data):
        raise wtforms.validators.ValidationError(_("Not a valid host address"))


class DeviceForm(custom_form.ModelForm):
    # TODO: trim device_name during validation
    device_name = wtforms.StringField("DeviceName",
                                      validators=[wtforms.validators.DataRequired(),
                                                  custom_fields.Uniqueness()])
    # TODO: trim hostname during validation
    hostname = wtforms.StringField("Hostname",
                                   validators=[wtforms.validators.DataRequired(),
                                               dns_validator,
                                               custom_fields.Uniqueness()])
    min_activity_duration = wtforms.IntegerField("MinActivityDuration",
                                                 validators=[wtforms.validators.NumberRange(
                                                     min=constants.DEVICE_MIN_MIN_ACTIVITY_DURATION,
                                                     max=constants.DEVICE_MAX_MIN_ACTIVITY_DURATION)])
    max_active_ping_delay = wtforms.IntegerField("MaxActivePingDelay",
                                                 validators=[wtforms.validators.NumberRange(
                                                     min=constants.DEVICE_MIN_MAX_ACTIVE_PING_DELAY,
                                                     max=constants.DEVICE_MAX_MAX_ACTIVE_PING_DELAY)])
    sample_size = wtforms.IntegerField("SampleSize",
                                       validators=[wtforms.validators.NumberRange(
                                           min=constants.DEVICE_MIN_SAMPLE_SIZE,
                                           max=constants.DEVICE_MAX_SAMPLE_SIZE)])


def create_rulesets_form(prefix, p_localized_context_details, p_context_choices, p_context_details_filters):
    class RulesetForm(custom_form.ModelForm):
        context_label = wtforms.StringField("ContextLabel")
        context = wtforms.SelectField("Context", choices=p_context_choices)
        context_details = custom_fields.LocalizedField("ContextDetails", p_values=p_localized_context_details,
                                                       filters=p_context_details_filters)
        min_time_of_day = custom_fields.TimeField("MinTimeOfDay")
        max_time_of_day = custom_fields.TimeField("MaxTimeOfDay")
        max_time_per_day = custom_fields.DurationField("MaxTimePerDay")
        min_break = custom_fields.DurationField("MinBreak")
        free_play = custom_fields.BooleanField("FreePlay")
        max_activity_duration = custom_fields.DurationField("MaxActivityDuration")
        optional_time_per_day = custom_fields.DurationField("OptionalTimePerDay")

    return RulesetForm(prefix=prefix, meta={'csrf': True})


class User2DeviceForm(custom_form.ModelForm):
    percent = wtforms.IntegerField("Percent", validators=[wtforms.validators.NumberRange(min=1, max=100)])
    active = custom_fields.BooleanField("Active")
