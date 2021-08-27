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

from little_brother import constants
from little_brother import entity_forms
from little_brother.persistence.session_context import SessionContext
from little_brother.web.base_view_handler import BaseViewHandler
from python_base_app import custom_fields
from python_base_app import tools
from python_base_app.base_web_server import BaseWebServer
from some_flask_helpers import blueprint_adapter

ID_PREFIX = '{id}_'

HTML_KEY_NEW_USER = "NewUser"

BLUEPRINT_ADAPTER = blueprint_adapter.BlueprintAdapter()

# Dummy function to trigger extraction by pybabel...
_ = lambda x: x


class UsersViewHandler(BaseViewHandler):

    def __init__(self, p_package, p_languages):

        super().__init__(p_blueprint_name=constants.USERS_BLUEPRINT_NAME, p_blueprint_adapter=BLUEPRINT_ADAPTER,
                         p_package=p_package)

        self._languages = p_languages

    @BLUEPRINT_ADAPTER.route_method("/users", endpoint="main_view", methods=["GET", "POST"])
    @flask_login.login_required
    def users_view(self):

        with SessionContext(p_persistence=self.persistence) as session_context:
            request = flask.request

            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=self.simplify_url(request.url_rule),
                                                                   p_duration=duration)):
                try:
                    users = self.user_entity_manager.get_sorted_users(session_context)
                    forms = self.get_users_forms(p_users=users, p_session_context=session_context)

                    valid_and_submitted, submitted = self.validate(p_forms=forms)

                    if valid_and_submitted:
                        self.save_users_data(p_users=users, p_forms=forms)
                        self.handle_button_press(p_forms=forms, p_request=request, p_session_context=session_context,
                                                 p_users=users)
                        return flask.redirect(flask.url_for("users.main_view"))

                    if not submitted:
                        self.load_from_model(p_forms=forms, p_users=users)

                    page = flask.render_template(
                        constants.USERS_HTML_TEMPLATE,
                        rel_font_size=self.get_rel_font_size(),
                        users=users,
                        authentication=BaseWebServer.get_authentication_info(),
                        forms=forms,
                        new_user_html_key=HTML_KEY_NEW_USER,
                        new_user_submit_value=HTML_KEY_NEW_USER,
                        navigation={
                            'current_view': constants.USERS_BLUEPRINT_NAME + "." + constants.USERS_VIEW_NAME
                        },
                    )

                except Exception as e:
                    return self.handle_rendering_exception(p_page_name="users page", p_exception=e)

            return page

    def load_from_model(self, p_forms, p_users):

        for user in p_users:
            p_forms[user.html_key].load_from_model(p_model=user)

            for ruleset in user.rulesets:
                p_forms[ruleset.html_key].load_from_model(p_model=ruleset)
                # provide a callback function so that the RuleSet can retrieve context summaries
                ruleset._get_context_rule_handler = self.rule_handler.get_context_rule_handler

            for user2device in user.devices:
                p_forms[user2device.html_key].load_from_model(p_model=user2device)

    def handle_button_press(self, p_forms, p_request, p_session_context, p_users):

        if p_request.form['submit'] == HTML_KEY_NEW_USER:
            username = p_forms[HTML_KEY_NEW_USER].username.data
            self.app_control.add_new_user(p_session_context=p_session_context,
                                          p_username=username, p_locale=self._locale_helper.locale)
            # TODO: after adding new user Users window should be opened for new user

        else:
            for user in p_users:
                if p_request.form['submit'] == user.delete_html_key:
                    self.user_entity_manager.delete_user(
                        p_session_context=p_session_context, p_username=user.username)
                    self.persistence.clear_cache()
                    self.app_control.send_config_to_all_slaves()

                elif p_request.form['submit'] == user.new_ruleset_html_key:
                    self.user_entity_manager.assign_ruleset(
                        p_session_context=p_session_context, p_username=user.username)

                elif p_request.form['submit'] == user.new_device_html_key:
                    device_id = int(p_forms[user.new_device_html_key].device_id.data)
                    self.user_2_device_entity_manager.add_user2device(
                        p_session_context=p_session_context, p_device_id=device_id,
                        p_username=user.username)

                else:
                    for ruleset in user.rulesets:
                        if p_request.form['submit'] == ruleset.delete_html_key:
                            self.rule_set_entity_manager.delete_ruleset(
                                p_session_context=p_session_context, p_ruleset_id=ruleset.id)

                        elif p_request.form['submit'] == ruleset.move_down_html_key:
                            self.rule_set_entity_manager.move_down_ruleset(
                                p_session_context=p_session_context, p_ruleset_id=ruleset.id)

                        elif p_request.form['submit'] == ruleset.move_up_html_key:
                            self.rule_set_entity_manager.move_up_ruleset(
                                p_session_context=p_session_context, p_ruleset_id=ruleset.id)

                    for user2device in user.devices:
                        if p_request.form['submit'] == user2device.delete_html_key:
                            self.user_2_device_entity_manager.delete_user2device(
                                p_session_context=p_session_context, p_user2device_id=user2device.id)

    def get_users_forms(self, p_session_context, p_users):

        forms = {}

        unmonitored_users = self.app_control.get_unmonitored_users(p_session_context)

        if len(unmonitored_users) > 0:
            new_user_form = entity_forms.NewUserForm(meta={'csrf': True})
            new_user_form.username.choices = [(username, username) for username in unmonitored_users]
            forms[HTML_KEY_NEW_USER] = new_user_form

        for user in p_users:
            form = entity_forms.UserForm(prefix=ID_PREFIX.format(id=user.html_key), meta={'csrf': True})
            form.locale.choices = sorted([(locale, language) for locale, language in self._languages.items()])
            forms[user.html_key] = form

            for ruleset in user.rulesets:
                localized_values = [(value, self.gettext(value))
                                    for value in self.rule_handler.get_context_rule_handler_choices()]

                if ruleset.fixed_context:
                    choices = self.add_labels([ruleset.context])

                else:
                    choices = self.add_labels(self.rule_handler.get_context_rule_handler_names())

                context_details_filters = [
                    lambda x: custom_fields.unlocalize(p_localized_values=localized_values, p_value=x)]

                form = entity_forms.create_rulesets_form(p_context_choices=choices,
                                                         p_localized_context_details=localized_values,
                                                         p_context_details_filters=context_details_filters,
                                                         prefix=ID_PREFIX.format(id=ruleset.html_key))
                forms[ruleset.html_key] = form

                form.context_details.validators = [
                    lambda a_form, a_field: self.rule_handler.validate_context_rule_handler_details(
                        p_context_name=a_form.context.data, p_context_details=a_field.data)]

            unmonitored_devices = self.app_control.get_unmonitored_devices(p_user=user,
                                                                           p_session_context=p_session_context)

            if len(unmonitored_devices) > 0:
                new_device_form = entity_forms.NewUser2DeviceForm(prefix=ID_PREFIX.format(id=user.html_key),
                                                                  meta={'csrf': True})
                new_device_form.device_id.choices = [(str(device.id), device.device_name) for device in
                                                     unmonitored_devices]
                forms[user.new_device_html_key] = new_device_form

            for user2device in user.devices:
                form = entity_forms.User2DeviceForm(prefix=ID_PREFIX.format(id=user2device.html_key),
                                                    meta={'csrf': True})
                forms[user2device.html_key] = form

        return forms

    def save_users_data(self, p_users, p_forms):

        with SessionContext(p_persistence=self.persistence) as session_context:
            session = session_context.get_session()
            changed = False

            for user in p_users:
                form = p_forms[user.html_key]
                a_persistent_user = self.user_entity_manager.get_by_username(
                    p_session_context=session_context, p_username=user.username)

                if a_persistent_user is not None and form.differs_from_model(p_model=a_persistent_user):
                    form.save_to_model(p_model=a_persistent_user)
                    changed = True

                for ruleset in user.rulesets:
                    form = p_forms[ruleset.html_key]
                    a_persistent_ruleset = self.rule_set_entity_manager.get_by_id(
                        p_session_context=session_context, p_id=ruleset.id)

                    if a_persistent_ruleset is not None and form.differs_from_model(p_model=a_persistent_ruleset):
                        form.save_to_model(p_model=a_persistent_ruleset)
                        changed = True

                for user2device in user.devices:
                    form = p_forms[user2device.html_key]
                    a_persistent_user_2_device = self.user_2_device_entity_manager.get_by_id(
                        p_session_context=session_context, p_id=user2device.id)

                    if a_persistent_user_2_device is not None and form.differs_from_model(
                            p_model=a_persistent_user_2_device):
                        form.save_to_model(p_model=a_persistent_user_2_device)
                        changed = True

            if changed:
                session.commit()

                self._persistence.clear_cache()
                self.app_control.send_config_to_all_slaves()
                self.user_manager.reset_users(p_session_context=session_context)

    def add_labels(self, p_value_list):

        return [(entry, self.gettext(entry)) for entry in p_value_list]
