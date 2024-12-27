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
from typing import Type

from sqlalchemy import Column

from little_brother import dependency_injection
from little_brother.persistence import persistence
from little_brother.persistence.session_context import SessionContext
from python_base_app import log_handling


class BaseEntityManager(object):

    def __init__(self, p_entity_class: Type):
        self._logger = log_handling.get_logger(self.__class__.__name__)
        self._entity_class = p_entity_class
        self._persistence: persistence.Persistence | None = None

    @property
    def persistence(self):
        if self._persistence is None:
            self._persistence = dependency_injection.container[persistence.Persistence]

        return self._persistence

    def get_by_id(self, p_session_context: SessionContext, p_id: int):

        session = p_session_context.get_session()
        query = session.query(self._entity_class).filter(self._entity_class.id == p_id)

        if query.count() == 1:
            return query.one()

        else:
            return None

    def delete_generic_historic_entries(self, p_session_context: SessionContext,
                                        p_history_length_in_days: int, p_reference_time_column: Column):

        session = p_session_context.get_session()
        reference_time = datetime.datetime.now() + datetime.timedelta(days=-p_history_length_in_days)

        result = session.query(self._entity_class).filter(p_reference_time_column< reference_time).all()

        msg = f"Deleting {len(result)} table row(s) of class {self._entity_class.__name__}..."
        self._logger.info(msg)

        for event in result:
            session.delete(event)

        session.commit()
