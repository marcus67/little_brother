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

import sqlalchemy

from little_brother import dependency_injection
from little_brother import process_info
from little_brother.persistence import base_entity_manager
from little_brother.persistence.persistent_device_entity_manager import DeviceEntityManager
from little_brother.persistence.persistent_process_info import ProcessInfo
from little_brother.persistence.session_context import SessionContext
from python_base_app import tools


class ProcessInfoEntityManager(base_entity_manager.BaseEntityManager):

    def __init__(self):
        super().__init__(p_entity_class=ProcessInfo)

        self._process_infos = None
        self._device_entity_manager = None

    @property
    def device_entity_manager(self):

        if self._device_entity_manager is None:
            self._device_entity_manager: DeviceEntityManager = \
                dependency_injection.container[DeviceEntityManager]

        return self._device_entity_manager

    def load_process_infos(self, p_session_context, p_lookback_in_days):

        session = p_session_context.get_session()
        reference_time = datetime.datetime.now() + datetime.timedelta(days=-p_lookback_in_days)

        result = session.query(ProcessInfo).filter(
            ProcessInfo.start_time > reference_time).all()

        for pinfo in result:
            device = self.device_entity_manager.hostname_device_map(
                p_session_context=p_session_context).get(pinfo.hostname)

            if device is not None:
                pinfo.hostlabel = device.device_name

            else:
                pinfo.hostlabel = None

        return result

    def write_process_info(self, p_session_context: SessionContext, p_process_info: process_info.ProcessInfo):

        session = p_session_context.get_session()
        exists = session.query(sqlalchemy.exists().where(
            ProcessInfo.key == p_process_info.get_key())).scalar()

        if not exists:
            pinfo = tools.create_class_instance(ProcessInfo, p_initial_values=p_process_info)
            pinfo.key = p_process_info.get_key()
            session.add(pinfo)

        session.commit()

    def update_process_info(self, p_session_context: SessionContext, p_process_info: process_info.ProcessInfo):

        session = p_session_context.get_session()
        pinfo = session.query(ProcessInfo).filter(
            ProcessInfo.key == p_process_info.get_key()).one()
        pinfo.end_time = p_process_info.end_time
        pinfo.downtime = p_process_info.downtime
        session.commit()

    def delete_historic_entries(self, p_session_context: SessionContext, p_history_length_in_days: int):

        session = p_session_context.get_session()
        reference_time = datetime.datetime.now() + datetime.timedelta(days=-p_history_length_in_days)
        result = session.query(ProcessInfo).filter(ProcessInfo.start_time < reference_time).all()

        msg = "Deleting {count} process infos..."
        self._logger.info(msg.format(count=len(result)))

        for pinfo in result:
            session.delete(pinfo)

        session.commit()
