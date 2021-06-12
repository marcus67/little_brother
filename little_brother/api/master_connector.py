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

from little_brother import constants, user_status
from python_base_app import base_rest_api_access
from python_base_app import exceptions
from python_base_app import tools

SECTION_NAME = "MasterConnector"


class MasterConnectorConfigModel(base_rest_api_access.BaseRestAPIAccessConfigModel):

    def __init__(self):
        super().__init__(p_section_name=SECTION_NAME)


class MasterConnector(base_rest_api_access.BaseRestAPIAccess):

    def __init__(self, p_config):

        super().__init__(
            p_config=p_config,
            p_base_api_url=constants.API_URL,
            p_section_name=SECTION_NAME)

    def receive_events(self, p_json_data):

        access_token = p_json_data[constants.JSON_ACCESS_TOKEN]
        hostname = p_json_data[constants.JSON_HOSTNAME]
        json_events = p_json_data[constants.JSON_EVENTS]
        json_slave_stats = p_json_data.get(constants.JSON_CLIENT_STATS, None)

        if access_token != self._config.access_token:
            fmt = "Received invalid access token from host '{hostname}'"
            self._logger.warning(fmt.format(hostname=hostname))
            return None

        if json_slave_stats is not None:
            return (hostname, json_events, json_slave_stats)

        else:
            return (hostname, json_events)

    def encode_event(self, p_hostname, p_events, p_client_stats=None):
        event = {
            constants.JSON_ACCESS_TOKEN: self._config.access_token,
            constants.JSON_HOSTNAME: p_hostname,
            constants.JSON_EVENTS: p_events
        }

        if p_client_stats is not None:
            event[constants.JSON_CLIENT_STATS] = p_client_stats

        return event

    def send_events(self, p_hostname, p_events, p_client_stats=None):

        url = self._get_api_url(constants.API_REL_URL_EVENTS)

        data = self.encode_event(p_hostname=p_hostname, p_events=p_events, p_client_stats=p_client_stats)

        try:
            result = self.execute_api_call(
                p_url=url,
                p_method="POST",
                p_mime_type="application/json",
                p_data=json.dumps(obj=data, cls=tools.ObjectEncoder),
                p_jsonify=True)

        except exceptions.UnauthorizedException:

            fmt = "cannot send events: invalid access token"
            self._logger.error(fmt)
            result = None

        return result

    # Note: the following method is functionally identical the method in little_brother_taskbar/status_connector.py
    def request_status(self, p_username):

        url = self._get_api_url(constants.API_REL_URL_STATUS)

        try:
            api_result = self.execute_api_call(
                p_url=url,
                p_method="GET",
                p_parameters={constants.API_URL_PARAM_USERNAME: p_username},
                p_jsonify=True)

            result = tools.objectify_dict(p_dict=api_result,
                                          p_class=user_status.UserStatus,
                                          p_attribute_classes={})

        except exceptions.ArtifactNotFoundException as e:
            result = None

        return result

    # Note: the following method is functionally identical the method in little_brother_taskbar/status_connector.py
    def request_time_extension(self, p_username:str, p_access_code:str, p_extension_length:int) -> int:

        url = self._get_api_url(constants.API_REL_URL_REQUEST_TIME_EXTENSION)

        try:
            self.execute_api_call(
                p_url=url,
                p_method="POST",
                p_parameters={
                    constants.API_URL_PARAM_USERNAME: p_username,
                    constants.API_URL_PARAM_SECRET: p_access_code,
                    constants.API_URL_PARAM_EXTENSION_LENGTH: p_extension_length
                },
                p_jsonify=True)

        except exceptions.RangeNotSatisfiableException:
            return constants.HTTP_STATUS_CODE_RANGE_NOT_SATISFIABLE

        except exceptions.UnauthorizedException:
            return constants.HTTP_STATUS_CODE_UNAUTHORIZED

        except exceptions.ArtifactNotFoundException:
            return constants.HTTP_STATUS_CODE_NOT_FOUND

        return constants.HTTP_STATUS_CODE_OK

