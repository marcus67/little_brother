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

from little_brother import constants
from little_brother.persistence.session_context import SessionContext
from little_brother.web.base_view_handler import BaseViewHandler
from python_base_app import tools
from python_base_app.base_web_server import BaseWebServer
from some_flask_helpers import blueprint_adapter

# Dummy function to trigger extraction by pybabel...
_ = lambda x: x

BLUEPRINT_NAME = "status"

INDEX_BLUEPRINT_ADAPTER = blueprint_adapter.BlueprintAdapter()


class StatusViewHandler(BaseViewHandler):

    def __init__(self, p_package):

        super().__init__(p_blueprint_name=BLUEPRINT_NAME, p_blueprint_adapter=INDEX_BLUEPRINT_ADAPTER,
                         p_package=p_package)

    @INDEX_BLUEPRINT_ADAPTER.route_method("/")
    def entry_view(self):

        return flask.redirect(flask.url_for("status.main_view"))

    @INDEX_BLUEPRINT_ADAPTER.route_method("/status", endpoint="main_view")
    def status_view(self):

        request = flask.request
        with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                               p_service=self.simplify_url(request.url_rule),
                                                               p_duration=duration)):
            with SessionContext(p_persistence=self.persistence) as session_context:
                try:
                    process_infos = self.processs_handler_manager.get_process_infos()
                    user_infos = self.admin_data_handler.get_user_status_infos(p_session_context=session_context,
                                                                               p_process_infos=process_infos)

                    sorted_infos = sorted(user_infos.values(), key=lambda info:info['full_name'])

                    page = flask.render_template(
                        constants.STATUS_HTML_TEMPLATE,
                        rel_font_size=self.get_rel_font_size(),
                        user_infos=sorted_infos,
                        has_downtime_today=self.has_downtime_today(p_user_infos=user_infos),
                        app_control_config=self.app_control._config,
                        authentication=BaseWebServer.get_authentication_info(),
                        navigation={
                            'current_view': constants.STATUS_BLUEPRINT_NAME + "." + constants.STATUS_VIEW_NAME},
                    )

                except Exception as e:
                    return self.handle_rendering_exception(p_page_name="status page", p_exception=e)

                return page
