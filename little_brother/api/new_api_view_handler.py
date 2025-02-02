# -*- coding: utf-8 -*-
import datetime

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

import flask
import jsonpickle
from flask import jsonify

from little_brother import constants
from little_brother import dependency_injection
from little_brother.api.master_connector import MasterConnector
from little_brother.base_view_handler import BaseViewHandler
from little_brother.event_handler import EventHandler
from little_brother.persistence.persistent_user import User
from little_brother.persistence.persistent_user_entity_manager import UserEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.process_handler_manager import ProcessHandlerManager
from little_brother.rule_override import RuleOverride
from little_brother.transport.rule_set_to import RuleSetTO
from little_brother.transport.user_to import UserTO
from little_brother.transport.user_transport_manager import UserTransportManager
from python_base_app import tools
from python_base_app.angular_auth_view_handler import AngularAuthViewHandler
from python_base_app.base_user_handler import BaseUserHandler
from python_base_app.tools import objectify_dict, get_time_from_iso_8601
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

        self._master_connector: MasterConnector | None = None
        self._auth_view_handler: AngularAuthViewHandler | None = None
        self._event_handler: EventHandler | None = None
        self._languages = p_languages
        self._user_entity_manager: UserEntityManager | None = None
        self._process_handler_manager = None
        self._user_handler: BaseUserHandler | None = None 

    @property
    def user_entity_manager(self) -> UserEntityManager:

        if self._user_entity_manager is None:
            self._user_entity_manager = dependency_injection.container[UserEntityManager]
        return self._user_entity_manager

    @property
    def user_handler(self) -> BaseUserHandler:

        if self._user_handler is None:
            self._user_handler = dependency_injection.container[BaseUserHandler]
        return self._user_handler

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

    @property
    def process_handler_manager(self) -> ProcessHandlerManager:
        if self._process_handler_manager is None:
            self._process_handler_manager = dependency_injection.container[ProcessHandlerManager]

        return self._process_handler_manager

    def measure(self, p_hostname, p_service, p_duration):

        self.app_control.set_prometheus_http_requests_summary(p_hostname=p_hostname,
                                                              p_service=p_service,
                                                              p_duration=p_duration)

    def api_error(self, p_message, p_status_code=constants.HTTP_STATUS_CODE_NOT_FOUND):
        if isinstance(p_message, dict):
            return jsonify(p_message), p_status_code

        return jsonify({
            constants.JSON_STATUS: "error",
            constants.JSON_ERROR: p_message
        }), p_status_code

    def api_ok(self) -> tuple[any, int]:
        return jsonify({constants.JSON_STATUS: "OK"}), 200

    def missing_parameter_error(self, p_parameter_name):
        msg_format = _("parameter '{parameter_name}' not specified")
        msg = msg_format.format(parameter_name=p_parameter_name)
        return self.api_error(p_message=msg)

    def invalid_parameter_format_error(self, p_parameter_name, p_value):
        msg = f"parameter '{p_parameter_name}' with value '{p_value}' has wrong format"
        return self.api_error(p_message=msg, p_status_code=400)

    def user_id_not_exist_error(self, p_user_id):
        msg = f"user id '{p_user_id}' does not exist or is not being monitored"
        return self.api_error(p_message=msg, p_status_code=404)

    def user_not_authorized_error(self, p_user_id:int):
        return self.api_error(p_message=f"User id {p_user_id} does not have access to this ressource",
                              p_status_code=constants.HTTP_STATUS_CODE_UNAUTHORIZED)

    def invalid_secret_error(self):
        return self.api_error(p_message="invalid access code",
                              p_status_code=constants.HTTP_STATUS_CODE_UNAUTHORIZED)

    def internal_server_error(self, p_exception: Exception):
        return self.api_error(p_message=f"internal server error: {p_exception.__class__.__name__}: {p_exception!s}",
                              p_status_code=constants.HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR)

    def destroy(self):
        API_BLUEPRINT_ADAPTER.unassign_view_handler_instances()

    def check_access(self, p_session_context:SessionContext, p_authorization_result: dict,
                     p_active_user_id: int = None) -> bool:

        if p_authorization_result["is_admin"]:
            return True

        if p_active_user_id is None:

            return False

        logged_user_id = p_authorization_result.get("user_id", None)

        if not logged_user_id:
            return False

        return  logged_user_id == p_active_user_id


    #  TODO: Remove copy in api_view_handler!
    def extend_time_extension_for_session(self, p_session_context, p_user_name, p_delta_extension,
                                          p_reference_time=None):

        process_infos = self.process_handler_manager.get_process_infos()

        admin_info = self.admin_data_handler.get_admin_info(
            p_session_context=p_session_context, p_user_name=p_user_name, p_process_infos=process_infos)

        session_active = admin_info.user_info[
                             "active_stat_info"].current_activity_start_time is not None

        active_rule_result_info = admin_info.user_info["active_rule_result_info"]
        session_end_datetime = active_rule_result_info.session_end_datetime

        self.time_extension_entity_manager.set_time_extension_for_session(
            p_session_context=p_session_context, p_user_name=p_user_name,
            p_session_active=session_active, p_delta_extension=p_delta_extension,
            p_session_end_datetime=session_end_datetime,
            p_reference_time=p_reference_time)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_REL_URL_ABOUT, methods=["GET"])
    def api_about(self):
        request = flask.request
        with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                               p_service=self.simplify_url(request.url_rule),
                                                               p_duration=duration)):
            try:
                result, http_status = self.auth_view_handler.check_authorization(
                    p_request=request, p_admin_required=False)

                if http_status != 200:
                    return self.api_error(p_message=result, p_status_code=http_status)

                template_dict = {}
                self.add_general_template_data(p_dict=template_dict, p_add_authentication_data=False)
                template_dict["languages"] = sorted(
                    [(a_locale, a_language) for a_locale, a_language in self._languages.items()])

                return jsonify(template_dict), 200

            except Exception as e:
                return self.internal_server_error(p_exception=e)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_REL_URL_STATUS, methods=["GET"])
    def api_status(self):
        request = flask.request
        try:
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=self.simplify_url(request.url_rule),
                                                                   p_duration=duration)):
                result, http_status = self.auth_view_handler.check_authorization(
                    p_request=request, p_admin_required=False)

                if http_status != 200:
                    return self.api_error(p_message=result, p_status_code=http_status)

                # TODO: restrict access to status of logged in user if non-admin!
                with SessionContext(p_persistence=self.persistence) as session_context:
                    process_infos = self.processs_handler_manager.get_process_infos()
                    user_status_tos = self.admin_data_handler.get_user_status_transfer_objects(
                        p_session_context=session_context,
                        p_process_infos=process_infos)

                return jsonpickle.encode(user_status_tos), 200

        except Exception as e:
            return self.internal_server_error(p_exception=e)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_REL_URL_STATUS_DETAILS, methods=["GET"])
    def api_status_detail(self, user_id):
        request = flask.request
        try:
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=self.simplify_url(request.url_rule),
                                                                   p_duration=duration)):
                result, http_status = self.auth_view_handler.check_authorization(
                    p_request=request, p_admin_required=False)

                if http_status != 200:
                    return self.api_error(p_message=result, p_status_code=http_status)

                with SessionContext(p_persistence=self.persistence) as session_context:
                    user: User = self.user_entity_manager.get_by_id(p_session_context=session_context, p_id=user_id)

                    if user is None:
                        return self.user_id_not_exist_error(p_user_id=user_id)

                    process_infos = self.processs_handler_manager.get_process_infos()
                    user_status_to = self.admin_data_handler.get_user_status_and_details_transfer_object(
                        p_session_context=session_context,
                        p_process_infos=process_infos,
                        p_user_id=user_id)

                return jsonpickle.encode(user_status_to), 200

        except Exception as e:
            return self.internal_server_error(p_exception=e)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_REL_URL_ADMIN, methods=["GET"])
    def api_admin(self):
        request = flask.request
        try:
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=self.simplify_url(request.url_rule),
                                                                   p_duration=duration)):
                result, http_status = self.auth_view_handler.check_authorization(p_request=request)

                if http_status != 200:
                    return self.api_error(p_message=result, p_status_code=http_status)

                with SessionContext(p_persistence=self.persistence) as session_context:
                    process_infos = self.processs_handler_manager.get_process_infos()
                    user_status_tos = self.admin_data_handler.get_user_admin_transfer_objects(
                        p_session_context=session_context,
                        p_process_infos=process_infos)

                return jsonpickle.encode(user_status_tos), 200

        except Exception as e:
            return self.internal_server_error(p_exception=e)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_REL_URL_ADMIN_LIST_TIME_EXTENSIONS, methods=["GET"])
    def api_admin_time_extensions(self, user_id):
        request = flask.request
        try:
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=self.simplify_url(request.url_rule),
                                                                   p_duration=duration)):
                result, http_status = self.auth_view_handler.check_authorization(
                    p_request=request, p_admin_required=False)

                if http_status != 200:
                    return self.api_error(p_message=result, p_status_code=http_status)

                with SessionContext(p_persistence=self.persistence) as session_context:
                    user: User = self.user_entity_manager.get_by_id(p_session_context=session_context, p_id=user_id)

                    if user is None:
                        return self.user_id_not_exist_error(p_user_id=user_id)

                    time_extension_periods = self.admin_data_handler.get_user_admin_time_extensions(
                        p_session_context=session_context,
                        p_user_id=user_id)

                return jsonpickle.encode(time_extension_periods), 200

        except Exception as e:
            return self.internal_server_error(p_exception=e)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_REL_URL_ADMIN_DETAILS, methods=["GET"])
    def api_admin_detail(self, user_id):
        request = flask.request
        try:
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=self.simplify_url(request.url_rule),
                                                                   p_duration=duration)):
                result, http_status = self.auth_view_handler.check_authorization(p_request=request)

                if http_status != 200:
                    return self.api_error(p_message=result, p_status_code=http_status)

                with SessionContext(p_persistence=self.persistence) as session_context:
                    user: User = self.user_entity_manager.get_by_id(p_session_context=session_context, p_id=user_id)

                    if user is None:
                        return self.user_id_not_exist_error(p_user_id=user_id)

                    process_infos = self.processs_handler_manager.get_process_infos()
                    user_status_to = self.admin_data_handler.get_admin_status_and_details_transfer_object(
                        p_session_context=session_context,
                        p_process_infos=process_infos,
                        p_user_id=user_id)

                return jsonpickle.encode(user_status_to), 200

        except Exception as e:
            return self.internal_server_error(p_exception=e)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_REL_URL_CONTROL, methods=["GET"])
    def api_control(self):
        request = flask.request
        try:
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=self.simplify_url(request.url_rule),
                                                                   p_duration=duration)):
                result, http_status = self.auth_view_handler.check_authorization(
                    p_request=request, p_admin_required=False)

                if http_status != 200:
                    return self.api_error(p_message=result, p_status_code=http_status)

                control_to = self.admin_data_handler.get_control_transfer_object()

                return jsonpickle.encode(control_to, unpicklable=False), 200

        except Exception as e:
            return self.internal_server_error(p_exception=e)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_REL_URL_ADMIN_EXTEND_TIME_EXTENSION, methods=["POST"])
    def api_admin_extend_time_extension(self, user_id, delta_time_extension_in_minutes):
        request = flask.request

        try:
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=self.simplify_url(request.url_rule),
                                                                   p_duration=duration)):
                result, http_status = self.auth_view_handler.check_authorization(p_request=request)

                if http_status != 200:
                    return self.api_error(p_message=result, p_status_code=http_status)

                with SessionContext(p_persistence=self.persistence) as session_context:

                    user: User = self.user_entity_manager.get_by_id(p_session_context=session_context, p_id=user_id)

                    if user is None:
                        return self.user_id_not_exist_error(p_user_id=user_id)
                    
                    try:
                        delta_extension: int = int(delta_time_extension_in_minutes)

                    except ValueError:
                        return self.invalid_parameter_format_error(
                            p_parameter_name="delta_time_extension_in_minutes", p_value=delta_time_extension_in_minutes)

                    self.extend_time_extension_for_session(
                        p_session_context=session_context, p_user_name=user.username,
                        p_delta_extension=delta_extension)

                return self.api_ok()

        except Exception as e:
            return self.internal_server_error(p_exception=e)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_REL_URL_ADMIN_UPDATE_RULE_OVERRIDE, methods=["POST"])
    def api_admin_update_rule_override(self, user_id, reference_date):
        request = flask.request

        try:
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=self.simplify_url(request.url_rule),
                                                                   p_duration=duration)):
                result, http_status = self.auth_view_handler.check_authorization(p_request=request)

                if http_status != 200:
                    return self.api_error(p_message=result, p_status_code=http_status)

                try:
                    date : datetime.date = datetime.date.fromisoformat(reference_date)

                except ValueError:
                    self.invalid_parameter_format_error(p_parameter_name="reference_date", p_value=reference_date)

                with SessionContext(p_persistence=self.persistence) as session_context:

                    user: User = self.user_entity_manager.get_by_id(p_session_context=session_context, p_id=user_id)

                    if user is None:
                        return self.user_id_not_exist_error(p_user_id=user_id)

                    override_to: RuleSetTO = objectify_dict(request.json, RuleSetTO,
                                              p_attribute_readers={
                                                  "min_time_of_day": tools.get_string_as_time,
                                                  "max_time_of_day": tools.get_string_as_time,
                                              })
                    override : RuleOverride = RuleOverride(
                        p_reference_date=date,
                        p_username=user.username,
                        p_min_time_of_day=get_time_from_iso_8601(override_to.min_time_of_day_in_iso_8601),
                        p_max_time_of_day=get_time_from_iso_8601(override_to.max_time_of_day_in_iso_8601),
                        p_max_time_per_day=override_to.max_time_per_day_in_seconds,
                        p_max_activity_duration=override_to.max_activity_duration_in_seconds,
                        p_min_break=override_to.min_break_in_seconds,
                        p_free_play=override_to.free_play
                    )

                    self.admin_data_handler.update_rule_override(override)

                return self.api_ok()

        except Exception as e:
            return self.internal_server_error(p_exception=e)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_REL_URL_USERS, methods=["GET"])
    def api_users(self):
        request = flask.request
        try:
            with (tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                    p_service=self.simplify_url(request.url_rule),
                                                                    p_duration=duration))):
                result, http_status = self.auth_view_handler.check_authorization(
                    p_request=request, p_admin_required=False)

                if http_status != 200:
                    return self.api_error(p_message=result, p_status_code=http_status)

                with SessionContext(p_persistence=self.persistence) as session_context:

                    active_user_id = self.user_entity_manager.add_user_id_to_authorization_result(
                        p_session_context=session_context, p_authorization_result=result["authorization"]
                    )

                    users = self.user_entity_manager.get_sorted_users(session_context)
                    unmonitored_users = self.app_control.get_unmonitored_users(session_context)

                    user_tos = UserTransportManager.get_user_tos(
                        p_users=users, p_unmonitored_users=unmonitored_users, p_active_user_id=active_user_id)

                return jsonpickle.encode(user_tos), 200

        except Exception as e:
            return self.internal_server_error(p_exception=e)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_REL_URL_USER, methods=["GET"])
    def api_get_user(self, user_id):
        request = flask.request
        try:
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=self.simplify_url(request.url_rule),
                                                                   p_duration=duration)):
                result, http_status = self.auth_view_handler.check_authorization(p_request=request,
                                                                                 p_admin_required=False)


                if http_status != 200:
                    return self.api_error(p_message=result, p_status_code=http_status)

                with SessionContext(p_persistence=self.persistence) as session_context:
                    if not self.check_access(p_session_context=session_context,
                                             p_authorization_result=result['authorization'],
                                             p_active_user_id=int(user_id)):
                        return self.user_not_authorized_error(p_user_id=user_id)

                    user = self.user_entity_manager.get_by_id(p_session_context=session_context, p_id=user_id)
                    user_to = UserTransportManager.get_user_to(p_user=user)

                return jsonpickle.encode(user_to), 200

        except Exception as e:
            return self.internal_server_error(p_exception=e)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_REL_URL_USER, methods=["PUT"])
    def api_put_user(self, user_id):
        request = flask.request
        try:
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=self.simplify_url(request.url_rule),
                                                                   p_duration=duration)):
                result, http_status = self.auth_view_handler.check_authorization(p_request=request)

                if http_status != 200:
                    return self.api_error(p_message=result, p_status_code=http_status)

                with SessionContext(p_persistence=self.persistence) as session_context:

                    user: User = self.user_entity_manager.get_by_id(p_session_context=session_context, p_id=user_id)

                    if user is None:
                        return self.user_id_not_exist_error(p_user_id=user_id)

                    user_to: UserTO = objectify_dict(request.json, UserTO)

                    session = session_context.get_session()
                    user.active = user_to.active
                    user.first_name = user_to.first_name
                    user.last_name = user_to.last_name
                    user.locale = user_to.locale
                    
                    session.commit()
                    self.actions_after_user_change(p_session_context=session_context)

                return self.api_ok()

        except Exception as e:
            return self.internal_server_error(p_exception=e)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_REL_URL_PUT_USER, methods=["POST"])
    def api_post_user(self, username):
        request = flask.request
        try:
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=self.simplify_url(request.url_rule),
                                                                   p_duration=duration)):
                result, http_status = self.auth_view_handler.check_authorization(p_request=request)

                if http_status != 200:
                    return self.api_error(p_message=result, p_status_code=http_status)

                with SessionContext(p_persistence=self.persistence) as session_context:

                    user_id = self.app_control.add_new_user(
                        p_session_context=session_context,
                        p_username=username, p_locale=self.locale_helper.locale)

                    if user_id is None:
                        return self.api_error(p_message=f"Cannot create user for username '{username}'",
                                              p_status_code=constants.HTTP_STATUS_CODE_CONFLICT)

                    return jsonpickle.encode({'user_id': user_id}), 200


        except Exception as e:
            return self.internal_server_error(p_exception=e)

    @API_BLUEPRINT_ADAPTER.route_method(p_rule=constants.API_REL_URL_DELETE_USER, methods=["DELETE"])
    def api_delete_user(self, username):
        request = flask.request
        try:
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=self.simplify_url(request.url_rule),
                                                                   p_duration=duration)):
                result, http_status = self.auth_view_handler.check_authorization(p_request=request)

                if http_status != 200:
                    return self.api_error(p_message=result, p_status_code=http_status)

                with SessionContext(p_persistence=self.persistence) as session_context:

                    self.user_entity_manager.delete_user(
                        p_session_context=session_context, p_username=username)
                    self.actions_after_user_change(p_session_context=session_context)

                    return self.api_ok()


        except Exception as e:
            return self.internal_server_error(p_exception=e)

    def actions_after_user_change(self, p_session_context: SessionContext):
        self._persistence.clear_cache()
        self.app_control.send_config_to_all_clients()
        self.user_manager.reset_users(p_session_context=p_session_context)
        self.app_control.reset_process_patterns()
