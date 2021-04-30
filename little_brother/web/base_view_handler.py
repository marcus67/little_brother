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

from little_brother import dependency_injection
from little_brother.admin_data_handler import AdminDataHandler
from little_brother.app_control import AppControl
from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn
from little_brother.rule_handler import RuleHandler
from python_base_app import log_handling
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

    def register(self, p_app, p_url_prefix:str=None):

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


    def destroy(self):
        self._blueprint_adapter.unassign_view_handler_instances()

    def gettext(self, p_text):
        return self.locale_helper.gettext(p_text=p_text)
