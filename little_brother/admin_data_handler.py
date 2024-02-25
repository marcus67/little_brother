# -*- coding: utf-8 -*-

# Copyright (C) 2019-2024  Marcus Rickert
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
from little_brother.persistence.persistent_rule_set import RuleSet
from little_brother.persistence.persistent_time_extension import TimeExtension
from little_brother.persistence.persistent_user import User
from little_brother.persistence.session_context import SessionContext
from little_brother.process_statistics import DayStatistics
from little_brother.rule_handler import RuleHandler
from little_brother.transport.control_to import ControlTO
from little_brother.transport.rule_set_to import RuleSetTO
from little_brother.transport.user_admin_detail_to import UserAdminDetailTO
from little_brother.transport.user_admin_to import UserAdminTO
from little_brother.transport.user_status_detail_to import UserStatusDetailTO
from little_brother.transport.user_status_to import UserStatusTO
from little_brother.user_locale_handler import UserLocaleHandler
from python_base_app import log_handling
from python_base_app import tools
from python_base_app import view_info
from python_base_app.tools import get_datetime_in_iso_8601
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

        user: User = self.user_entity_manager.user_map(p_session_context).get(p_username)

        if user is None or not user.active:
            return None

        admin_info = view_info.ViewInfo(p_html_key=p_username)
        admin_info.full_name = user.full_name
        admin_info.username = p_username

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

    def get_user_status_transfer_object(self, p_session_context, p_user, p_reference_time,
                                        p_users_stat_infos, p_active_time_extensions,
                                        p_include_details: bool) -> UserStatusTO:

        user_status_to: UserStatusTO | None = None

        rule_set: RuleSet = self.rule_handler.get_active_ruleset(
            p_rule_sets=p_user.rulesets, p_reference_date=p_reference_time.date())
        stat_infos = p_users_stat_infos.get(p_user.username)
        active_time_extension = p_active_time_extensions.get(p_user.username)
        user_locale = self.user_locale_handler.get_user_locale(
            p_session_context=p_session_context, p_username=p_user.username)

        if stat_infos is not None:
            stat_info: process_statistics.ProcessStatisticsInfo = stat_infos.get(rule_set.context)

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

                user_status_details: list[UserStatusDetailTO] | None = None

                if p_include_details:
                    user_status_details = []

                    for i in range(0, stat_info.max_lookback_in_days):
                        user_status_activity_details: list[UserStatusDetailTO] = []

                        for activity in stat_info.day_statistics[i].activities:
                            user_status_activity: UserStatusDetailTO = UserStatusDetailTO(
                                p_history_label=None,
                                p_duration_in_seconds=int(activity.duration) if activity.duration else None,
                                p_downtime_in_seconds=int(activity.downtime) if activity.downtime else None,
                                p_min_time_in_iso_8601=get_datetime_in_iso_8601(activity.start_time),
                                p_max_time_in_iso_8601=get_datetime_in_iso_8601(activity.end_time),
                                p_host_infos=activity.host_infos)
                            user_status_activity_details.append(user_status_activity)

                        day_info: DayStatistics = stat_info.day_statistics[i]

                        user_status_day_detail: UserStatusDetailTO = UserStatusDetailTO(
                            p_history_label=self.history_labels[i][0].format(**self.history_labels[i][1]),
                            p_duration_in_seconds=day_info.duration,
                            p_downtime_in_seconds=day_info.downtime,
                            p_min_time_in_iso_8601=day_info.min_time_in_iso_8601,
                            p_max_time_in_iso_8601=day_info.max_time_in_iso_8601,
                            p_host_infos=day_info.host_infos,
                            p_user_status_details=user_status_activity_details)

                        user_status_details.append(user_status_day_detail)

                user_status_to = UserStatusTO(
                    p_user_id=p_user.id,
                    p_username=p_user.username,
                    p_full_name=stat_info.full_name,
                    p_free_play=rule_set.free_play,
                    p_activity_permitted=rule_result_info.activity_allowed(),
                    p_context_label=rule_set.label,
                    p_todays_activity_duration_in_seconds=int(stat_info.todays_activity_duration)
                    if stat_info.todays_activity_duration else None,
                    p_todays_downtime_in_seconds=int(stat_info.todays_downtime) if stat_info.todays_downtime else None,
                    p_max_time_per_day_in_seconds=rule_set.max_time_per_day,
                    p_current_activity_duration_in_seconds=
                    int(stat_info.current_activity_duration) if stat_info.current_activity_duration else None,
                    p_current_activity_start_time_in_iso_8601=stat_info.current_activity_start_time_in_iso_8601,
                    p_current_activity_downtime_in_seconds=int(stat_info.current_activity_downtime)
                    if stat_info.current_activity_downtime else None,
                    p_previous_activity_start_time_in_iso_8601=stat_info.previous_activity_start_time_in_iso_8601,
                    p_previous_activity_end_time_in_iso_8601=stat_info.previous_activity_end_time_in_iso_8601,
                    p_reasons=[template.format(**value_dict)
                               for template, value_dict in rule_result_info.applying_rule_text_templates],
                    p_user_status_details=user_status_details
                )

        return user_status_to

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

    def get_control_transfer_object(self) -> ControlTO:
        return ControlTO(p_refresh_interval_in_milliseconds=self._config.index_refresh_interval * 1000)

    def get_user_status_transfer_objects(self, p_session_context, p_process_infos) -> dict[str, UserStatusTO]:

        user_status_tos = {}

        reference_time = datetime.datetime.now()

        active_time_extensions = self.time_extension_entity_manager.get_active_time_extensions(
            p_session_context=p_session_context, p_reference_datetime=reference_time)

        users_stat_infos = process_statistics.get_process_statistics(
            p_process_infos=p_process_infos,
            p_reference_time=reference_time,
            p_user_map=self.user_entity_manager.user_map(p_session_context),
            p_max_lookback_in_days=1,
            p_min_activity_duration=self._config.min_activity_duration)

        for username in self.user_entity_manager.user_map(p_session_context).keys():
            user: User = self.user_entity_manager.user_map(p_session_context).get(username)

            if user is not None:
                user_status_to = self.get_user_status_transfer_object(
                    p_session_context=p_session_context, p_user=user, p_users_stat_infos=users_stat_infos,
                    p_active_time_extensions=active_time_extensions, p_reference_time=reference_time,
                    p_include_details=False)

                if user_status_to is not None:
                    user_status_tos[user.username] = user_status_to

        return user_status_tos

    def get_user_status_and_details_transfer_object(self, p_user_id: int, p_session_context,
                                                    p_process_infos) -> UserStatusTO | None:

        reference_time = datetime.datetime.now()

        active_time_extensions = self.time_extension_entity_manager.get_active_time_extensions(
            p_session_context=p_session_context, p_reference_datetime=reference_time)

        users_stat_infos = process_statistics.get_process_statistics(
            p_process_infos=p_process_infos,
            p_reference_time=reference_time,
            p_user_map=self.user_entity_manager.user_map(p_session_context),
            p_max_lookback_in_days=self._config.process_lookback_in_days,
            p_min_activity_duration=self._config.min_activity_duration)

        user: User = self.user_entity_manager.get_by_id(p_session_context=p_session_context, p_id=p_user_id)

        if user is None:
            return None

        return self.get_user_status_transfer_object(
            p_session_context=p_session_context, p_user=user, p_users_stat_infos=users_stat_infos,
            p_active_time_extensions=active_time_extensions, p_reference_time=reference_time,
            p_include_details=True)

    def get_user_admin_transfer_objects(self, p_session_context, p_process_infos) -> list[UserAdminTO]:

        user_admin_tos: list[UserAdminTO] = []

        reference_time = datetime.datetime.now()

        user_status_tos = self.get_user_status_transfer_objects(p_session_context=p_session_context,
                                                                p_process_infos=p_process_infos)

        user_infos = self.get_user_status_infos(p_session_context=p_session_context, p_include_history=False,
                                                p_process_infos=p_process_infos)

        active_time_extensions = self.time_extension_entity_manager.get_active_time_extensions(
            p_session_context=p_session_context, p_reference_datetime=reference_time)

        for user in self.user_entity_manager.user_map(p_session_context).values():
            if user.active:
                user_admin_to = self.get_user_admin_transfer_object(
                    p_session_context=p_session_context, p_user_infos=user_infos,
                    p_time_extensions=active_time_extensions,
                    p_user_status_tos=user_status_tos,
                    p_username=user.username)
                user_admin_tos.append(user_admin_to)

        return user_admin_tos

    def get_user_admin_transfer_object(self, p_session_context, p_user_infos, p_time_extensions,
                                       p_username, p_user_status_tos,
                                       p_days=None) -> UserAdminTO | None:

        user_info = p_user_infos.get(p_username)

        if user_info is None:
            return None

        user_status_to = p_user_status_tos.get(p_username)

        if user_status_to is None:
            return None

        user: User = self.user_entity_manager.user_map(p_session_context).get(p_username)

        if user is None or not user.active:
            return None

        time_extension : TimeExtension = p_time_extensions.get(p_username)
        time_extension_periods = []

        if time_extension is not None:
            # add special value 0 for "off"
            time_extension_periods.append(0)

        for period in self._config.time_extension_periods_list:
            if period > 0:
                time_extension_periods.append(period)

            else:
                if time_extension is not None and \
                        time_extension.end_datetime + \
                        datetime.timedelta(minutes=period) >= time_extension.start_datetime:
                    time_extension_periods.append(period)

        user_admin_details_tos = []

        if p_days:
            for reference_date in sorted(p_days):
                rule_set = self.rule_handler.get_active_ruleset(
                    p_rule_sets=user.rulesets, p_reference_date=reference_date)

                if rule_set is not None:
                    key_rule_override = rule_override.get_key(p_username=p_username,
                                                              p_reference_date=reference_date)
                    override = self._rule_overrides.get(key_rule_override)

                    if override is None:
                        override = rule_override.RuleOverride(p_reference_date=reference_date,
                                                              p_username=p_username)

                    effective_rule_set = rule_result_info.apply_override(p_rule_set=rule_set,
                                                                         p_rule_override=override)

                    if reference_date == datetime.date.today():
                        long_format = _("'Today ('EEE')'", 'long')
                        short_format = _("'Today'", 'short')

                    elif reference_date == datetime.date.today() + datetime.timedelta(days=1):
                        long_format = _("'Tomorrow ('EEE')'", 'long')
                        short_format = _("'Tomorrow'", 'short')

                    else:
                        long_format = _("yyyy-MM-dd' ('EEE')'")
                        short_format = _("EEE")

                    user_admin_detail_to = UserAdminDetailTO(
                        p_long_format=long_format,
                        p_short_format=short_format,
                        p_date_in_iso_8601=tools.get_datetime_in_iso_8601(reference_date),
                        p_rule_set=RuleSetTO(
                            p_label=rule_set.context_label,
                            p_free_play=rule_set.free_play,
                            p_max_time_of_day_in_iso_8601=tools.get_datetime_in_iso_8601(rule_set.max_time_of_day),
                            p_min_time_of_day_in_iso_8601=tools.get_datetime_in_iso_8601(rule_set.min_time_of_day),
                            p_min_break_in_seconds=rule_set.min_break,
                            p_max_time_per_day_in_seconds=rule_set.max_time_per_day,
                            p_max_activity_duration_in_seconds=rule_set.max_activity_duration
                        ),
                        p_override=RuleSetTO(
                            p_free_play=override.free_play,
                            p_max_time_of_day_in_iso_8601=tools.get_datetime_in_iso_8601(override.max_time_of_day),
                            p_min_time_of_day_in_iso_8601=tools.get_datetime_in_iso_8601(override.min_time_of_day),
                            p_min_break_in_seconds=override.min_break,
                            p_max_time_per_day_in_seconds=override.max_time_per_day,
                            p_max_activity_duration_in_seconds=override.max_activity_duration
                        ),
                        p_effective_rule_set=RuleSetTO(
                            p_free_play=effective_rule_set.free_play,
                            p_max_time_of_day_in_iso_8601=tools.get_datetime_in_iso_8601(effective_rule_set.max_time_of_day),
                            p_min_time_of_day_in_iso_8601=tools.get_datetime_in_iso_8601(effective_rule_set.min_time_of_day),
                            p_min_break_in_seconds=effective_rule_set.min_break,
                            p_max_time_per_day_in_seconds=effective_rule_set.max_time_per_day,
                            p_max_activity_duration_in_seconds=effective_rule_set.max_activity_duration
                        ))

                    user_admin_details_tos.append(user_admin_detail_to)

        return UserAdminTO(p_username=p_username,
                           p_user_status=user_status_to,
                           p_time_extension_periods=time_extension_periods,
                           p_max_lookahead_in_days=self._config.admin_lookahead_in_days,
                           p_user_admin_details=user_admin_details_tos)

    def get_admin_status_and_details_transfer_object(self, p_user_id: int, p_session_context,
                                                     p_process_infos) -> UserStatusTO | None:

        reference_time = datetime.datetime.now()

        days = [datetime.date.today() + datetime.timedelta(days=i) for i in
                range(0, self._config.admin_lookahead_in_days + 1)]

        for override in self._rule_overrides.values():
            if override.reference_date not in days and override.reference_date >= datetime.date.today():
                days.append(override.reference_date)

        active_time_extensions = self.time_extension_entity_manager.get_active_time_extensions(
            p_session_context=p_session_context, p_reference_datetime=reference_time)

        users_stat_infos = process_statistics.get_process_statistics(
            p_process_infos=p_process_infos,
            p_reference_time=reference_time,
            p_user_map=self.user_entity_manager.user_map(p_session_context),
            p_max_lookback_in_days=self._config.process_lookback_in_days,
            p_min_activity_duration=self._config.min_activity_duration)

        user: User = self.user_entity_manager.get_by_id(p_session_context=p_session_context, p_id=p_user_id)

        if user is None:
            return None

        user_status_tos = self.get_user_status_transfer_objects(p_session_context=p_session_context,
                                                                p_process_infos=p_process_infos)

        return self.get_user_admin_transfer_object(
            p_session_context=p_session_context, p_username=user.username,
            p_time_extensions=active_time_extensions,
            p_user_status_tos=user_status_tos,
            p_user_infos=users_stat_infos,
            p_days=days)

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
