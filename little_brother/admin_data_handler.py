# -*- coding: utf-8 -*-

# Copyright (C) 2019-2021  Marcus Rickert
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

import datetime

from little_brother import dependency_injection
from little_brother import process_statistics
from little_brother import rule_override
from little_brother import rule_result_info
from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn
from little_brother.persistence.persistent_user import User
from little_brother.persistence.session_context import SessionContext
from little_brother.rule_handler import RuleHandler
from little_brother.user_locale_handler import UserLocaleHandler
from python_base_app import log_handling
from python_base_app import tools
from python_base_app import view_info
from python_base_app.view_info import ViewInfo


def _(text, _mode=None):
    return text


class AdminDataHandler(PersistenceDependencyInjectionMixIn):

    def __init__(self, p_config):

        super().__init__()

        self._config = p_config

        self._logger = log_handling.get_logger(self.__class__.__name__)

        self._rule_handler = None
        self._user_locale_handler = UserLocaleHandler()
        self._rule_overrides = {}

        self.history_labels = [(_('{days} days ago'), {"days": day}) for day in
                               range(0, self._config.process_lookback_in_days + 1)]

        self.history_labels[0] = (_('Today'), {"days": 0})
        self.history_labels[1] = (_('Yesterday'), {"days": 1})

    @property
    def rule_overrides(self):
        return self._rule_overrides

    @property
    def rule_handler(self) -> RuleHandler:

        if self._rule_handler is None:
            self._rule_handler = dependency_injection.container[RuleHandler]

        return self._rule_handler

    @property
    def user_locale_handler(self) -> UserLocaleHandler:

        if self._user_locale_handler is None:
            self._user_locale_handler = dependency_injection.container[UserLocaleHandler]

        return self._user_locale_handler

    def get_admin_info(self, p_session_context, p_user_name, p_process_infos) -> ViewInfo:

        admin_infos = self.get_admin_infos(
            p_session_context=p_session_context,
            p_process_infos=p_process_infos,
            p_user_names=[p_user_name])

        if len(admin_infos) == 0:
            return None

        return admin_infos[0]

    def get_day_info_for_user(self, p_admin_info, p_username: str,
                              p_reference_date: datetime.datetime, p_rule_set) -> view_info.ViewInfo:

        if p_rule_set is not None:
            key_rule_override = rule_override.get_key(p_username=p_username,
                                                      p_reference_date=p_reference_date)
            override = self._rule_overrides.get(key_rule_override)

            if override is None:
                override = rule_override.RuleOverride(p_reference_date=p_reference_date,
                                                      p_username=p_username)

            effective_rule_set = rule_result_info.apply_override(p_rule_set=p_rule_set,
                                                                 p_rule_override=override)

            day_info = view_info.ViewInfo(p_parent=p_admin_info,
                                          p_html_key=tools.get_simple_date_as_string(
                                              p_date=p_reference_date))

            if p_reference_date == datetime.date.today():
                day_info.long_format = _("'Today ('EEE')'", 'long')
                day_info.short_format = _("'Today'", 'short')

            elif p_reference_date == datetime.date.today() + datetime.timedelta(days=1):
                day_info.long_format = _("'Tomorrow ('EEE')'", 'long')
                day_info.short_format = _("'Tomorrow'", 'short')

            else:
                day_info.long_format = _("yyyy-MM-dd' ('EEE')'")
                day_info.short_format = _("EEE")

            day_info.reference_date = p_reference_date
            day_info.rule_set = p_rule_set
            day_info.override = override
            day_info.effective_rule_set = effective_rule_set
            day_info.max_lookahead_in_days = self._config.admin_lookahead_in_days

            return day_info

    def get_admin_info_for_user(self, p_session_context, p_user_infos, p_time_extensions, p_days, p_username):

        user : User = self.user_entity_manager.user_map(p_session_context).get(p_username)

        if user is None or not user.active:
            return None

        admin_info = view_info.ViewInfo(p_html_key=p_username)
        admin_info.full_name = user.full_name
        admin_info.username = p_username
        admin_info.full_name = p_username

        admin_info.time_extension = p_time_extensions.get(p_username)
        admin_info.time_extension_periods = []

        if admin_info.time_extension is not None:
            # add special value 0 for "off"
            admin_info.time_extension_periods.append(0)

        for period in self._config.time_extension_periods_list:
            if period > 0:
                admin_info.time_extension_periods.append(period)

            else:
                if admin_info.time_extension is not None and \
                        admin_info.time_extension.end_datetime + \
                        datetime.timedelta(minutes=period) >= admin_info.time_extension.start_datetime:
                    admin_info.time_extension_periods.append(period)


        admin_info.day_infos = []

        admin_info.user_info = p_user_infos.get(p_username)

        if admin_info.user_info is not None:
            for reference_date in sorted(p_days):
                rule_set = self.rule_handler.get_active_ruleset(
                    p_rule_sets=user.rulesets, p_reference_date=reference_date)

                day_info = self.get_day_info_for_user(p_admin_info=admin_info, p_username=p_username,
                                                      p_reference_date=reference_date, p_rule_set=rule_set)

                admin_info.day_infos.append(day_info)

        return admin_info

    def get_admin_infos(self, p_session_context, p_user_names, p_process_infos):

        admin_infos = []

        user_infos = self.get_user_status_infos(p_session_context=p_session_context, p_include_history=False,
                                                p_process_infos=p_process_infos)
        time_extensions = self.time_extension_entity_manager.get_active_time_extensions(
            p_session_context=p_session_context, p_reference_datetime=tools.get_current_time())

        days = [datetime.date.today() + datetime.timedelta(days=i) for i in
                range(0, self._config.admin_lookahead_in_days + 1)]

        for override in self._rule_overrides.values():
            if override.reference_date not in days and override.reference_date >= datetime.date.today():
                days.append(override.reference_date)

        for username in p_user_names:
            admin_info = self.get_admin_info_for_user(p_session_context=p_session_context, p_user_infos=user_infos,
                                                      p_days=days, p_time_extensions=time_extensions,
                                                      p_username=username)

            if admin_info is not None:
                admin_infos.append(admin_info)

        return sorted(admin_infos, key=lambda info: info.full_name)

    def update_rule_override(self, p_rule_override):

        fmt = "Updating '{override}'"
        self._logger.debug(fmt.format(override=str(p_rule_override)))

        self._rule_overrides[p_rule_override.get_key()] = p_rule_override

        with SessionContext(p_persistence=self.persistence) as session_context:
            self.rule_override_entity_manager.update_rule_override(
                p_session_context=session_context, p_rule_override=p_rule_override)

    def get_user_info_for_user(self, p_session_context, p_user, p_reference_time,
                               p_users_stat_infos, p_active_time_extensions):

        user_info = None

        rule_set = self.rule_handler.get_active_ruleset(
            p_rule_sets=p_user.rulesets, p_reference_date=p_reference_time.date())
        stat_infos = p_users_stat_infos.get(p_user.username)
        active_time_extension = p_active_time_extensions.get(p_user.username)
        user_locale = self.user_locale_handler.get_user_locale(
            p_session_context=p_session_context, p_username=p_user.username)

        if stat_infos is not None:
            stat_info = stat_infos.get(rule_set.context)

            if stat_info is not None:
                self._logger.debug(str(stat_info))

                key_rule_override = rule_override.get_key(p_username=p_user.username,
                                                          p_reference_date=p_reference_time.date())
                override = self._rule_overrides.get(key_rule_override)

                rule_result_info = self.rule_handler.process_rule_sets_for_user(
                    p_rule_sets=p_user.rulesets,
                    p_stat_info=stat_info,
                    p_active_time_extension=active_time_extension,
                    p_reference_time=p_reference_time,
                    p_rule_override=override,
                    p_locale=user_locale)

                activity_permitted = rule_result_info.activity_allowed()

                user_info = {
                    'username': p_user.username,
                    'full_name': p_user.full_name,
                    'active_rule_set': rule_set,
                    'active_stat_info': stat_info,
                    'active_rule_result_info': rule_result_info,
                    'max_lookback_in_days': self._config.process_lookback_in_days,
                    'activity_permitted': activity_permitted,
                    'history_labels': self.history_labels
                }

        return user_info

    def get_user_status_infos(self, p_session_context, p_process_infos, p_include_history=True):

        user_infos = {}

        reference_time = datetime.datetime.now()

        active_time_extensions = self.time_extension_entity_manager.get_active_time_extensions(
            p_session_context=p_session_context, p_reference_datetime=reference_time)

        users_stat_infos = process_statistics.get_process_statistics(
            p_process_infos=p_process_infos,
            p_reference_time=reference_time,
            p_user_map=self.user_entity_manager.user_map(p_session_context),
            p_max_lookback_in_days=self._config.process_lookback_in_days if p_include_history else 1,
            p_min_activity_duration=self._config.min_activity_duration)

        for username in self.user_entity_manager.user_map(p_session_context).keys():
            user: User = self.user_entity_manager.user_map(p_session_context).get(username)

            if user is not None:
                user_info = self.get_user_info_for_user(p_session_context=p_session_context, p_user=user,
                                                        p_users_stat_infos=users_stat_infos,
                                                        p_active_time_extensions=active_time_extensions,
                                                        p_reference_time=reference_time)

                if user_info is not None:
                    user_infos[username] = user_info

        return user_infos

    def load_rule_overrides(self):

        with SessionContext(p_persistence=self.persistence) as session_context:
            overrides = self.rule_override_entity_manager.load_rule_overrides(
                p_session_context=session_context, p_lookback_in_days=self._config.process_lookback_in_days + 1)

        for override in overrides:
            new_override = rule_override.RuleOverride(
                p_username=override.username,
                p_reference_date=override.reference_date,
                p_max_time_per_day=override.max_time_per_day,
                p_min_time_of_day=override.min_time_of_day,
                p_max_time_of_day=override.max_time_of_day,
                p_min_break=override.min_break,
                p_max_activity_duration=override.max_activity_duration,
                p_free_play=override.free_play)

            self._rule_overrides[new_override.get_key()] = new_override

        fmt = "Loaded %d rule overrides from database looking back %s days" % (
            len(overrides), self._config.process_lookback_in_days)
        self._logger.info(fmt)

    def get_current_rule_result_info(self, p_reference_time, p_process_infos, p_username):

        rule_result_info = None

        with SessionContext(p_persistence=self.persistence) as session_context:
            users_stat_infos = process_statistics.get_process_statistics(
                p_process_infos=p_process_infos,
                p_reference_time=p_reference_time,
                p_max_lookback_in_days=1,
                p_user_map=self.user_entity_manager.user_map(session_context),
                p_min_activity_duration=self._config.min_activity_duration)

            active_time_extensions = self.time_extension_entity_manager.get_active_time_extensions(
                p_session_context=session_context, p_reference_datetime=tools.get_current_time())

            user_locale = self._user_locale_handler.get_user_locale(p_session_context=session_context,
                                                                    p_username=p_username)
            user: User = self.user_entity_manager.user_map(p_session_context=session_context).get(p_username)

            if user is not None:
                rule_set = self.rule_handler.get_active_ruleset(p_rule_sets=user.rulesets,
                                                                p_reference_date=p_reference_time.date())

                stat_infos = users_stat_infos.get(p_username)
                active_time_extension = active_time_extensions.get(p_username)

                if stat_infos is not None:
                    stat_info = stat_infos.get(rule_set.context)

                    if stat_info is not None:
                        self._logger.debug(str(stat_info))

                        key_rule_override = rule_override.get_key(p_username=p_username,
                                                                  p_reference_date=p_reference_time.date())
                        override = self._rule_overrides.get(key_rule_override)

                        rule_result_info = self.rule_handler.process_rule_sets_for_user(
                            p_rule_sets=user.rulesets,
                            p_stat_info=stat_info,
                            p_reference_time=p_reference_time,
                            p_active_time_extension=active_time_extension,
                            p_rule_override=override,
                            p_locale=user_locale)

        return rule_result_info
