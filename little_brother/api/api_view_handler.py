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

import json

import flask

import little_brother
from little_brother import constants, dependency_injection
from little_brother.app_control import AppControl
from little_brother.dependency_injection import container
from little_brother.event_handler import EventHandler
from little_brother.master_connector import MasterConnector
from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn
from little_brother.persistence.session_context import SessionContext
from little_brother.user_manager import UserManager
from python_base_app import log_handling
from python_base_app import tools
from some_flask_helpers import blueprint_adapter

API_BLUEPRINT_NAME = "API"
API_BLUEPRINT_ADAPTER = blueprint_adapter.BlueprintAdapter()

# Dummy function to trigger extraction by pybabel...
_ = lambda x: x

class ApiViewHandler(PersistenceDependencyInjectionMixIn):

    def __init__(self, p_app):

        super().__init__()

        self._appcontrol = None
        self._master_connector = None
        self._event_handler = None
        self._user_manager = None
        self._logger = log_handling.get_logger(self.__class__.__name__)

        self._blueprint = flask.Blueprint(API_BLUEPRINT_NAME, little_brother.__name__)
        API_BLUEPRINT_ADAPTER.assign_view_handler_instance(p_blueprint=self._blueprint,
                                                           p_view_handler_instance=self)
        API_BLUEPRINT_ADAPTER.check_view_methods()
        p_app.register_blueprint(self._blueprint)

    @property
    def app_control(self) -> AppControl:
        
        if self._appcontrol is None:
            self._appcontrol = container[AppControl]
            
        return self._appcontrol

    @property
    def master_connector(self) -> MasterConnector:

        if self._master_connector is None:
            self._master_connector = container[MasterConnector]

        return self._master_connector

    @property
    def event_handler(self) -> EventHandler:

        if self._event_handler is None:
            self._event_handler = container[EventHandler]

        return self._event_handler

    @property
    def user_manager(self) -> UserManager:

        if self._user_manager is None:
            self._user_manager = dependency_injection.container[UserManager]

        return self._user_manager

    def measure(self, p_hostname, p_service, p_duration):

        self.app_control.set_prometheus_http_requests_summary(p_hostname=p_hostname,
                                                              p_service=p_service,
                                                              p_duration=p_duration)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_URL_EVENTS, methods=["POST"])
    def api_events(self):
        request = flask.request

        with tools.TimingContext(lambda duration:self.measure(p_hostname=request.remote_addr,
                                                         p_service=request.url_rule, p_duration=duration)):
            data = request.get_json()

            event_info = self.master_connector.receive_events(p_json_data=data)

            if event_info is None:
                return flask.Response("{error: invalid access code}", status=constants.HTTP_STATUS_CODE_UNAUTHORIZED,
                                      mimetype='application/json')

            client_stats = None

            if len(event_info) > 2:
                # new format: 3 entries including client statistics
                (hostname, json_events, json_client_stats) = event_info
                client_stats = self.app_control.receive_client_stats(p_json_data=json_client_stats)

            else:
                # old format: 2 entries without slave statistics
                (hostname, json_events) = event_info

            msg = "Received {count} events from host '{hostname}'"
            self._logger.debug(msg.format(count=len(json_events), hostname=hostname))

            self.app_control.update_client_info(p_hostname=hostname, p_client_stats=client_stats)
            self.event_handler.receive_events(p_json_data=json_events)

            return_events = self.event_handler.get_return_events(p_hostname=hostname)
            msg = "Sending {count} events back to host '{hostname}'"
            self._logger.debug(msg.format(count=len(return_events), hostname=hostname))

            return flask.Response(json.dumps(return_events, cls=tools.ObjectEncoder), status=constants.HTTP_STATUS_CODE_OK,
                                  mimetype='application/json')

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_URL_STATUS, methods=["GET"])
    def api_status(self):
        request = flask.request

        with tools.TimingContext(lambda duration:self.measure(p_hostname=request.remote_addr,
                                                         p_service=request.url_rule, p_duration=duration)):
            username = request.args.get(constants.API_URL_PARAM_USERNAME)

            if username is None:
                msg = _("username '{username}' not specified")
                return flask.Response('{{ "{errortag}" : "{msg}" }}'.format(msg=msg, errortag=constants.JSON_ERROR),
                                      status=constants.HTTP_STATUS_CODE_NOT_FOUND,
                                      mimetype='application/json')

            with SessionContext(p_persistence=self.persistence) as session_context:
                user_status = self.user_manager.get_current_user_status(
                    p_session_context=session_context, p_username=username)

            if user_status is None:
                msg = _("username '{username}' not being monitored")
                return flask.Response('{{ "{errortag}" : "{msg}" }}'.format(msg=msg, errortag=constants.JSON_ERROR),
                                      status=constants.HTTP_STATUS_CODE_NOT_FOUND,
                                      mimetype='application/json')

            msg = "Received status request for user '{username}'"
            self._logger.debug(msg.format(username=username))

            return flask.Response(json.dumps(user_status, cls=tools.ObjectEncoder), status=constants.HTTP_STATUS_CODE_OK,
                                  mimetype='application/json')
