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

from little_brother import dependency_injection
from little_brother.persistence.persistence import Persistence
from little_brother.persistence.persistent_admin_event_entity_manager import AdminEventEntityManager
from little_brother.persistence.persistent_daily_user_status_entity_manager import DailyUserStatusEntityManager
from little_brother.persistence.persistent_device_entity_manager import DeviceEntityManager
from little_brother.persistence.persistent_process_info_entity_manager import ProcessInfoEntityManager
from little_brother.persistence.persistent_rule_override_entity_manager import RuleOverrideEntityManager
from little_brother.persistence.persistent_rule_set_entity_manager import RuleSetEntityManager
from little_brother.persistence.persistent_time_extension_entity_manager import TimeExtensionEntityManager
from little_brother.persistence.persistent_user_2_device_entity_manager import User2DeviceEntityManager
from little_brother.persistence.persistent_user_entity_manager import UserEntityManager


class PersistenceDependencyInjectionMixIn:

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Dependency injection
        self._persistence = None
        self._device_entity_manager = None
        self._user_entity_manager = None
        self._process_info_entity_manager = None
        self._admin_event_entity_manager = None
        self._rule_set_entity_manager = None
        self._rule_override_entity_manager = None
        self._device_entity_manager = None
        self._user_2_device_entity_manager = None
        self._time_extension_entity_manager = None
        self._user_status_entity_manager = None

    @property
    def persistence(self):

        if self._persistence is None:
            self._persistence = dependency_injection.container[Persistence]

        return self._persistence

    @property
    def time_extension_entity_manager(self) -> TimeExtensionEntityManager:

        if self._time_extension_entity_manager is None:
            self._time_extension_entity_manager = dependency_injection.container[TimeExtensionEntityManager]

        return self._time_extension_entity_manager

    @property
    def user_entity_manager(self) -> UserEntityManager:

        if self._user_entity_manager is None:
            self._user_entity_manager = dependency_injection.container[UserEntityManager]
        return self._user_entity_manager

    @property
    def device_entity_manager(self) -> DeviceEntityManager:

        if self._device_entity_manager is None:
            self._device_entity_manager = dependency_injection.container[DeviceEntityManager]

        return self._device_entity_manager

    @property
    def process_info_entity_manager(self) -> ProcessInfoEntityManager:

        if self._process_info_entity_manager is None:
            self._process_info_entity_manager = dependency_injection.container[ProcessInfoEntityManager]

        return self._process_info_entity_manager

    @property
    def admin_event_entity_manager(self) -> AdminEventEntityManager:

        if self._admin_event_entity_manager is None:
            self._admin_event_entity_manager = dependency_injection.container[AdminEventEntityManager]

        return self._admin_event_entity_manager

    @property
    def rule_set_entity_manager(self) -> RuleSetEntityManager:

        if self._rule_set_entity_manager is None:
            self._rule_set_entity_manager = dependency_injection.container[RuleSetEntityManager]

        return self._rule_set_entity_manager

    @property
    def rule_override_entity_manager(self) -> RuleOverrideEntityManager:

        if self._rule_override_entity_manager is None:
            self._rule_override_entity_manager = dependency_injection.container[RuleOverrideEntityManager]

        return self._rule_override_entity_manager

    @property
    def user_2_device_entity_manager(self) -> User2DeviceEntityManager:

        if self._user_2_device_entity_manager is None:
            self._user_2_device_entity_manager = dependency_injection.container[User2DeviceEntityManager]

        return self._user_2_device_entity_manager

    @property
    def daily_user_status_entity_manager(self) -> DailyUserStatusEntityManager:

        if self._user_status_entity_manager is None:
            self._user_status_entity_manager = dependency_injection.container[DailyUserStatusEntityManager]

        return self._user_status_entity_manager
