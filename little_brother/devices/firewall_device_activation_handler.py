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
from little_brother.devices.firewall_handler import FirewallHandler
from little_brother.persistence.persistent_device import Device
from python_base_app import log_handling


class FirewallDeviceActivationHandler(BaseDeviceActivationHandler):

    def __init__(self):
        self._firewall_handler: Optional[FirewallHandler] = None
        self._logger = log_handling.get_logger(self.__class__.__name__)

    @property
    def firewall_handler(self) -> FirewallHandler:
        if self._firewall_handler is None:
            self._firewall_handler = dependency_injection.container[FirewallHandler]

        return self._firewall_handler

    def set_usage_permission_for_device(self, p_device: Device, p_usage_permitted: bool):
        self._logger.debug(f"Set usage permission for device '{p_device.device_name}' to {p_usage_permitted}")

        self.firewall_handler.set_usage_permission_for_ip(p_ip_address=p_device.ip_address,
                                                          p_blocked_ip_addresses=p_device.list_of_blocked_ip_addresses,
                                                          p_usage_permitted=p_usage_permitted)
