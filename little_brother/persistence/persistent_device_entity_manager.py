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

from little_brother import constants
from little_brother import dependency_injection
from little_brother.persistence import persistent_rule_set_entity_manager, base_entity_manager
from little_brother.persistence.persistent_device import Device
from little_brother.persistence.persistent_user import User
from little_brother.persistence.persistent_user_2_device import User2Device
from little_brother.persistence.session_context import SessionContext
from python_base_app import tools


class DeviceEntityManager(base_entity_manager.BaseEntityManager):

    def __init__(self):
        super().__init__(p_entity_class=Device)

        self._devices = None

    @property
    def rule_set_entity_manager(self):

        if self._rule_set_entity_manager is None:
            self._rule_set_entity_manager: persistent_rule_set_entity_manager.RuleSetEntityManager = \
                dependency_injection.container[persistent_rule_set_entity_manager.RuleSetEntityManager]

        return self._rule_set_entity_manager

    def get_by_device_name(self, p_session_context: SessionContext, p_device_name: str):

        session = p_session_context.get_session()
        query = session.query(Device).filter(Device.device_name == p_device_name)

        if query.count() == 1:
            return query.one()

        else:
            return None

    def devices(self, p_session_context: SessionContext):

        current_devices = p_session_context.get_cache("devices")

        if current_devices is None:
            session = p_session_context.get_session()
            current_devices = session.query(Device).options().all()
            p_session_context.set_cache(p_name="devices", p_object=current_devices)

        return current_devices

    def hostname_device_map(self, p_session_context: SessionContext):

        return {device.hostname: device for device in self.devices(p_session_context=p_session_context)}

    def device_map(self, p_session_context: SessionContext):

        return {device.device_name: device for device in self.devices(p_session_context=p_session_context)}

    def add_new_device(self, p_session_context: SessionContext, p_name_pattern: str):

        session = p_session_context.get_session()
        new_device = Device()
        new_device.device_name = tools.get_new_object_name(
            p_name_pattern=p_name_pattern,
            p_existing_names=[device.device_name for device in self.devices(p_session_context)])
        new_device.sample_size = constants.DEFAULT_DEVICE_SAMPLE_SIZE
        new_device.min_activity_duration = constants.DEFAULT_DEVICE_MIN_ACTIVITY_DURATION
        new_device.max_active_ping_delay = constants.DEFAULT_DEVICE_MAX_ACTIVE_PING_DELAY
        session.add(new_device)

        session.commit()
        self.persistence.clear_cache()

    def add_device(self, p_session_context, p_username, p_device_id):

        session = p_session_context.get_session()
        user = User.get_by_username(p_session=session, p_username=p_username)

        if user is None:
            msg = "Cannot add device to user {username}. Not in database!"
            self._logger.warning(msg.format(username=p_username))
            session.close()
            return

        device = Device.get_by_id(p_session=session, p_id=p_device_id)

        if device is None:
            msg = "Cannot add device id {id} to user {username}. Not in database!"
            self._logger.warning(msg.format(id=p_device_id, username=p_username))
            session.close()
            return

        user2device = User2Device()
        user2device.user = user
        user2device.device = device
        user2device.active = False
        user2device.percent = 100

        session.add(user2device)

        session.commit()
        self.persistence.clear_cache()

    def delete_device(self, p_session_context: SessionContext, p_id: int):

        session = p_session_context.get_session()
        device = self.get_by_id(p_session_context=p_session_context, p_id=p_id)

        if device is None:
            msg = "Cannot delete device {id}. Not in database!"
            self._logger.warning(msg.format(id=p_id))
            session.close()
            return

        for user2device in device.users:
            session.delete(user2device)

        session.delete(device)
        session.commit()
        self.persistence.clear_cache()
