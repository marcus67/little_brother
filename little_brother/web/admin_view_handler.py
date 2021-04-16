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

import re

import flask
import flask_login
import flask_wtf

from little_brother import constants
from little_brother import rule_override
from little_brother.persistence.session_context import SessionContext
from little_brother.web.base_view_handler import BaseViewHandler, FORM_ID_CSRF
from python_base_app import tools
from python_base_app.base_web_server import BaseWebServer
from some_flask_helpers import blueprint_adapter

TIME_EXTENSION_SUBMIT_PATTERN = "time_extension_{username}_(off|-?[0-9]+)"

BLUEPRINT_ADAPTER = blueprint_adapter.BlueprintAdapter()

# Dummy function to trigger extraction by pybabel...
_ = lambda x: x


class AdminViewHandler(BaseViewHandler):

    def __init__(self, p_package):

        super().__init__(p_blueprint_name=constants.ADMIN_BLUEPRINT_NAME, p_blueprint_adapter=BLUEPRINT_ADAPTER,
                         p_package=p_package)

    @BLUEPRINT_ADAPTER.route_method("/admin", endpoint="main_view", methods=["GET", "POST"])
    @flask_login.login_required
    def admin_view(self):

        request = flask.request
        with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                               p_service=self.simplify_url(request.url_rule),
                                                               p_duration=duration)):
            with SessionContext(p_persistence=self.persistence) as session_context:

                try:
                    admin_infos = self.app_control.get_admin_infos(p_session_context=session_context)
                    forms = self.get_admin_forms(p_admin_infos=admin_infos)

                    valid_and_submitted = True
                    submitted = False

                    for form in forms.values():
                        if not form.validate_on_submit():
                            valid_and_submitted = False

                        if form.is_submitted():
                            submitted = True

                    if valid_and_submitted:
                        self.save_admin_data(admin_infos, forms)

                        for admin_info in admin_infos:

                            username = admin_info.username
                            submit_regex = re.compile(TIME_EXTENSION_SUBMIT_PATTERN.format(username=username))
                            result = submit_regex.match(request.form['submit'])

                            if result is not None:
                                delta = int(result.group(1))

                                reference_time = tools.get_current_time()
                                start_datetime = reference_time

                                session_active = admin_info.user_info[
                                                     "active_stat_info"].current_activity_start_time is not None

                                if session_active:
                                    active_rule_result_info = admin_info.user_info["active_rule_result_info"]

                                    if active_rule_result_info.session_end_datetime is not None:
                                        start_datetime = active_rule_result_info.session_end_datetime

                                self.time_extension_entity_manager.set_time_extension(
                                    p_session_context=session_context,
                                    p_username=username,
                                    p_reference_datetime=reference_time,
                                    p_start_datetime=start_datetime,
                                    p_time_delta=delta
                                )

                        return flask.redirect(flask.url_for("admin.main_view"))

                    if not submitted:
                        for admin_info in admin_infos:
                            for day_info in admin_info.day_infos:
                                forms[day_info.html_key].load_from_model(p_model=day_info.override)

                    page = flask.render_template(
                        constants.ADMIN_HTML_TEMPLATE,
                        rel_font_size=self.get_rel_font_size(),
                        admin_infos=admin_infos,
                        authentication=BaseWebServer.get_authentication_info(),
                        forms=forms,
                        navigation={
                            'current_view': constants.ADMIN_BLUEPRINT_NAME + "." + constants.ADMIN_VIEW_NAME})

                except Exception as e:

                    msg = "Exception '{exception}' while generating admin page"
                    self._logger.exception(msg.format(exception=str(e)))

                return page

    @staticmethod
    def get_admin_forms(p_admin_infos):

        forms = {}

        forms[FORM_ID_CSRF] = flask_wtf.FlaskForm(meta={'csrf': False})

        for admin_info in p_admin_infos:
            for day_info in admin_info.day_infos:
                form = rule_override.RuleOverrideForm(prefix=day_info.html_key + '_', meta={'csrf': False})
                forms[day_info.html_key] = form

        return forms

    def save_admin_data(self, p_admin_infos, p_forms):

        for admin_info in p_admin_infos:
            for day_info in admin_info.day_infos:
                form = p_forms[day_info.html_key]

                if form.differs_from_model(p_model=day_info.override):
                    form.save_to_model(p_model=day_info.override)
                    self.app_control.update_rule_override(day_info.override)
