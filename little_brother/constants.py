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

import os.path

UNKNOWN = "<unknown>"

DIR_NAME = 'little-brother'
APPLICATION_USER = 'little-brother'
APPLICATION_NAME = 'LittleBrother'

DEFAULT_RULE_SET_PRIORITY = 1

DEFAULT_PROCESS_NAME_PATTERN = "systemd|bash|sh|csh|tsh"
DEFAULT_USER2DEVICE_PERCENT = 100

DEFAULT_DEVICE_NEW_NAME_PATTERN = "New device {id}"
DEFAULT_DEVICE_HOST_NAME = "localhost"
DEFAULT_DEVICE_SAMPLE_SIZE = 10
DEFAULT_DEVICE_MIN_ACTIVITY_DURATION = 120
DEFAULT_DEVICE_MAX_ACTIVE_PING_DELAY = 50

DEFAULT_LOCALE = "en_US"

DEFAULT_ACCESS_CODE = "REPLACE-THIS-VALUE-WITH-A-STRONG-SECRET"

# VALID DATA RANGES

DEVICE_MIN_MIN_ACTIVITY_DURATION = 1
DEVICE_MAX_MIN_ACTIVITY_DURATION = 1000

DEVICE_MIN_MAX_ACTIVE_PING_DELAY = 1
DEVICE_MAX_MAX_ACTIVE_PING_DELAY = 1000

DEVICE_MIN_SAMPLE_SIZE = 5
DEVICE_MAX_SAMPLE_SIZE = 100

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

TEXT_SEPERATOR = ' <i style="font-size: 0.5rem; vertical-align: +25%" class="fas fa-circle fa-sm"></i> '

API_URL = "/api"
API_REL_URL_EVENTS = "events"
API_URL_EVENTS = os.path.join(API_URL, API_REL_URL_EVENTS)

API_REL_URL_STATUS = "status"
API_URL_STATUS = os.path.join(API_URL, API_REL_URL_STATUS)

API_REL_URL_REQUEST_TIME_EXTENSION = "request-time-extension"
API_URL_REQUEST_TIME_EXTENSION = os.path.join(API_URL, API_REL_URL_REQUEST_TIME_EXTENSION)

API_URL_PARAM_USERNAME = "username"
API_URL_PARAM_SECRET = "secret"
API_URL_PARAM_EXTENSION_LENGTH = "extension_length"

JSON_HOSTNAME = "hostname"
JSON_EVENTS = "events"
JSON_CLIENT_STATS = "client_stats"
JSON_RULESETS = "rulesets"
JSON_USERNAME = "username"
JSON_PROCESS_NAME_PATTERN = "process_name_pattern"
JSON_PROHIBITED_PROCESS_NAME_PATTERN = "prohibited_process_name_pattern"
JSON_ACTIVE = "active"
JSON_ACCESS_TOKEN = "secret"
JSON_ERROR = "error"
JSON_USER_CONFIG = "config:user_config"
JSON_MAXIMUM_TIME_WITHOUT_SEND = "config:maximum_time_without_send"

# See https://de.wikipedia.org/wiki/HTTP-Statuscode
HTTP_STATUS_CODE_OK = 200
HTTP_STATUS_CODE_UNAUTHORIZED = 401
HTTP_STATUS_CODE_NOT_FOUND = 404
HTTP_STATUS_CODE_RANGE_NOT_SATISFIABLE = 416

INTERNAL_ERROR_HTML_TEMPLATE = "internal_error.template.html"

ABOUT_BLUEPRINT_NAME = "about"
ABOUT_HTML_TEMPLATE = "about.template.html"
ABOUT_REL_URL = "about"
ABOUT_VIEW_NAME = "main_view"

ADMIN_BLUEPRINT_NAME = "admin"
ADMIN_HTML_TEMPLATE = "admin.template.html"
ADMIN_REL_URL = "admin"
ADMIN_VIEW_NAME = "main_view"

DEVICES_BLUEPRINT_NAME = "devices"
DEVICES_HTML_TEMPLATE = "devices.template.html"
DEVICES_REL_URL = "devices"
DEVICES_VIEW_NAME = "main_view"

LOGIN_BLUEPRINT_NAME = "login"
LOGIN_HTML_TEMPLATE = "login.template.html"

STATUS_BLUEPRINT_NAME = "status"
STATUS_HTML_TEMPLATE = "status.template.html"
STATUS_REL_URL = "status"
STATUS_VIEW_NAME = "main_view"

TOPOLOGY_BLUEPRINT_NAME = "topology"
TOPOLOGY_HTML_TEMPLATE = "topology.template.html"
TOPOLOGY_REL_URL = "topology"
TOPOLOGY_VIEW_NAME = "main_view"

USERS_BLUEPRINT_NAME = "users"
USERS_HTML_TEMPLATE = "users.template.html"
USERS_REL_URL = "users"
USERS_VIEW_NAME = "main_view"

CSS_CLASS_EMPHASIZE_RULE_OVERRIDE = "rule-override"

SOURCEFORGE_VERSION_RSS_URL = "https://sourceforge.net/projects/little-brother/rss?path=/"
SOURCEFORGE_VERSION_XPATH = "./channel/item/title"
SOURCEFORGE_VERSION_REGEX = "^/([a-z]+)/little-brother_([.0-9]+)_([0-9]+)\.deb$"

