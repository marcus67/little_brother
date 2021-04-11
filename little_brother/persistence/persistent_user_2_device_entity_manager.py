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
from little_brother.persistence import base_entity_manager
from little_brother.persistence.persistent_device import Device
from little_brother.persistence.persistent_device_entity_manager import DeviceEntityManager
from little_brother.persistence.persistent_user_2_device import User2Device
from little_brother.persistence.persistent_user_entity_manager import UserEntityManager
from little_brother.persistence.session_context import SessionContext


class User2DeviceEntityManager(base_entity_manager.BaseEntityManager):

    def __init__(self):
        super().__init__(p_entity_class=User2Device)

        self._user_2_devices = None
        self._user_entity_manager = None
        self._device_entity_manager = None

    @property
    def user_entity_manager(self):

        if self._user_entity_manager is None:
            self._user_entity_manager: UserEntityManager = \
                dependency_injection.container[UserEntityManager]

        return self._user_entity_manager

    @property
    def device_entity_manager(self):

        if self._device_entity_manager is None:
            self._device_entity_manager: DeviceEntityManager = \
                dependency_injection.container[DeviceEntityManager]

        return self._device_entity_manager

    def get_by_id(self, p_session_context: SessionContext, p_id: int):

        session = p_session_context.get_session()
        query = session.query(User2Device).filter(User2Device.id == p_id)

        if query.count() == 1:
            return query.one()

        else:
            return None

    def delete_user2device(self, p_session_context: SessionContext, p_user2device_id: int):

        session = p_session_context.get_session()
        user2device = self.get_by_id(p_session_context=p_session_context, p_id=p_user2device_id)

        if user2device is None:
            msg = "Cannot delete user2device {id}. Not in database!"
            self._logger.warning(msg.format(id=p_user2device_id))
            session.close()
            return

        session.delete(user2device)
        session.commit()
        self.persistence.clear_cache()

    def add_user2device(self, p_session_context: SessionContext, p_username: str, p_device_id: int) -> int:

        user = self.user_entity_manager.get_by_username(p_session_context=p_session_context, p_username=p_username)

        if user is None:
            msg = "Cannot add device to user {username}. Not in database!"
            self._logger.warning(msg.format(username=p_username))
            return None

        device: Device = self.device_entity_manager.get_by_id(p_session_context=p_session_context, p_id=p_device_id)

        if device is None:
            msg = "Cannot add device id {id} to user {username}. Not in database!"
            self._logger.warning(msg.format(id=p_device_id, username=p_username))
            return None

        session = p_session_context.get_session()
        user2device = User2Device()
        user2device.user = user
        user2device.device = device
        user2device.active = False
        user2device.percent = 100

        session.add(user2device)

        session.commit()
        self.persistence.clear_cache()

        return user2device.id
