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
from flask_helpers import blueprint_adapter
from little_brother import constants
from python_base_app import log_handling
from python_base_app import tools

API_BLUEPRINT_NAME = "API"
API_BLUEPRINT_ADAPTER = blueprint_adapter.BlueprintAdapter()

# Dummy function to trigger extraction by pybabel...F
_ = lambda x: x

class ApiViewHandler(object):

    def __init__(self, p_app, p_app_control, p_master_connector):
        self._appcontrol = p_app_control
        self._master_connector = p_master_connector
        self._logger = log_handling.get_logger(self.__class__.__name__)

        self._blueprint = flask.Blueprint(API_BLUEPRINT_NAME, little_brother.__name__)
        API_BLUEPRINT_ADAPTER.assign_view_handler_instance(p_blueprint=self._blueprint,
                                                           p_view_handler_instance=self)
        API_BLUEPRINT_ADAPTER.check_view_methods()
        p_app.register_blueprint(self._blueprint)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_URL_EVENTS, methods=["POST"])
    def api_events(self):
        request = flask.request
        data = request.get_json()

        event_info = self._master_connector.receive_events(p_json_data=data)

        if event_info is None:
            return flask.Response("{error: invalid access code}", status=constants.HTTP_STATUS_CODE_UNAUTHORIZED,
                                  mimetype='application/json')

        (hostname, json_events) = event_info

        msg = "Received {count} events from host '{hostname}'"
        self._logger.debug(msg.format(count=len(json_events), hostname=hostname))

        self._appcontrol.receive_events(p_json_data=json_events)

        return_events = self._appcontrol.get_return_events(p_hostname=hostname)
        msg = "Sending {count} events back to host '{hostname}'"
        self._logger.debug(msg.format(count=len(return_events), hostname=hostname))

        return flask.Response(json.dumps(return_events, cls=tools.ObjectEncoder), status=constants.HTTP_STATUS_CODE_OK,
                              mimetype='application/json')

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_URL_STATUS, methods=["GET"])
    def api_status(self):
        request = flask.request

        username = request.args.get(constants.API_URL_PARAM_USERNAME)

        if username is None:
            msg = _("username '{username}' not specified")
            return flask.Response('{{ "{errortag}" : "{msg}" }}'.format(msg=msg, errortag=constants.JSON_ERROR),
                                  status=constants.HTTP_STATUS_CODE_NOT_FOUND,
                                  mimetype='application/json')

        user_status = self._appcontrol.get_user_status(p_username=username)

        if user_status is None:
            msg = _("username '{username}' not being monitored")
            return flask.Response('{{ "{errortag}" : "{msg}" }}'.format(msg=msg, errortag=constants.JSON_ERROR),
                                  status=constants.HTTP_STATUS_CODE_NOT_FOUND,
                                  mimetype='application/json')

        msg = "Received status request for user '{username}'"
        self._logger.debug(msg.format(username=username))

        return flask.Response(json.dumps(user_status, cls=tools.ObjectEncoder), status=constants.HTTP_STATUS_CODE_OK,
                              mimetype='application/json')
