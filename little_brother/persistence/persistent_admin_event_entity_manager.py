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

from little_brother import admin_event
from little_brother.persistence import base_entity_manager
from little_brother.persistence.persistent_admin_event import AdminEvent
from little_brother.persistence.session_context import SessionContext
from python_base_app import tools


class AdminEventEntityManager(base_entity_manager.BaseEntityManager):

    def __init__(self):
        super().__init__(p_entity_class=AdminEvent)

    @staticmethod
    def log_admin_event(p_session_context: SessionContext, p_admin_event: admin_event.AdminEvent):

        session = p_session_context.get_session()
        event = tools.create_class_instance(AdminEvent, p_initial_values=p_admin_event)
        session.add(event)
        session.commit()

    def delete_historic_entries(self, p_session_context: SessionContext, p_history_length_in_days: int):

        self.delete_generic_historic_entries(p_session_context=p_session_context,
                                             p_history_length_in_days=p_history_length_in_days,
                                             p_reference_time_column=AdminEvent.event_time)
