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

from little_brother import constants
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

        if access_token != self._config.access_token:
            fmt = "Received invalid access token from host '{hostname}'"
            self._logger.warning(fmt.format(hostname=hostname))
            return None

        return (hostname, json_events)

    def send_events(self, p_hostname, p_events):

        url = self._get_api_url(constants.API_REL_URL_EVENTS)

        data = {
            constants.JSON_ACCESS_TOKEN: self._config.access_token,
            constants.JSON_HOSTNAME: p_hostname,
            constants.JSON_EVENTS: p_events}

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
