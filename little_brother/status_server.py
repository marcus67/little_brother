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

import gettext

import flask
import flask_babel
import flask_login
import flask_wtf

import little_brother
from flask_helpers import blueprint_adapter
from little_brother import api_view_handler
from little_brother import git
from little_brother import rule_override
from little_brother import settings
from python_base_app import base_web_server
from python_base_app import tools

LANGUAGES = {
    'en': 'English',
    'de': 'Deutsch',
    'fr': 'Français',
    'it': 'Italiano',
}

SECTION_NAME = "StatusServer"

HEALTH_VIEW_NAME = "health"
HEALTH_REL_URL = "health"

INDEX_HTML_TEMPLATE = "index.template.html"
INDEX_REL_URL = "status"
INDEX_VIEW_NAME = "index"

ADMIN_HTML_TEMPLATE = "admin.template.html"
ADMIN_REL_URL = "admin"
ADMIN_VIEW_NAME = "admin"

ABOUT_HTML_TEMPLATE = "about.template.html"
ABOUT_REL_URL = "about"
ABOUT_VIEW_NAME = "about"

LOGIN_HTML_TEMPLATE = "login.template.html"

API_RELOAD_REL_URL = 'reload'

DEFAULT_CSS_NAME = 'default.css'
LOGIN_CSS_NAME = "login.css"

LOGO_LITTLE_BROTHER_NAME = 'icon_baby-panda_128x128.png'
ICON_FAVICON_NAME = 'baby-panda_32x32.ico'
ICON_DENIED_NAME = 'icon_denied.png'
ICON_OK_NAME = 'icon_check.png'

TEMPLATE_REL_DIR = "templates"

FORM_ID_CSRF = 'csrf'

# Dummy function to trigger extraction by pybabel...
_ = lambda x: x

BLUEPRINT_NAME = "little_brother"

BLUEPRINT_ADAPTER = blueprint_adapter.BlueprintAdapter()


class StatusServerConfigModel(base_web_server.BaseWebServerConfigModel):

    def __init__(self):
        super().__init__(p_section_name=SECTION_NAME)

        self.initializr_rel_dir = 'contrib/initializr'
        self.js_cookie_rel_dir = 'contrib/js-cookie'

        self.datetime_format = "%d.%m.%y %H:%M"
        self.time_format = "%H:%M"
        self.date_format = "%a %d.%m.%Y"
        self.simple_date_format = "%d.%m.%Y"


class StatusServer(base_web_server.BaseWebServer):

    def __init__(self,
                 p_config,
                 p_package_name,
                 p_app_control,
                 p_master_connector,
                 p_is_master):

        super(StatusServer, self).__init__(
            p_config=p_config,
            p_name="Web Server",
            p_package_name=p_package_name,
            p_use_login_manager=p_is_master,
            p_login_view=self.login_view,
            p_logged_out_endpoint=BLUEPRINT_NAME + '.' + INDEX_VIEW_NAME)

        self._blueprint = None
        self._is_master = p_is_master
        self._appcontrol = p_app_control
        self._master_connector = p_master_connector
        self._stat_dict = {}
        self._server_exception = None

        if self._is_master:
            self._blueprint = flask.Blueprint(BLUEPRINT_NAME, little_brother.__name__, static_folder="static")
            BLUEPRINT_ADAPTER.assign_view_handler_instance(p_blueprint=self._blueprint, p_view_handler_instance=self)
            BLUEPRINT_ADAPTER.check_view_methods()

            self._app.register_blueprint(blueprint=self._blueprint, url_prefix=self._config.base_url)

            self._api_view_handler = api_view_handler.ApiViewHandler(
                p_app=self._app, p_app_control=self._appcontrol, p_master_connector=self._master_connector)

        self._app.jinja_env.filters['datetime_to_string'] = self.format_datetime
        self._app.jinja_env.filters['time_to_string'] = self.format_time
        self._app.jinja_env.filters['date_to_string'] = self.format_date
        self._app.jinja_env.filters['simple_date_to_string'] = self.format_simple_date
        self._app.jinja_env.filters['seconds_to_string'] = self.format_seconds
        self._app.jinja_env.filters['boolean_to_string'] = self.format_boolean
        self._app.jinja_env.filters['format'] = self.format

        self._babel = flask_babel.Babel(self._app)
        self._babel.localeselector(self.get_request_locale)
        gettext.bindtextdomain("messages", "little_brother/translations")

    def get_request_locale(self):
        locale = flask.request.accept_languages.best_match(LANGUAGES)
        msg = "Best matching locale = {locale}"
        self._logger.debug(msg.format(locale=locale))
        return locale

    def login_view(self):

        page = flask.render_template(
            LOGIN_HTML_TEMPLATE,
            authentication=self.get_authenication_info(),
            navigation={
                'current_view': ADMIN_VIEW_NAME},
        )
        return page

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

    @staticmethod
    def format_seconds(value):

        return tools.get_duration_as_string(p_seconds=value, p_include_seconds=False)

    @staticmethod
    def format_boolean(value):

        return _("On") if value else _("Off")

    @staticmethod
    def format(value, param_dict):

        return value.format(**param_dict)

    @BLUEPRINT_ADAPTER.route_method("/")
    def entry_view(self):

        return flask.redirect(flask.url_for("little_brother.index"))

    def save_admin_data(self, p_admin_infos, p_forms):

        for admin_info in p_admin_infos:
            for day_info in admin_info.day_infos:
                form = p_forms[day_info.html_key]

                if form.differs_from_model(p_model=day_info.override):
                    form.save_to_model(p_model=day_info.override)
                    self._appcontrol.update_rule_override(day_info.override)

    @BLUEPRINT_ADAPTER.route_method("/admin", endpoint="admin", methods=["GET", "POST"])
    @flask_login.login_required
    def admin_view(self):

        admin_infos = self._appcontrol.get_admin_infos()
        forms = self.get_admin_forms(p_admin_infos=admin_infos)

        valid_and_submitted = True

        for form in forms.values():
            if not form.validate_on_submit():
                valid_and_submitted = False

        if valid_and_submitted:
            self.save_admin_data(admin_infos, forms)
            return flask.redirect(flask.url_for("little_brother.admin"))

        for admin_info in admin_infos:
            for day_info in admin_info.day_infos:
                forms[day_info.html_key].load_from_model(p_model=day_info.override)

        return flask.render_template(
            ADMIN_HTML_TEMPLATE,
            admin_infos=admin_infos,
            authentication=self.get_authenication_info(),
            forms=forms,
            navigation={
                'current_view': ADMIN_VIEW_NAME},
        )

    @BLUEPRINT_ADAPTER.route_method("/status", endpoint="index")
    def index_view(self):

        page = flask.render_template(
            INDEX_HTML_TEMPLATE,
            user_infos=self._appcontrol.get_user_infos(),
            authentication=self.get_authenication_info(),
            navigation={
                'current_view': INDEX_VIEW_NAME},
        )

        return page

    @BLUEPRINT_ADAPTER.route_method("/about", endpoint="about")
    def about_view(self):

        page = flask.render_template(
            ABOUT_HTML_TEMPLATE,
            user_infos=self._appcontrol.get_user_infos(),
            settings=settings.settings,
            git_metadata=git.git_metadata,
            authentication=self.get_authenication_info(),
            navigation={
                'current_view': ABOUT_VIEW_NAME}

        )
        return page

    @staticmethod
    def get_admin_forms(p_admin_infos):

        forms = {}

        forms[FORM_ID_CSRF] = flask_wtf.FlaskForm(csrf_enabled=True)

        for admin_info in p_admin_infos:
            for day_info in admin_info.day_infos:
                form = rule_override.RuleOverrideForm(prefix=day_info.html_key + '_', csrf_enabled=False)
                forms[day_info.html_key] = form

        return forms

    def destroy(self):

        BLUEPRINT_ADAPTER.unassign_view_handler_instances()
        super().destroy()
