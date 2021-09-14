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

from little_brother import constants, entity_forms
from little_brother import rule_override
from little_brother.persistence.session_context import SessionContext
from little_brother.web.base_view_handler import BaseViewHandler
from python_base_app import tools
from some_flask_helpers import blueprint_adapter

TIME_EXTENSION_SUBMIT_PATTERN = "time_extension_{username}_(off|-?[0-9]+)"

BLUEPRINT_ADAPTER = blueprint_adapter.BlueprintAdapter()


# Dummy function to trigger extraction by pybabel...
def _(x):
    return x


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
                    admin_infos = self.admin_data_handler.get_admin_infos(
                        p_session_context=session_context,
                        p_process_infos=self.processs_handler_manager.get_process_infos(),
                        p_user_names=self.user_manager.usernames)

                    forms = self.get_admin_forms(p_admin_infos=admin_infos)

                    valid_and_submitted, submitted = self.validate(p_forms=forms)

                    if valid_and_submitted:
                        self.save_admin_data(admin_infos, forms)
                        self.handle_button_press(admin_infos, request, session_context)
                        return flask.redirect(flask.url_for("admin.main_view"))

                    if not submitted:
                        self.load_from_model(admin_infos, forms)

                    template_dict = {}
                    self.add_general_template_data(p_dict=template_dict)
                    template_dict["forms"] = forms
                    template_dict["admin_infos"] = admin_infos
                    template_dict["navigation"] = {
                        'current_view': constants.ADMIN_BLUEPRINT_NAME + "." + constants.ADMIN_VIEW_NAME
                    }
                    self.add_version_info(p_dict=template_dict)

                    page = flask.render_template(constants.ADMIN_HTML_TEMPLATE, **template_dict)

                except Exception as e:
                    return self.handle_rendering_exception(p_page_name="admin page", p_exception=e)

                return page

    def load_from_model(self, p_admin_infos, p_forms):

        for admin_info in p_admin_infos:
            for day_info in admin_info.day_infos:
                p_forms[day_info.html_key].load_from_model(p_model=day_info.override)

    def handle_button_press(self, p_admin_infos, p_request, p_session_context):

        for admin_info in p_admin_infos:
            username = admin_info.username
            submit_regex = re.compile(TIME_EXTENSION_SUBMIT_PATTERN.format(username=username))
            result = submit_regex.match(p_request.form['submit'])

            if result is not None:
                delta = int(result.group(1))

                self.time_extension_entity_manager.set_time_extension_for_admin_info_and_session(
                    p_session_context=p_session_context, p_user_name=username,
                    p_admin_info=admin_info, p_delta=delta)

    @staticmethod
    def get_admin_forms(p_admin_infos):

        forms = {}

        forms['dummy'] = entity_forms.DummyAdminForm(meta={'csrf': True})

        for admin_info in p_admin_infos:
            for day_info in admin_info.day_infos:
                form = rule_override.RuleOverrideForm(prefix=day_info.html_key + '_', meta={'csrf': True})
                forms[day_info.html_key] = form

        return forms

    def save_admin_data(self, p_admin_infos, p_forms):

        for admin_info in p_admin_infos:
            for day_info in admin_info.day_infos:
                form = p_forms[day_info.html_key]

                if form.differs_from_model(p_model=day_info.override):
                    form.save_to_model(p_model=day_info.override)
                    self.admin_data_handler.update_rule_override(day_info.override)
