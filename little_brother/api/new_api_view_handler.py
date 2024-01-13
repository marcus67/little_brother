# -*- coding: utf-8 -*-

# Copyright (C) 2019-2024  Marcus Rickert
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
import json

import flask
from flask import jsonify

from little_brother import constants
from little_brother import dependency_injection
from little_brother.api.master_connector import MasterConnector
from little_brother.base_view_handler import BaseViewHandler
from little_brother.event_handler import EventHandler
from little_brother.persistence.persistent_daily_user_status import DailyUserStatus
from little_brother.persistence.persistent_user import User
from little_brother.persistence.session_context import SessionContext
from python_base_app import tools
from python_base_app.angular_auth_view_handler import AngularAuthViewHandler
from some_flask_helpers import blueprint_adapter

MIME_TYPE_APPLICATION_JSON = 'application/json'

API_BLUEPRINT_NAME = "NEW_API"
API_BLUEPRINT_ADAPTER = blueprint_adapter.BlueprintAdapter()

# Dummy function to trigger extraction by pybabel...


def _(x):
    return x


class NewApiViewHandler(BaseViewHandler):

    def __init__(self, p_package, p_languages):

        super().__init__(p_blueprint_name=API_BLUEPRINT_NAME, p_blueprint_adapter=API_BLUEPRINT_ADAPTER,
                         p_package=p_package)

        self._master_connector = None
        self._auth_view_handler = None
        self._event_handler = None
        self._languages = p_languages

    @property
    def blueprint(self):
        return self._blueprint

    @property
    def master_connector(self) -> MasterConnector:

        if self._master_connector is None:
            self._master_connector = dependency_injection.container[MasterConnector]

        return self._master_connector

    @property
    def auth_view_handler(self) -> AngularAuthViewHandler:

        if self._auth_view_handler is None:
            self._auth_view_handler = dependency_injection.container[AngularAuthViewHandler]

        return self._auth_view_handler

    @property
    def event_handler(self) -> EventHandler:

        if self._event_handler is None:
            self._event_handler = dependency_injection.container[EventHandler]

        return self._event_handler

    def measure(self, p_hostname, p_service, p_duration):

        self.app_control.set_prometheus_http_requests_summary(p_hostname=p_hostname,
                                                              p_service=p_service,
                                                              p_duration=p_duration)

    def api_error(self, p_message, p_status_code=constants.HTTP_STATUS_CODE_NOT_FOUND):
        msg_format = '{{ "{errortag}" : "{msg}" }}'
        msg = msg_format.format(errortag=constants.JSON_ERROR, msg=p_message)
        return flask.Response(msg, status=p_status_code, mimetype=MIME_TYPE_APPLICATION_JSON)

    def missing_parameter_error(self, p_parameter_name):
        msg_format = _("parameter '{parameter_name}' not specified")
        msg = msg_format.format(parameter_name=p_parameter_name)
        return self.api_error(p_message=msg)

    def wrong_parameter_format_error(self, p_parameter_name, p_value):
        msg_format = _("parameter '{parameter_name}' with value '{value}' has wrong format")
        msg = msg_format.format(parameter_name=p_parameter_name, value=p_value)
        return self.api_error(p_message=msg)

    def user_does_not_exist_error(self, p_username):
        msg_format = _("username '{username}' does not exist or is not being monitored")
        msg = msg_format.format(username=p_username)
        return self.api_error(p_message=msg)

    def invalid_secret_error(self):
        return self.api_error(p_message="invalid access code",
                              p_status_code=constants.HTTP_STATUS_CODE_UNAUTHORIZED)

    def internal_server_error(self, p_exception : Exception):
        return self.api_error(p_message=f"internal server error: {str(p_exception)}",
                              p_status_code=constants.HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR)


    def destroy(self):
        API_BLUEPRINT_ADAPTER.unassign_view_handler_instances()
        
    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_REL_URL_ABOUT, methods=["GET"])
    def api_about(self):
        request = flask.request
        with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                               p_service=self.simplify_url(request.url_rule),
                                                               p_duration=duration)):
            try:
                result, http_status = self.auth_view_handler.check_authorization(p_request=request)

                if http_status != 200:
                    return jsonify(result), http_status

                template_dict = {}
                self.add_general_template_data(p_dict=template_dict, p_add_authentication_data=False)
                template_dict["languages"] = sorted(
                    [(a_locale, a_language) for a_locale, a_language in self._languages.items()])

                return jsonify(template_dict), 200

            except Exception as e:
                return self.internal_server_error(p_exception=e)
