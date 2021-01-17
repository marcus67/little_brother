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

import os.path

DIR_NAME = 'little-brother'
APPLICATION_USER = 'little-brother'

DEFAULT_PROCESS_NAME_PATTERN = "systemd|bash|sh|csh|tsh"
DEFAULT_USER2DEVICE_PERCENT = 100

DEFAULT_DEVICE_SAMPLE_SIZE = 10
DEFAULT_DEVICE_MIN_ACTIVITY_DURATION = 120
DEFAULT_DEVICE_MAX_ACTIVE_PING_DELAY = 50

LANGUAGES = {
    'en': 'English',
    'de': 'Deutsch',
    'fr': 'Français',
    'hr': 'Hrvatski',
    'it': 'Italiano',
    'nl': 'Nederlands',
    'fi': 'Suomen kieli',
    'tr': 'Türkçe',
    'ru': 'Русский язык',
    'ja': '日本語',
    'bn': 'বাংলা',
    'th': 'ภาษาไทย',
    'da': 'Dansk',
    'es': 'Español'
}

TEXT_SEPERATOR = " 🞄 "

API_URL = "/api"
API_REL_URL_EVENTS = "events"
API_URL_EVENTS = os.path.join(API_URL, API_REL_URL_EVENTS)

API_REL_URL_STATUS = "status"
API_URL_STATUS = os.path.join(API_URL, API_REL_URL_STATUS)

API_URL_PARAM_USERNAME = "username"

JSON_HOSTNAME = "hostname"
JSON_EVENTS = "events"
JSON_CLIENT_STATS = "client_stats"
JSON_RULESETS = "rulesets"
JSON_USERNAME = "username"
JSON_PROCESS_NAME_PATTERN = "process_name_pattern"
JSON_ACTIVE = "active"
JSON_ACCESS_TOKEN = "secret"
JSON_ERROR = "error"

HTTP_STATUS_CODE_OK = 200
HTTP_STATUS_CODE_UNAUTHORIZED = 401
HTTP_STATUS_CODE_NOT_FOUND = 404