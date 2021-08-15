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
import datetime
import json

import flask

import little_brother
from little_brother import constants
from little_brother import dependency_injection
from little_brother.admin_data_handler import AdminDataHandler
from little_brother.api.master_connector import MasterConnector
from little_brother.app_control import AppControl
from little_brother.event_handler import EventHandler
from little_brother.persistence.persistent_daily_user_status import DailyUserStatus
from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn
from little_brother.persistence.persistent_user import User
from little_brother.persistence.session_context import SessionContext
from little_brother.process_handler_manager import ProcessHandlerManager
from little_brother.rule_handler import RuleHandler
from little_brother.user_manager import UserManager
from python_base_app import log_handling
from python_base_app import tools
from some_flask_helpers import blueprint_adapter

MIME_TYPE_APPLICATION_JSON = 'application/json'

API_BLUEPRINT_NAME = "API"
API_BLUEPRINT_ADAPTER = blueprint_adapter.BlueprintAdapter()

# Dummy function to trigger extraction by pybabel...
_ = lambda x: x

# ToDo: Derive ApiViewHandler from BaseViewHandler!
class ApiViewHandler(PersistenceDependencyInjectionMixIn):

    def __init__(self, p_app):

        super().__init__()

        self._appcontrol = None
        self._master_connector = None
        self._event_handler = None
        self._user_manager = None
        self._rule_handler = None
        self._admin_data_handler = None
        self._process_handler_manager = None
        self._logger = log_handling.get_logger(self.__class__.__name__)

        self._blueprint = flask.Blueprint(API_BLUEPRINT_NAME, little_brother.__name__)
        API_BLUEPRINT_ADAPTER.assign_view_handler_instance(p_blueprint=self._blueprint,
                                                           p_view_handler_instance=self)
        API_BLUEPRINT_ADAPTER.check_view_methods()
        p_app.register_blueprint(self._blueprint)

    @property
    def blueprint(self):
        return self._blueprint

    @property
    def app_control(self) -> AppControl:
        
        if self._appcontrol is None:
            self._appcontrol = dependency_injection.container[AppControl]
            
        return self._appcontrol

    @property
    def master_connector(self) -> MasterConnector:

        if self._master_connector is None:
            self._master_connector = dependency_injection.container[MasterConnector]

        return self._master_connector

    @property
    def event_handler(self) -> EventHandler:

        if self._event_handler is None:
            self._event_handler = dependency_injection.container[EventHandler]

        return self._event_handler

    @property
    def user_manager(self) -> UserManager:

        if self._user_manager is None:
            self._user_manager = dependency_injection.container[UserManager]

        return self._user_manager

    @property
    def rule_handler(self) -> RuleHandler:

        if self._rule_handler is None:
            self._rule_handler = dependency_injection.container[RuleHandler]

        return self._rule_handler

    @property
    def admin_data_handler(self) -> AdminDataHandler:

        if self._admin_data_handler is None:
            self._admin_data_handler = dependency_injection.container[AdminDataHandler]

        return self._admin_data_handler

    @property
    def processs_handler_manager(self) -> ProcessHandlerManager:
        if self._process_handler_manager is None:
            self._process_handler_manager = dependency_injection.container[ProcessHandlerManager]

        return self._process_handler_manager


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

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_URL_EVENTS, methods=["POST"])
    def api_events(self):
        request = flask.request

        with tools.TimingContext(lambda duration:self.measure(p_hostname=request.remote_addr,
                                                         p_service=request.url_rule, p_duration=duration)):
            data = request.get_json()

            event_info = self.master_connector.receive_events(p_json_data=data)

            if event_info is None:
                return self.invalid_secret_error()

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
            self.app_control.queue_broadcast_event_start_master()
            self.event_handler.receive_events(p_json_data=json_events)

            return_events = self.event_handler.get_return_events(p_hostname=hostname)
            msg = "Sending {count} events back to host '{hostname}'"
            self._logger.debug(msg.format(count=len(return_events), hostname=hostname))

            return flask.Response(json.dumps(return_events, cls=tools.ObjectEncoder), status=constants.HTTP_STATUS_CODE_OK,
                                                  mimetype=MIME_TYPE_APPLICATION_JSON)


    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_URL_STATUS, methods=["GET"])
    def api_status(self):
        request = flask.request

        with tools.TimingContext(lambda duration:self.measure(p_hostname=request.remote_addr,
                                                         p_service=request.url_rule, p_duration=duration)):
            username = request.args.get(constants.API_URL_PARAM_USERNAME)

            if username is None:
                return self.missing_parameter_error(p_parameter_name=constants.API_URL_PARAM_USERNAME)

            with SessionContext(p_persistence=self.persistence) as session_context:
                user_status = self.user_manager.get_current_user_status(
                    p_session_context=session_context, p_username=username)

                if user_status is None or not user_status.monitoring_active:
                    return self.user_does_not_exist_error(p_username=username)

                user = self.user_entity_manager.get_by_username(p_session_context=session_context, p_username=username)

                user_status.optional_time_available = \
                    self.get_optional_time_available_in_minutes(p_session_context=session_context, p_user=user)

                user_status.ruleset_check_interval = self.app_control._config.check_interval

                msg = "Received status request for user '{username}'"
                self._logger.debug(msg.format(username=username))

                return flask.Response(json.dumps(user_status, cls=tools.ObjectEncoder),
                                      status=constants.HTTP_STATUS_CODE_OK,
                                      mimetype=MIME_TYPE_APPLICATION_JSON)


    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_URL_REQUEST_TIME_EXTENSION, methods=["POST"])
    def api_request_time_extension(self):
        request = flask.request

        with tools.TimingContext(lambda duration:self.measure(p_hostname=request.remote_addr,
                                                         p_service=request.url_rule, p_duration=duration)):
            username = request.args.get(constants.API_URL_PARAM_USERNAME)
            secret = request.args.get(constants.API_URL_PARAM_SECRET)
            extension_length_string = request.args.get(constants.API_URL_PARAM_EXTENSION_LENGTH)

            if username is None:
                return self.missing_parameter_error(p_parameter_name=constants.API_URL_PARAM_USERNAME)

            if secret is None:
                return self.missing_parameter_error(p_parameter_name=constants.API_URL_PARAM_SECRET)

            if extension_length_string is None:
                return self.missing_parameter_error(p_parameter_name=constants.API_URL_PARAM_EXTENSION_LENGTH)

            with SessionContext(p_persistence=self.persistence) as session_context:
                user = self.user_entity_manager.get_by_username(p_session_context=session_context, p_username=username)

                if user is None:
                    return  self.user_does_not_exist_error(p_username=username)

                if secret != user.access_code:
                    return self.invalid_secret_error()

                try:
                    extension_length = int(extension_length_string)

                except:
                    return self.wrong_parameter_format_error(p_parameter_name=constants.API_URL_PARAM_EXTENSION_LENGTH,
                                                             p_value=extension_length_string)

                msg = "Received time extension request for user '{username}' for {minutes} minutes"
                self._logger.debug(msg.format(username=username, minutes=extension_length))

                return self.request_time_extension(p_session_context=session_context, p_user=user,
                                                   p_time_extension_length=extension_length)

    def get_optional_time_available_in_minutes(self, p_session_context: SessionContext, p_user: User,
                                               p_reference_date: datetime.date=None):

        if p_reference_date is None:
            p_reference_date = datetime.date.today()

        user_status = self.daily_user_status_entity_manager.get_user_status(
            p_user_id=p_user.id, p_session_context=p_session_context, p_reference_date=p_reference_date)

        active_rule_set = self.rule_handler.get_active_ruleset(p_reference_date=p_reference_date,
                                                               p_rule_sets=p_user.rulesets)

        if active_rule_set.optional_time_per_day is None:
            return None

        if active_rule_set is not None:
            optional_time_per_day = int (active_rule_set.optional_time_per_day / 60)

        else:
            optional_time_per_day = 0

        if user_status is None:
            optional_time_used = 0

        else:
            optional_time_used = user_status.optional_time_used


        return optional_time_per_day - optional_time_used

    def request_time_extension(self, p_session_context: SessionContext, p_user: User,
                               p_time_extension_length: int, p_reference_date: datetime.date=None):

        optional_time_available= self.get_optional_time_available_in_minutes(p_session_context=p_session_context,
                                                                             p_user=p_user, p_reference_date=p_reference_date)

        if p_time_extension_length <= optional_time_available:

            process_infos = self.processs_handler_manager.get_process_infos()

            admin_info = self.admin_data_handler.get_admin_info(
                p_session_context=p_session_context, p_user_name=p_user.username, p_process_infos=process_infos)

            self.time_extension_entity_manager.set_time_extension_for_admin_info_and_session(
                p_session_context=p_session_context, p_admin_info=admin_info,
                p_user_name=p_user.username, p_delta=p_time_extension_length)

            session = p_session_context.get_session()

            if p_reference_date is None:
                p_reference_date = datetime.date.today()

            user_status = self.daily_user_status_entity_manager.get_user_status(
                p_user_id=p_user.id, p_session_context=p_session_context, p_reference_date=p_reference_date)

            if user_status is None:
                user_status = DailyUserStatus()
                session.add(user_status)
                user_status.reference_date = p_reference_date
                user_status.user = p_user
                user_status.optional_time_used = p_time_extension_length

            else:
                user_status.optional_time_used += p_time_extension_length

            session.commit()

            return flask.Response("OK", status=constants.HTTP_STATUS_CODE_OK, mimetype=MIME_TYPE_APPLICATION_JSON)

        else:
            return self.api_error(p_message="requested time extension too large",
                                  p_status_code=constants.HTTP_STATUS_CODE_RANGE_NOT_SATISFIABLE)

    def destroy(self):
        API_BLUEPRINT_ADAPTER.unassign_view_handler_instances()
