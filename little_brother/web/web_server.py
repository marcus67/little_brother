# -*- coding: utf-8 -*-

# Copyright (C) 2019-21  Marcus Rickert
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
import gettext
import os

import babel.dates
import flask
import flask_babel
import humanize

import little_brother
from little_brother import app_control
from little_brother import constants
from little_brother.api import api_view_handler
from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn
from little_brother.web.about_view_handler import AboutViewHandler
from little_brother.web.admin_view_handler import AdminViewHandler
from little_brother.web.devices_view_handler import DevicesViewHandler
from little_brother.web.login_view_handler import LoginViewHandler
from little_brother.web.status_view_handler import StatusViewHandler
from little_brother.web.topology_view_handler import TopologyViewHandler
from little_brother.web.users_view_handler import UsersViewHandler
from python_base_app import base_web_server
from python_base_app import locale_helper
from python_base_app import tools

SECTION_NAME = "StatusServer"

_ = lambda x: x


class StatusServerConfigModel(base_web_server.BaseWebServerConfigModel):

    def __init__(self):
        super().__init__(p_section_name=SECTION_NAME)

        self.initializr_rel_dir = 'contrib/initializr'
        self.js_cookie_rel_dir = 'contrib/js-cookie'

        self.datetime_format = "%d.%m.%y %H:%M"
        self.time_format = "%H:%M"
        self.date_format = "%a %d.%m.%Y"
        self.simple_date_format = "%d.%m.%Y"


class StatusServer(PersistenceDependencyInjectionMixIn, base_web_server.BaseWebServer):

    def __init__(self,
                 p_config,
                 p_package_name,
                 p_app_control,
                 p_master_connector,
                 p_is_master,
                 p_locale_helper,
                 p_base_gettext=None,
                 p_languages=None,
                 p_user_handler=None):

        self._api_view_handler = None
        self._about_view_handler = AboutViewHandler(p_package=little_brother, p_languages=p_languages)
        self._admin_view_handler = AdminViewHandler(p_package=little_brother)
        self._devices_view_handler = DevicesViewHandler(p_package=little_brother)
        self._login_view_handler = LoginViewHandler(p_package=little_brother, p_languages=p_languages)
        self._status_view_handler = StatusViewHandler(p_package=little_brother)
        self._topology_view_handler = TopologyViewHandler(p_package=little_brother)
        self._users_view_handler = UsersViewHandler(p_package=little_brother, p_languages=p_languages)

        super(StatusServer, self).__init__(
            p_config=p_config,
            p_name="Web Server",
            p_package_name=p_package_name,
            p_user_handler=p_user_handler,
            p_login_view=self._login_view_handler.login_view,
            p_logged_out_endpoint=constants.STATUS_BLUEPRINT_NAME + '.' + constants.STATUS_VIEW_NAME)

        # This blueprint handles static resources...
        self._blueprint = flask.Blueprint("little_brother", little_brother.__name__, static_folder="static")
        self._app.register_blueprint(self._blueprint, url_prefix=self._config.base_url)

        self._about_view_handler.register(p_app=self._app, p_url_prefix=self._config.base_url)
        self._admin_view_handler.register(p_app=self._app, p_url_prefix=self._config.base_url)
        self._devices_view_handler.register(p_app=self._app, p_url_prefix=self._config.base_url)
        self._login_view_handler.register(p_app=self._app, p_url_prefix=self._config.base_url)
        self._status_view_handler.register(p_app=self._app, p_url_prefix=self._config.base_url)
        self._topology_view_handler.register(p_app=self._app, p_url_prefix=self._config.base_url)
        self._users_view_handler.register(p_app=self._app, p_url_prefix=self._config.base_url)

        self._is_master: bool = p_is_master
        self.app_control: app_control.AppControl = p_app_control
        self._master_connector = p_master_connector

        self._stat_dict = {}
        self._server_exception: Exception = None
        self._locale_helper: locale_helper.LocaleHelper = p_locale_helper
        self._languages = p_languages
        self._base_gettext = p_base_gettext
        self._langs = {}
        self._localedir = os.path.join(os.path.dirname(__file__), "../translations")

        if self._languages is None:
            self._languages = {'en': "English"}

        if self._base_gettext is None:
            self._base_gettext = lambda text: text

        if self._is_master:
            self._api_view_handler = api_view_handler.ApiViewHandler(p_app=self._app)
            self._csrf.exempt(self._api_view_handler.blueprint)

        self._app.jinja_env.filters['datetime_to_string'] = self.format_datetime
        self._app.jinja_env.filters['time_to_string'] = self.format_time
        self._app.jinja_env.filters['date_to_string'] = self.format_date
        self._app.jinja_env.filters['simple_date_to_string'] = self.format_simple_date
        self._app.jinja_env.filters['seconds_to_string'] = self.format_seconds
        self._app.jinja_env.filters['boolean_to_string'] = self.format_boolean
        self._app.jinja_env.filters['format'] = self.format
        self._app.jinja_env.filters['format_babel_date'] = self.format_babel_date
        self._app.jinja_env.filters['format_text_array'] = self.format_text_array
        self._app.jinja_env.filters['invert'] = self.invert
        self._app.jinja_env.filters['seconds_as_humanized_duration'] = self.format_seconds_as_humanized_duration
        self._app.jinja_env.filters['_base'] = self._base_gettext

        self._babel = flask_babel.Babel(self._app)
        self._babel.localeselector(self._locale_helper.locale_selector)
        gettext.bindtextdomain("messages", "little_brother/translations")

    def invert(self, rel_font_size):

        return str(int(1.0 / float(rel_font_size) * 10000.0))

    def format_datetime(self, value):

        if value is None:
            return "-"

        else:
            return value.strftime(self._config.datetime_format)

    def format_simple_date(self, value):

        if value is None:
            return "-"

        else:
            return value.strftime(self._config.simple_date_format)

    def format_date(self, value):

        if value is None:
            return "-"

        else:
            return value.strftime(self._config.date_format)

    def format_time(self, value):

        if value is None:
            return "-"

        else:
            return value.strftime(self._config.time_format)

    def format_seconds_as_humanized_duration(self, seconds):

        if seconds is None:
            return _("n/a")

        try:
            # trying to activate the localization for a non-existing locale (including 'en'!) triggers an exception
            if self._locale_helper.locale is not None:
                humanize.i18n.activate(self._locale_helper.locale)

        except Exception:
            humanize.i18n.deactivate()

        return humanize.naturaldelta(datetime.timedelta(seconds=seconds))

    @staticmethod
    def format_seconds(value):

        return tools.get_duration_as_string(p_seconds=value, p_include_seconds=False)

    @staticmethod
    def format_boolean(value):

        return tools.format_boolean(p_value=value)

    @staticmethod
    def format(value, param_dict):

        return value.format(**param_dict)

    def format_text_array(self, value):

        text = ""

        for part in value:
            if part == constants.TEXT_SEPERATOR:
                if text != "":
                    text += constants.TEXT_SEPERATOR

            else:
                text += self._base_gettext(self.gettext(part))

        return text

    def format_babel_date(self, value, format_string):

        return babel.dates.format_date(value, format_string, locale=self._locale_helper.locale)

    def gettext(self, p_text):
        return self._locale_helper.gettext(p_text=p_text)

    def destroy(self):

        if self._api_view_handler is not None:
            self._api_view_handler.destroy()

        self._about_view_handler.destroy()
        self._admin_view_handler.destroy()
        self._devices_view_handler.destroy()
        self._login_view_handler.destroy()
        self._status_view_handler.destroy()
        self._topology_view_handler.destroy()
        self._users_view_handler.destroy()
        super().destroy()
