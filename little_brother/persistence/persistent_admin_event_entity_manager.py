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

from little_brother import admin_event
from little_brother.persistence import base_entity_manager
from little_brother.persistence.persistent_admin_event import AdminEvent
from little_brother.persistence.session_context import SessionContext
from python_base_app import tools


class AdminEventEntityManager(base_entity_manager.BaseEntityManager):

    def __init__(self):
        super().__init__(p_entity_class=AdminEvent)

    def log_admin_event(self, p_session_context: SessionContext, p_admin_event: admin_event.AdminEvent):

        session = p_session_context.get_session()
        event = tools.create_class_instance(AdminEvent, p_initial_values=p_admin_event)
        session.add(event)
        session.commit()

    def delete_historic_entries(self, p_session_context: SessionContext, p_history_length_in_days: int):

        session = p_session_context.get_session()
        reference_time = datetime.datetime.now() + datetime.timedelta(days=-p_history_length_in_days)

        result = session.query(AdminEvent).filter(AdminEvent.event_time < reference_time).all()

        msg = "Deleting {count} admin events..."
        self._logger.info(msg.format(count=len(result)))

        for event in result:
            session.delete(event)
