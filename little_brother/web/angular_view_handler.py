# -*- coding: utf-8 -*-
# Copyright (C) 2019-2024  Marcus Rickert
#
# See https://github.com/marcus67/python_base_app
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
import os.path

# Ideas taken from https://realpython.com/handling-user-authentication-with-angular-and-flask/

import flask
import flask.wrappers
import some_flask_helpers
from flask import send_from_directory

import python_base_app
from little_brother.base_view_handler import BaseViewHandler

ANGULAR_BLUEPRINT_NAME = 'angular-index-and-proxy'
ANGULAR_BLUEPRINT_ADAPTER = some_flask_helpers.BlueprintAdapter()

ANGULAR_INDEX_URL = '/'
ANGULAR_INDEX_ENDPOINT_NAME = "INDEX"

ANGULAR_PROXY_URL = '/<path:path>'
ANGULAR_PROXY_ENDPOINT_NAME = "PATH"


def _(x):
    return x


class AngularViewHandler(BaseViewHandler):

    def __init__(self, p_package, p_rel_static_folder="angular"):
        super().__init__(p_blueprint_name=ANGULAR_BLUEPRINT_NAME, p_blueprint_adapter=ANGULAR_BLUEPRINT_ADAPTER,
                         p_package=p_package)

        self._static_folder = os.path.join("static", p_rel_static_folder)

        # self._blueprint = flask.Blueprint(ANGULAR_BLUEPRINT_NAME, python_base_app.__name__)
        # ANGULAR_BLUEPRINT_ADAPTER.assign_view_handler_instance(
        #     p_blueprint=self._blueprint, p_view_handler_instance=self)
        # ANGULAR_BLUEPRINT_ADAPTER.check_view_methods()

    @ANGULAR_BLUEPRINT_ADAPTER.route_method(p_rule=ANGULAR_INDEX_URL, endpoint=ANGULAR_INDEX_URL, methods=["GET"])
    def index(self):
        return send_from_directory(self._static_folder, "index.html")

    @ANGULAR_BLUEPRINT_ADAPTER.route_method(p_rule=ANGULAR_PROXY_URL, endpoint=ANGULAR_PROXY_URL, methods=["GET"])
    def proxy(self, path):
        return send_from_directory(self._static_folder, path)

    def destroy(self):
        ANGULAR_BLUEPRINT_ADAPTER.unassign_view_handler_instances()
