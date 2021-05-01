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
import flask_login
import flask_wtf

from little_brother import constants
from little_brother import entity_forms
from little_brother.persistence.session_context import SessionContext
from little_brother.web.base_view_handler import BaseViewHandler, FORM_ID_CSRF
from python_base_app import custom_fields
from python_base_app import tools
from python_base_app.base_web_server import BaseWebServer
from some_flask_helpers import blueprint_adapter

HTML_KEY_NEW_DEVICE = "NewDevice"

BLUEPRINT_ADAPTER = blueprint_adapter.BlueprintAdapter()

# Dummy function to trigger extraction by pybabel...
_ = lambda x: x


class DevicesViewHandler(BaseViewHandler):

    def __init__(self, p_package):

        super().__init__(p_blueprint_name=constants.DEVICES_BLUEPRINT_NAME, p_blueprint_adapter=BLUEPRINT_ADAPTER,
                         p_package=p_package)

    @staticmethod
    def get_devices_forms(p_devices):

        forms = {}
        forms[FORM_ID_CSRF] = flask_wtf.FlaskForm(meta={'csrf': False})
        uniqueness = custom_fields.Uniqueness(
            p_field_selectors=[lambda form: form.device_name, lambda form: form.hostname])

        for device in p_devices:
            form = entity_forms.DeviceForm(prefix='{id}_'.format(id=device.html_key), meta={'csrf': False})
            uniqueness.add_form(p_form=form)
            forms[device.device_name] = form

        return forms

    def save_devices_data(self, p_devices, p_forms):

        with SessionContext(p_persistence=self.persistence) as session_context:
            session = session_context.get_session()
            changed = False

            for device in p_devices:
                form = p_forms[device.device_name]
                device = self.device_entity_manager.get_by_device_name(
                    p_session_context=session_context, p_device_name=device.device_name)

                if device is not None and form.differs_from_model(p_model=device):
                    form.save_to_model(p_model=device)
                    changed = True

            session.commit()
            session.close()

            if changed:
                self.persistence.clear_cache()

    @BLUEPRINT_ADAPTER.route_method("/devices", endpoint="main_view", methods=["GET", "POST"])
    @flask_login.login_required
    def devices_view(self):

        with SessionContext(p_persistence=self.persistence) as session_context:
            request = flask.request
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=self.simplify_url(request.url_rule),
                                                                   p_duration=duration)):

                try:
                    devices = self.device_entity_manager.get_sorted_devices(session_context)
                    forms = self.get_devices_forms(p_devices=devices)

                    valid_and_submitted, submitted = self.validate(p_forms=forms)

                    if valid_and_submitted:
                        self.save_devices_data(devices, forms)

                        if request.form['submit'] == HTML_KEY_NEW_DEVICE:
                            self.device_entity_manager.add_new_device(
                                p_session_context=session_context,
                                p_name_pattern=self.gettext(constants.DEFAULT_DEVICE_NEW_NAME_PATTERN))
                            # TODO: after adding new device Devices window should be opened for new device
                        else:
                            for device in devices:
                                if request.form['submit'] == device.delete_html_key:
                                    self.device_entity_manager.delete_device(
                                        p_session_context=session_context, p_id=device.id)

                        return flask.redirect(flask.url_for("devices.main_view"))

                    if not submitted:
                        for device in devices:
                            forms[device.device_name].load_from_model(p_model=device)

                    page = flask.render_template(
                        constants.DEVICES_HTML_TEMPLATE,
                        rel_font_size=self.get_rel_font_size(),
                        devices=devices,
                        authentication=BaseWebServer.get_authentication_info(),
                        forms=forms,
                        new_device_html_key=HTML_KEY_NEW_DEVICE,
                        new_device_submit_value=HTML_KEY_NEW_DEVICE,
                        navigation={
                            'current_view': constants.DEVICES_BLUEPRINT_NAME + "." + constants.DEVICES_VIEW_NAME
                        },
                    )

                except Exception as e:
                    return self.handle_rendering_exception(p_page_name="devices page", p_exception=e)

            return page
