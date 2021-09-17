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

import flask

from little_brother import dependency_injection, constants, settings, git
from little_brother.admin_data_handler import AdminDataHandler
from little_brother.api.version_checker import VersionChecker, VersionInfo
from little_brother.app_control import AppControl
from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn
from little_brother.process_handler_manager import ProcessHandlerManager
from little_brother.rule_handler import RuleHandler
from little_brother.user_manager import UserManager
from python_base_app import log_handling
from python_base_app.base_web_server import BaseWebServer
from python_base_app.locale_helper import LocaleHelper
from some_flask_helpers import blueprint_adapter

LOCALE_REL_FONT_SIZES = {
    'bn': 125  # scale Bangla fonts to 125% for readability
}

FORM_ID_CSRF = 'csrf'


class BaseViewHandler(PersistenceDependencyInjectionMixIn):

    def __init__(self, p_blueprint_name, p_blueprint_adapter, p_package):

        super().__init__()

        self._logger = log_handling.get_logger(self.__class__.__name__)
        self._url_prefix = None

        self._blueprint_adapter: blueprint_adapter.BlueprintAdapter = p_blueprint_adapter
        self._blueprint = flask.Blueprint(p_blueprint_name, p_package.__name__)
        p_blueprint_adapter.assign_view_handler_instance(p_blueprint=self._blueprint, p_view_handler_instance=self)
        p_blueprint_adapter.check_view_methods()

        self._app_control = None
        self._admin_data_handler = None
        self._rule_handler = None
        self._locale_helper = None
        self._process_handler_manager = None
        self._user_manager = None
        self._version_checker = None

    @property
    def app_control(self) -> AppControl:
        if self._app_control is None:
            self._app_control = dependency_injection.container[AppControl]

        return self._app_control

    @property
    def admin_data_handler(self) -> AdminDataHandler:
        if self._admin_data_handler is None:
            self._admin_data_handler = dependency_injection.container[AdminDataHandler]

        return self._admin_data_handler

    @property
    def locale_helper(self) -> LocaleHelper:
        if self._locale_helper is None:
            self._locale_helper = dependency_injection.container[LocaleHelper]

        return self._locale_helper

    @property
    def rule_handler(self) -> RuleHandler:
        if self._rule_handler is None:
            self._rule_handler = dependency_injection.container[RuleHandler]

        return self._rule_handler

    @property
    def processs_handler_manager(self) -> ProcessHandlerManager:
        if self._process_handler_manager is None:
            self._process_handler_manager = dependency_injection.container[ProcessHandlerManager]

        return self._process_handler_manager

    @property
    def user_manager(self) -> UserManager:

        if self._user_manager is None:
            self._user_manager = dependency_injection.container[UserManager]

        return self._user_manager

    @property
    def version_checker(self) -> VersionChecker:

        if self._version_checker is None:
            self._version_checker = dependency_injection.container[VersionChecker]

        return self._version_checker

    @classmethod
    def validate(cls, p_forms):

        valid = True
        submitted = False

        for form in p_forms.values():
            if not form.validate_on_submit():
                valid = False

            if form.is_submitted():
                submitted = True

        return valid and submitted, submitted

    def register(self, p_app, p_url_prefix: str = None):

        p_app.register_blueprint(self._blueprint, url_prefix=p_url_prefix)
        self._url_prefix = p_url_prefix

    def measure(self, p_hostname, p_service, p_duration):

        self.app_control.set_prometheus_http_requests_summary(
            p_hostname=p_hostname, p_service=p_service, p_duration=p_duration)

    def simplify_url(self, p_url):
        return str(p_url).replace(self._url_prefix, '')

    def has_downtime_today(self, p_user_infos):

        for user_info in p_user_infos.values():
            if user_info['active_stat_info'].todays_downtime:
                return True

        return False

    def get_rel_font_size(self):

        rel_font_size = LOCALE_REL_FONT_SIZES.get(self.locale_helper.locale)
        if not rel_font_size:
            rel_font_size = 100
        return rel_font_size

    def add_general_template_data(self, p_dict):

        p_dict["rel_font_size"] = self.get_rel_font_size()
        p_dict["settings"] = settings.settings
        p_dict["extended_settings"] = settings.extended_settings
        p_dict["git_metadata"] = git.git_metadata
        p_dict["authentication"] = BaseWebServer.get_authentication_info()

    def add_version_info(self, p_dict):

        current_revision = settings.extended_settings["debian_package_revision"]
        channel = self.app_control._config.update_channel

        suggested_version_info: VersionInfo = self.version_checker.is_revision_current(p_channel=channel,
                                                                                       p_revision=current_revision)

        if suggested_version_info is not None:
            format_dict = {
                "channel": channel,
                "current_version": settings.settings["version"],
                "current_revision": current_revision,
                "suggested_version": suggested_version_info.version,
                "suggested_revision": suggested_version_info.revision,
                "download_url": self.version_checker.get_download_url(p_channel=channel)
            }

            p_dict["version_format_dict"] = format_dict

    def destroy(self):
        self._blueprint_adapter.unassign_view_handler_instances()

    def gettext(self, p_text):
        return self.locale_helper.gettext(p_text=p_text)

    def handle_rendering_exception(self, p_page_name, p_exception):

        msg = "Exception '{exception}' while generating {page_name}"
        self._logger.exception(msg.format(exception=str(p_exception), page_name=p_page_name))

        return flask.render_template(
            constants.INTERNAL_ERROR_HTML_TEMPLATE,
            rel_font_size=self.get_rel_font_size(),
            error_message=str(p_exception)
        )
