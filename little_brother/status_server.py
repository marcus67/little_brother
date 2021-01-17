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

import gettext
import os

import babel.dates
import flask
import flask_babel
import flask_login
import flask_wtf

import little_brother
from some_flask_helpers import blueprint_adapter
from little_brother import api_view_handler
from little_brother import constants
from little_brother import entity_forms
from little_brother import git
from little_brother import persistence
from little_brother import rule_override
from little_brother import settings
from python_base_app import base_web_server
from python_base_app import custom_fields
from python_base_app import tools

LOCALE_REL_FONT_SIZES = {
    'bn': 125  # scale Bangla fonts to 125% for readability
}

SECTION_NAME = "StatusServer"

HEALTH_VIEW_NAME = "health"
HEALTH_REL_URL = "health"

INDEX_HTML_TEMPLATE = "index.template.html"
INDEX_REL_URL = "status"
INDEX_VIEW_NAME = "index"

ADMIN_HTML_TEMPLATE = "admin.template.html"
ADMIN_REL_URL = "admin"
ADMIN_VIEW_NAME = "admin"

USERS_HTML_TEMPLATE = "users.template.html"
USERS_REL_URL = "users"
USERS_VIEW_NAME = "users"

DEVICES_HTML_TEMPLATE = "devices.template.html"
DEVICES_REL_URL = "devices"
DEVICES_VIEW_NAME = "devices"

TOPOLOGY_HTML_TEMPLATE = "topology.template.html"
TOPOLOGY_REL_URL = "topology"
TOPOLOGY_VIEW_NAME = "topology"

ABOUT_HTML_TEMPLATE = "about.template.html"
ABOUT_REL_URL = "about"
ABOUT_VIEW_NAME = "about"

LOGIN_HTML_TEMPLATE = "login.template.html"

API_RELOAD_REL_URL = 'reload'

DEFAULT_CSS_NAME = 'default.css'
LOGIN_CSS_NAME = "login.css"

LOGO_LITTLE_BROTHER_NAME = 'icon-baby-panda-128x128.png'
ICON_FAVICON_NAME = 'baby-panda-32x32.ico'

TEMPLATE_REL_DIR = "templates"

FORM_ID_CSRF = 'csrf'

HTML_KEY_NEW_USER = "NewUser"
HTML_KEY_NEW_DEVICE = "NewDevice"

# Dummy function to trigger extraction by pybabel...
_ = lambda x: x

BLUEPRINT_NAME = "little_brother"

BLUEPRINT_ADAPTER = blueprint_adapter.BlueprintAdapter()


class StatusServerConfigModel(base_web_server.BaseWebServerConfigModel):

    def __init__(self):
        super().__init__(p_section_name=SECTION_NAME)

        self.initializr_rel_dir = 'contrib/initializr'
        self.js_cookie_rel_dir = 'contrib/js-cookie'

        self.datetime_format = "%d.%m.%y %H:%M"
        self.time_format = "%H:%M"
        self.date_format = "%a %d.%m.%Y"
        self.simple_date_format = "%d.%m.%Y"


class StatusServer(base_web_server.BaseWebServer):

    def __init__(self,
                 p_config,
                 p_package_name,
                 p_app_control,
                 p_master_connector,
                 p_persistence,
                 p_is_master,
                 p_locale_helper,
                 p_base_gettext=None,
                 p_languages=None,
                 p_user_handler=None):

        super(StatusServer, self).__init__(
            p_config=p_config,
            p_name="Web Server",
            p_package_name=p_package_name,
            p_user_handler=p_user_handler,
            p_login_view=self.login_view,
            p_logged_out_endpoint=BLUEPRINT_NAME + '.' + INDEX_VIEW_NAME)

        self._blueprint = None
        self._is_master = p_is_master
        self._appcontrol = p_app_control
        self._master_connector = p_master_connector
        self._persistence = p_persistence
        self._stat_dict = {}
        self._server_exception = None
        self._locale_helper = p_locale_helper
        self._languages = p_languages
        self._base_gettext = p_base_gettext
        self._langs = {}
        self._localedir = os.path.join(os.path.dirname(__file__), "translations")

        if self._languages is None:
            self._languages = {'en': "English"}

        if self._base_gettext is None:
            self._base_gettext = lambda text: text

        if self._is_master:
            self._blueprint = flask.Blueprint(BLUEPRINT_NAME, little_brother.__name__, static_folder="static")
            BLUEPRINT_ADAPTER.assign_view_handler_instance(p_blueprint=self._blueprint, p_view_handler_instance=self)
            BLUEPRINT_ADAPTER.check_view_methods()

            self._app.register_blueprint(blueprint=self._blueprint, url_prefix=self._config.base_url)

            self._api_view_handler = api_view_handler.ApiViewHandler(
                p_app=self._app, p_app_control=self._appcontrol, p_master_connector=self._master_connector)

        self._app.jinja_env.filters['datetime_to_string'] = self.format_datetime
        self._app.jinja_env.filters['time_to_string'] = self.format_time
        self._app.jinja_env.filters['date_to_string'] = self.format_date
        self._app.jinja_env.filters['simple_date_to_string'] = self.format_simple_date
        self._app.jinja_env.filters['seconds_to_string'] = self.format_seconds
        self._app.jinja_env.filters['boolean_to_string'] = self.format_boolean
        self._app.jinja_env.filters['format'] = self.format
        self._app.jinja_env.filters['format_babel_date'] = self.format_babel_date
        self._app.jinja_env.filters['format_text_array'] = self.format_text_array
        self._app.jinja_env.filters['invert'] = self.invert
        self._app.jinja_env.filters['_base'] = self._base_gettext

        self._babel = flask_babel.Babel(self._app)
        self._babel.localeselector(self._locale_helper.locale_selector)
        gettext.bindtextdomain("messages", "little_brother/translations")

        # entity_forms.RulesetForm.context_details.validators = (
        #     lambda form, field: self._appcontrol.validate_context_rule_handler_details(p_context_name=form.context.data,
        #                                                                                p_context_details=field.data))

    def invert(self, rel_font_size):

        return str(int(1.0 / float(rel_font_size) * 10000.0))

    def measure(self, p_hostname, p_service, p_duration):

        self._appcontrol.set_prometheus_http_requests_summary(p_hostname=p_hostname,
                                                              p_service=p_service,
                                                              p_duration=p_duration)

    def login_view(self):

        request = flask.request
        with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                               p_service=request.url_rule, p_duration=duration)):
            page = flask.render_template(
                LOGIN_HTML_TEMPLATE,
                rel_font_size=self.get_rel_font_size(),
                authentication=self.get_authenication_info(),
                navigation={
                    'current_view': ADMIN_VIEW_NAME},
            )
            return page

    def format_datetime(self, value):

        if value is None:
            return "-"

        else:
            return value.strftime(self._config.datetime_format)

    def format_simple_date(self, value):

        if value is None:
            return "-"

        else:
            return value.strftime(self._config.simple_date_format)

    def format_date(self, value):

        if value is None:
            return "-"

        else:
            return value.strftime(self._config.date_format)

    def format_time(self, value):

        if value is None:
            return "-"

        else:
            return value.strftime(self._config.time_format)

    @staticmethod
    def format_seconds(value):

        return tools.get_duration_as_string(p_seconds=value, p_include_seconds=False)

    @staticmethod
    def format_boolean(value):

        return tools.format_boolean(p_value=value)

    @staticmethod
    def format(value, param_dict):

        return value.format(**param_dict)

    def format_text_array(self, value):

        text = ""

        for part in value:
            if part == constants.TEXT_SEPERATOR:
                if text != "":
                    text += constants.TEXT_SEPERATOR

            else:
                text += self._base_gettext(self.gettext(part))

        return text

    def format_babel_date(self, value, format_string):

        return babel.dates.format_date(value, format_string, locale=self._locale_helper.locale)

    @BLUEPRINT_ADAPTER.route_method("/")
    def entry_view(self):

        return flask.redirect(flask.url_for("little_brother.index"))

    def save_admin_data(self, p_admin_infos, p_forms):

        for admin_info in p_admin_infos:
            for day_info in admin_info.day_infos:
                form = p_forms[day_info.html_key]

                if form.differs_from_model(p_model=day_info.override):
                    form.save_to_model(p_model=day_info.override)
                    self._appcontrol.update_rule_override(day_info.override)

    def save_users_data(self, p_users, p_forms):

        with persistence.SessionContext(p_persistence=self._persistence) as session_context:
            session = session_context.get_session()
            changed = False

            for user in p_users:
                form = p_forms[user.html_key]
                persistent_user = persistence.User.get_by_username(p_session=session, p_username=user.username)

                if persistent_user is not None and form.differs_from_model(p_model=persistent_user):
                    form.save_to_model(p_model=persistent_user)
                    changed = True

                for ruleset in user.rulesets:
                    form = p_forms[ruleset.html_key]
                    persistent_ruleset = persistence.RuleSet.get_by_id(p_session=session, p_id=ruleset.id)

                    if persistent_ruleset is not None and form.differs_from_model(p_model=persistent_ruleset):
                        form.save_to_model(p_model=persistent_ruleset)
                        changed = True

                for user2device in user.devices:
                    form = p_forms[user2device.html_key]
                    persistent_user2device = persistence.User2Device.get_by_id(p_session=session, p_id=user2device.id)

                    if persistent_user2device is not None and form.differs_from_model(p_model=persistent_user2device):
                        form.save_to_model(p_model=persistent_user2device)
                        changed = True

            if changed:
                session.commit()

                self._persistence.clear_cache()
                self._appcontrol.send_config_to_all_slaves()
                self._appcontrol.reset_users(p_session_context=session_context)

    def save_devices_data(self, p_devices, p_forms):

        with persistence.SessionContext(p_persistence=self._persistence) as session_context:
            session = session_context.get_session()
            changed = False

            for device in p_devices:
                form = p_forms[device.device_name]
                device = persistence.Device.get_by_device_name(p_session=session, p_device_name=device.device_name)

                if device is not None and form.differs_from_model(p_model=device):
                    form.save_to_model(p_model=device)
                    changed = True

            session.commit()
            session.close()

            if changed:
                self._persistence.clear_cache()


    @BLUEPRINT_ADAPTER.route_method("/admin", endpoint="admin", methods=["GET", "POST"])
    @flask_login.login_required
    def admin_view(self):

        request = flask.request
        with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                               p_service=request.url_rule, p_duration=duration)):
            with persistence.SessionContext(p_persistence=self._persistence) as session_context:

                admin_infos = self._appcontrol.get_admin_infos(p_session_context=session_context)
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
                    return flask.redirect(flask.url_for("little_brother.admin"))

                if not submitted:
                    for admin_info in admin_infos:
                        for day_info in admin_info.day_infos:
                            forms[day_info.html_key].load_from_model(p_model=day_info.override)

                return flask.render_template(
                    ADMIN_HTML_TEMPLATE,
                    rel_font_size=self.get_rel_font_size(),
                    admin_infos=admin_infos,
                    authentication=self.get_authenication_info(),
                    forms=forms,
                    navigation={
                        'current_view': ADMIN_VIEW_NAME},
                )

    @BLUEPRINT_ADAPTER.route_method("/topology", endpoint="topology")
    @flask_login.login_required
    def topology_view(self):

        request = flask.request
        with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                               p_service=request.url_rule, p_duration=duration)):
            with persistence.SessionContext(p_persistence=self._persistence) as session_context:

                topology_infos = self._appcontrol.get_topology_infos(p_session_context=session_context)
                return flask.render_template(
                    TOPOLOGY_HTML_TEMPLATE,
                    rel_font_size=self.get_rel_font_size(),
                    topology_infos=topology_infos,
                    app_control_config=self._appcontrol._config,
                    authentication=self.get_authenication_info(),
                    navigation={
                        'current_view': TOPOLOGY_VIEW_NAME},
                )

    @BLUEPRINT_ADAPTER.route_method("/users", endpoint="users", methods=["GET", "POST"])
    @flask_login.login_required
    def users_view(self):

        with persistence.SessionContext(p_persistence=self._persistence) as session_context:
            request = flask.request
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=request.url_rule, p_duration=duration)):

                users = self._appcontrol.get_sorted_users(session_context)
                forms = self.get_users_forms(p_users=users, p_session_context=session_context)

                valid_and_submitted = True
                submitted = False

                for form in forms.values():
                    if not form.validate_on_submit():
                        valid_and_submitted = False

                    if form.is_submitted():
                        submitted = True

                if valid_and_submitted:
                    self.save_users_data(users, forms)

                    if request.form['submit'] == HTML_KEY_NEW_USER:
                        username = forms[HTML_KEY_NEW_USER].username.data
                        self._appcontrol.add_new_user(p_session_context=session_context,
                                                      p_username=username, p_locale=self._locale_helper.locale)
                        # TODO: after adding new user Users window should be opened for new user

                    else:
                        for user in users:
                            if request.form['submit'] == user.delete_html_key:
                                self._persistence.delete_user(user.username)
                                self._appcontrol.send_config_to_all_slaves()

                            elif request.form['submit'] == user.new_ruleset_html_key:
                                self._persistence.add_ruleset(user.username)

                            elif request.form['submit'] == user.new_device_html_key:
                                device_id = int(forms[user.new_device_html_key].device_id.data)
                                self._persistence.add_device(p_device_id=device_id, p_username=user.username)

                            else:
                                for ruleset in user.rulesets:
                                    if request.form['submit'] == ruleset.delete_html_key:
                                        self._persistence.delete_ruleset(p_ruleset_id=ruleset.id)

                                    elif request.form['submit'] == ruleset.move_down_html_key:
                                        self._persistence.move_down_ruleset(p_ruleset_id=ruleset.id)

                                    elif request.form['submit'] == ruleset.move_up_html_key:
                                        self._persistence.move_up_ruleset(p_ruleset_id=ruleset.id)

                                for user2device in user.devices:
                                    if request.form['submit'] == user2device.delete_html_key:
                                        self._persistence.delete_user2device(p_user2device_id=user2device.id)

                    return flask.redirect(flask.url_for("little_brother.users"))

                if not submitted:
                    for user in users:
                        forms[user.html_key].load_from_model(p_model=user)

                        for ruleset in user.rulesets:
                            forms[ruleset.html_key].load_from_model(p_model=ruleset)
                            # provide a callback function so that the RuleSet can retrieve context summaries
                            ruleset.get_context_rule_handler = self._appcontrol.get_context_rule_handler

                        for user2device in user.devices:
                            forms[user2device.html_key].load_from_model(p_model=user2device)

                return flask.render_template(
                    USERS_HTML_TEMPLATE,
                    rel_font_size=self.get_rel_font_size(),
                    users=users,
                    authentication=self.get_authenication_info(),
                    forms=forms,
                    new_user_html_key=HTML_KEY_NEW_USER,
                    new_user_submit_value=HTML_KEY_NEW_USER,
                    navigation={
                        'current_view': USERS_VIEW_NAME
                    },
                )

    @BLUEPRINT_ADAPTER.route_method("/devices", endpoint="devices", methods=["GET", "POST"])
    @flask_login.login_required
    def devices_view(self):

        with persistence.SessionContext(p_persistence=self._persistence) as session_context:
            request = flask.request
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=request.url_rule, p_duration=duration)):

                devices = self._appcontrol.get_sorted_devices(session_context)
                forms = self.get_devices_forms(p_devices=devices)

                valid_and_submitted = True
                submitted = False

                for form in forms.values():
                    if not form.validate_on_submit():
                        valid_and_submitted = False

                    if form.is_submitted():
                        submitted = True

                if valid_and_submitted:
                    self.save_devices_data(devices, forms)

                    if request.form['submit'] == HTML_KEY_NEW_DEVICE:
                        self._persistence.add_new_device(p_session_context=session_context,
                                                         p_name_pattern=self.gettext("New device {id}"))
                        # TODO: after adding new device Devices window should be opened for new device
                    else:
                        for device in devices:
                            if request.form['submit'] == device.delete_html_key:
                                self._persistence.delete_device(device.id)

                    return flask.redirect(flask.url_for("little_brother.devices"))

                if not submitted:
                    for device in devices:
                        forms[device.device_name].load_from_model(p_model=device)

                return flask.render_template(
                    DEVICES_HTML_TEMPLATE,
                    rel_font_size=self.get_rel_font_size(),
                    devices=devices,
                    authentication=self.get_authenication_info(),
                    forms=forms,
                    new_device_html_key=HTML_KEY_NEW_DEVICE,
                    new_device_submit_value=HTML_KEY_NEW_DEVICE,
                    navigation={
                        'current_view': DEVICES_VIEW_NAME
                    },
                )

    def get_rel_font_size(self):

        rel_font_size = LOCALE_REL_FONT_SIZES.get(self._locale_helper.locale)
        if not rel_font_size:
            rel_font_size = 100
        return rel_font_size

    def has_downtime_today(self, p_user_infos):

        for user_info in p_user_infos.values():
            if user_info['active_stat_info'].todays_downtime:
                return True

        return False

    @BLUEPRINT_ADAPTER.route_method("/status", endpoint="index")
    def index_view(self):

        request = flask.request
        with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                               p_service=request.url_rule, p_duration=duration)):
            with persistence.SessionContext(p_persistence=self._persistence) as session_context:
                user_infos = self._appcontrol.get_user_status_infos(p_session_context=session_context)
                page = flask.render_template(
                    INDEX_HTML_TEMPLATE,
                    rel_font_size=self.get_rel_font_size(),
                    user_infos=user_infos,
                    has_downtime_today=self.has_downtime_today(p_user_infos=user_infos),
                    app_control_config=self._appcontrol._config,
                    authentication=self.get_authenication_info(),
                    navigation={
                        'current_view': INDEX_VIEW_NAME},
                )

        return page

    @BLUEPRINT_ADAPTER.route_method("/about", endpoint="about")
    def about_view(self):

        with persistence.SessionContext(p_persistence=self._persistence) as session_context:
            request = flask.request
            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=request.url_rule, p_duration=duration)):
                page = flask.render_template(
                    ABOUT_HTML_TEMPLATE,
                    rel_font_size=self.get_rel_font_size(),
                    user_infos=self._appcontrol.get_user_status_infos(session_context),
                    settings=settings.settings,
                    extended_settings=settings.extended_settings,
                    git_metadata=git.git_metadata,
                    authentication=self.get_authenication_info(),
                    languages=sorted([(a_locale, a_language) for a_locale, a_language in self._languages.items()]),
                    navigation={
                        'current_view': ABOUT_VIEW_NAME}

                )
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

    def add_labels(self, p_value_list):

        return [(entry, self.gettext(entry)) for entry in p_value_list]

    def get_users_forms(self, p_session_context, p_users):

        forms = {}
        forms[FORM_ID_CSRF] = flask_wtf.FlaskForm(meta={'csrf': False})

        unmonitored_users = self._appcontrol.get_unmonitored_users(p_session_context)

        if len(unmonitored_users) > 0:
            new_user_form = entity_forms.NewUserForm(meta={'csrf': False})
            new_user_form.username.choices = [(username, username) for username in unmonitored_users]
            forms[HTML_KEY_NEW_USER] = new_user_form

        for user in p_users:
            form = entity_forms.UserForm(prefix='{id}_'.format(id=user.html_key), meta={'csrf': False})
            form.locale.choices = sorted([(locale, language) for locale, language in self._languages.items()])
            forms[user.html_key] = form

            for ruleset in user.rulesets:
                localized_values = [(value, self.gettext(value))
                                    for value in self._appcontrol.get_context_rule_handler_choices()]

                if ruleset.fixed_context:
                    choices = self.add_labels([ruleset.context])

                else:
                    choices = self.add_labels(self._appcontrol.get_context_rule_handler_names())

                context_details_filters = [
                    lambda x: custom_fields.unlocalize(p_localized_values=localized_values, p_value=x)]

                form = entity_forms.create_rulesets_form(p_context_choices=choices,
                                                         p_localized_context_details=localized_values,
                                                         p_context_details_filters=context_details_filters,
                                                         prefix='{id}_'.format(id=ruleset.html_key))
                forms[ruleset.html_key] = form

                form.context_details.validators = [
                    lambda form, field: self._appcontrol.validate_context_rule_handler_details(
                        p_context_name=form.context.data, p_context_details=field.data)]

            unmonitored_devices = self._appcontrol.get_unmonitored_devices(p_user=user,
                                                                           p_session_context=p_session_context)

            if len(unmonitored_devices) > 0:
                new_device_form = entity_forms.NewUser2DeviceForm(prefix='{id}_'.format(id=user.html_key),
                                                                  meta={'csrf': False})
                new_device_form.device_id.choices = [(str(device.id), device.device_name) for device in
                                                     unmonitored_devices]
                forms[user.new_device_html_key] = new_device_form

            for user2device in user.devices:
                form = entity_forms.User2DeviceForm(prefix='{id}_'.format(id=user2device.html_key),
                                                    meta={'csrf': False})
                forms[user2device.html_key] = form

        return forms

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

    def destroy(self):

        BLUEPRINT_ADAPTER.unassign_view_handler_instances()
        super().destroy()

    def gettext(self, p_text):

        return self._locale_helper.gettext(p_text=p_text)
