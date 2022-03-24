# -*- coding: utf-8 -*-

# Copyright (C) 2019-2022  Marcus Rickert
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

from typing import Optional

from little_brother import dependency_injection
from little_brother.devices.base_device_activation_handler import BaseDeviceActivationHandler
from little_brother.devices.device_activation_manager_config_model import DeviceActivationManagerConfigModel
from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn
from little_brother.persistence.persistent_device import Device
from little_brother.persistence.session_context import SessionContext
from little_brother.user_manager import UserManager
from python_base_app import log_handling
from python_base_app.base_app import RecurringTask


class DeviceActivationManager(PersistenceDependencyInjectionMixIn):

    def __init__(self, p_config:DeviceActivationManagerConfigModel):
        super().__init__()

        self._config : DeviceActivationManagerConfigModel = p_config
        self._logger = log_handling.get_logger(self.__class__.__name__)

        self._handlers :  Optional[list[BaseDeviceActivationHandler]] = []
        self._user_manager : Optional[UserManager] = None

    @property
    def user_manager(self) -> UserManager:
        if self._user_manager is None:
            self._user_manager = dependency_injection.container[UserManager]

        return self._user_manager


    def add_handler(self, p_handler: BaseDeviceActivationHandler):
        self._handlers.append(p_handler)

    def set_usage_permission_status_for_device(self, p_device:Device, p_usage_permitted: bool):
        for handler in self._handlers:
            handler.set_usage_permission_for_device(p_device=p_device, p_usage_permitted=p_usage_permitted)

    def check_device_activation_status(self):
        with SessionContext(p_persistence=self.persistence) as session_context:
            for device in self.device_entity_manager.devices(p_session_context=session_context):
                usage_permitted = True

                for user2device in device.users:
                    if user2device.active and user2device.blockable and user2device.user.active:
                        user_status = self.user_manager.get_current_user_status(
                            p_session_context=session_context, p_username=user2device.user.username)

                        if user_status is not None and not user_status.activity_allowed:
                            usage_permitted = False
                            break

                self.set_usage_permission_status_for_device(p_device=device,
                                                            p_usage_permitted=usage_permitted)

    def get_recurring_task(self) -> Optional[RecurringTask]:
        if not self._handlers:
            self._logger.info("No handlers for device activation registered.")
            return None

        task = RecurringTask(
            p_name="DeviceActivationManager.check_device_activation_status",
            p_handler_method=lambda: self.check_device_activation_status(),
            p_interval=self._config.check_interval)

        return task
