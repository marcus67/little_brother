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

import wtforms

from python_base_app import custom_fields
from python_base_app import custom_form


class UserForm(custom_form.ModelForm):

    first_name = wtforms.StringField("FirstName")
    last_name = wtforms.StringField("LastName")
    locale = wtforms.StringField("Locale")
    process_name_pattern = wtforms.StringField("ProcessNamePattern")
    active = custom_fields.BooleanField("Active")

class NewUserForm(custom_form.ModelForm):

    username = wtforms.SelectField("NewUsername")

class DeviceForm(custom_form.ModelForm):

    device_name = wtforms.StringField("FirstName")
    hostname = wtforms.StringField("FirstName")
    min_activity_duration = wtforms.IntegerField("MinActivityDuration")
    max_active_ping_delay = wtforms.IntegerField("MaxActivePingDelay")
    sample_size = wtforms.IntegerField("SampleSize")

class RulesetForm(custom_form.ModelForm):

    context_label = wtforms.StringField("ContextLabel")
    context = wtforms.SelectField("Context")
    context_details = wtforms.StringField("ContextDetails")
    min_time_of_day = custom_fields.TimeField("MinTimeOfDay")
    max_time_of_day = custom_fields.TimeField("MaxTimeOfDay")
    max_time_per_day = custom_fields.DurationField("MaxTimePerDay")
    min_break = custom_fields.DurationField("MinBreak")
    free_play = custom_fields.BooleanField("FreePlay")
    max_activity_duration = custom_fields.DurationField("MaxActivityDuration")
