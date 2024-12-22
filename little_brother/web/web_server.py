# -*- coding: utf-8 -*-

# Copyright (C) 2019-24  Marcus Rickert
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
import io
import os
import re
from os.path import join
from typing import List, Optional
from urllib.parse import urlunsplit

import babel.dates
import flask
import flask_babel
import humanize
from jinja2 import Environment, PackageLoader, select_autoescape

import little_brother
import little_brother as little_brother_package
from little_brother import app_control, dependency_injection
from little_brother import constants
from little_brother import entity_forms
from little_brother.api import api_view_handler
from little_brother.api.new_api_view_handler import NewApiViewHandler
from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn
from little_brother.settings import extended_settings
from little_brother.token_handler import TokenHandler, SECTION_NAME as TOKEN_HANDLER_SECTION_NAME
from little_brother.web.about_view_handler import AboutViewHandler
from little_brother.web.admin_view_handler import AdminViewHandler
from little_brother.web.angular_view_handler import AngularViewHandler
from little_brother.web.devices_view_handler import DevicesViewHandler
from little_brother.web.login_view_handler import LoginViewHandler
from little_brother.web.status_view_handler import StatusViewHandler
from little_brother.web.topology_view_handler import TopologyViewHandler
from little_brother.web.users_view_handler import UsersViewHandler
from python_base_app import angular_auth_view_handler
from python_base_app import base_web_server
from python_base_app import locale_helper
from python_base_app import tools
from python_base_app.angular_auth_view_handler import ANGULAR_BASE_URL
from python_base_app.base_app import RecurringTask
from python_base_app.configuration import ConfigurationException, NONE_STRING

SECTION_NAME = "StatusServer"

ANGULAR_CONFIG_TEMPLATE_FILE = "angular-config.template.json"
ANGULAR_CONFIG_FILE = "assets/config.json"
ANGULAR_HTML_INDEX_FILE = "index.html"

SETTING_ANGULAR_DEPLOYMENT_DIRECTORY = "angular_deployment_dest_directory"


def _(x):
    return x


class StatusServerConfigModel(base_web_server.BaseWebServerConfigModel):

    def __init__(self):
        super().__init__(p_section_name=SECTION_NAME)

        self.initializr_rel_dir = 'contrib/initializr'
        self.js_cookie_rel_dir = 'contrib/js-cookie'

        self.datetime_format = "%d.%m.%y %H:%M"
        self.time_format = "%H:%M"
        self.date_format = "%a %d.%m.%Y"
        self.simple_date_format = "%d.%m.%Y"
        self.classic_gui_active = True
        self.angular_gui_active = False

        self.angular_api_base_url = ANGULAR_BASE_URL
        self.angular_gui_base_url = ""
        self.angular_gui_rel_static_folder = "angular"
        self.angular_deployment_directory = NONE_STRING

        self.patch_angular_index_html = True
        self.create_angular_config_file = True


class StatusServer(PersistenceDependencyInjectionMixIn, base_web_server.BaseWebServer):

    def __init__(self,
                 p_configs,
                 p_package_name,
                 p_app_control,
                 p_master_connector,
                 p_is_master,
                 p_locale_helper,
                 p_base_gettext=None,
                 p_languages=None,
                 p_user_handler=None):

        self._api_view_handler = None
        self._new_api_view_handler = None
        self._new_api_angular_view_handler = None
        self._login_view_handler = None
        self._token_handler: Optional[TokenHandler] = None
        self._angular_auth_view_handler = None

        my_config: StatusServerConfigModel = p_configs[SECTION_NAME]

        login_view = None

        if my_config.classic_gui_active:
            self._login_view_handler = LoginViewHandler(p_package=little_brother, p_languages=p_languages)
            login_view = self._login_view_handler.login_view

        super().__init__(
            p_config=my_config,
            p_name="Web Server",
            p_package_name=p_package_name,
            p_user_handler=p_user_handler,
            p_login_view=login_view,
            p_logged_out_endpoint=constants.STATUS_BLUEPRINT_NAME + '.' + constants.STATUS_VIEW_NAME)

        # This blueprint handles static resources...
        self._blueprint = flask.Blueprint("little_brother", little_brother.__name__, static_folder="static")
        self._app.register_blueprint(self._blueprint, url_prefix=self._config.base_url)

        if not (self._config.angular_gui_active or self._config.classic_gui_active):
            raise ConfigurationException("Neither classic nor Angular GUI active!")

        self._logger.info("Starting web server")

        if self._config.angular_gui_active:
            self._logger.info("Activating Angular GUI support...")
            self._token_handler = TokenHandler(p_config=p_configs[TOKEN_HANDLER_SECTION_NAME],
                                               p_secret_key=self._app.config.get('SECRET_KEY'))

        if self._config.classic_gui_active:
            self._logger.info("Activating classic GUI support...")
            self._about_view_handler = AboutViewHandler(p_package=little_brother, p_languages=p_languages)
            self._admin_view_handler = AdminViewHandler(p_package=little_brother)
            self._devices_view_handler = DevicesViewHandler(p_package=little_brother)
            self._status_view_handler = StatusViewHandler(p_package=little_brother)
            self._topology_view_handler = TopologyViewHandler(p_package=little_brother)
            self._users_view_handler = UsersViewHandler(p_package=little_brother, p_languages=p_languages)

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
        self._server_exception: Optional[Exception] = None
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
            self._api_view_handler = api_view_handler.ApiViewHandler(p_app=self._app,
                                                                     p_config=p_configs[api_view_handler.SECTION_NAME])
            dependency_injection.container[api_view_handler.ApiViewHandler] = self._api_view_handler

            self._csrf.exempt(self._api_view_handler.blueprint)

            if self._config.angular_gui_active:
                self._angular_auth_view_handler = angular_auth_view_handler.AngularAuthViewHandler(
                    p_app=self._app, p_user_handler=p_user_handler,
                    p_url_prefix=self._config.angular_api_base_url,
                    p_token_handler=self._token_handler)
                dependency_injection.container[angular_auth_view_handler.AngularAuthViewHandler] = \
                    self._angular_auth_view_handler
                self._new_api_view_handler = NewApiViewHandler(p_package=little_brother, p_languages=p_languages)
                self._new_api_view_handler.register(p_app=self._app, p_url_prefix=self._config.angular_api_base_url)

                self._new_api_angular_view_handler = AngularViewHandler(
                    p_package=little_brother, p_rel_static_folder=self._config.angular_gui_rel_static_folder)
                self._new_api_angular_view_handler.register(
                    p_app=self._app, p_url_prefix=self._config.angular_gui_base_url)

                if self._config.patch_angular_index_html:
                    self.patch_angular_index_html()

                if self._config.create_angular_config_file:
                    self.create_angular_config_file()

                if not self._config.use_csrf:
                    self._csrf.exempt(self._angular_auth_view_handler.blueprint)
                    self._csrf.exempt(self._new_api_view_handler.blueprint)
                    self._csrf.exempt(self._new_api_angular_view_handler.blueprint)

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

        self._babel = flask_babel.Babel()
        self._babel.init_app(app=self._app, locale_selector=self._locale_helper.locale_selector)
        gettext.bindtextdomain("messages", "little_brother/translations")

        entity_forms.set_get_text(self.gettext)

    def get_angular_url(self, p_rel_url=None):

        effective_url = join(self._config.angular_gui_base_url, p_rel_url) \
            if p_rel_url is not None else self._config.angular_gui_base_url
        return urlunsplit(
            (
                self._config.scheme,
                "%s:%d" % (self._config.host, self._config.port),
                effective_url,
                None,
                None
            ))

    @staticmethod
    def invert(rel_font_size):
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

        if self._new_api_view_handler is not None:
            self._new_api_view_handler.destroy()

        if self._new_api_angular_view_handler is not None:
            self._new_api_angular_view_handler.destroy()

        if self._angular_auth_view_handler is not None:
            self._angular_auth_view_handler.destroy()

        if self._config.classic_gui_active:
            self._about_view_handler.destroy()
            self._admin_view_handler.destroy()
            self._devices_view_handler.destroy()
            self._login_view_handler.destroy()
            self._status_view_handler.destroy()
            self._topology_view_handler.destroy()
            self._users_view_handler.destroy()

        super().destroy()

    def get_recurring_tasks(self) -> List[RecurringTask]:

        tasks = []

        if self._token_handler is not None:
            tasks.append(self._token_handler.get_recurring_task())

        return tasks

    def get_angular_deployment_directory(self) -> str:

        my_dir = os.path.dirname(little_brother_package.__file__)

        if self._config.angular_deployment_directory is not None:
            return os.path.realpath(os.path.join(my_dir, "..", self._config.angular_deployment_directory))

        elif SETTING_ANGULAR_DEPLOYMENT_DIRECTORY in extended_settings:
            return os.path.join(my_dir, extended_settings[SETTING_ANGULAR_DEPLOYMENT_DIRECTORY])

        raise ConfigurationException(
            f"key '{SETTING_ANGULAR_DEPLOYMENT_DIRECTORY}' not found in settings.extended_settings or "
            "in [StatusServer].angular_deployment_directory!")

    def patch_angular_index_html(self):

        index_filename = os.path.join(self.get_angular_deployment_directory(),
                                      ANGULAR_HTML_INDEX_FILE)

        if not os.path.exists(index_filename):
            raise ConfigurationException(f"Cannot find Angular index.html at {index_filename}!")

        with open(index_filename) as f:
            content = f.read()

        regex = re.compile(r'^(.*<base href=")([^"]*)(".+)$', re.DOTALL)
        match = regex.match(content)

        if match is None:
            raise ConfigurationException(f"Cannot find baseUrl in index.html at {index_filename}!")

        new_content = f"{match.group(1)}{self._config.angular_gui_base_url}/{match.group(3)}"

        with open(index_filename, "w") as f:
            f.write(new_content)

        self._logger.info(f"Wrote updated Angular index.html to {index_filename}.")

    def create_angular_config_file(self):

        env = Environment(
            loader=PackageLoader("little_brother"),
            autoescape=select_autoescape()
        )

        template = env.get_template(ANGULAR_CONFIG_TEMPLATE_FILE)

        settings = {
            "base_url": self._config.angular_api_base_url
        }

        content = template.render(settings=settings)

        config_filename = os.path.join(self.get_angular_deployment_directory(), ANGULAR_CONFIG_FILE)

        try:
            with io.open(config_filename, "w") as f:
                f.write(content)
            self._logger.info(f"Wrote Angular configuration file to {config_filename}.")

        except IOError as e:
            raise ConfigurationException(f"Cannot write Angular configuration to file {config_filename}: {e!s}!")

    def run(self):
        if self._config.angular_gui_active:
            msg = f"Starting Angular web server '{self._name}' on " \
                  f"{self._config.host}:{self._config.port}{self._config.angular_gui_base_url}"
            self._logger.info(msg)

        super().run()
