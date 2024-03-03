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

from typing import Optional

from little_brother.persistence.base_entity_manager import BaseEntityManager
from little_brother.persistence.persistent_uid_mapping import UidMapping, DEFAULT_SERVER_GROUP
from little_brother.persistence.session_context import SessionContext
from python_base_app import log_handling


class UidMappingEntityManager(BaseEntityManager):

    def __init__(self):
        super().__init__(p_entity_class=UidMapping)

        self._uidMappings = None
        self._rule_set_entity_manager = None
        self._logger = log_handling.get_logger(self.__class__.__name__)

    @staticmethod
    def uid_mappings(p_session_context):

        current_uid_mappings = p_session_context.get_cache("uid_mappings")

        if current_uid_mappings is None:
            session = p_session_context.get_session()
            current_uid_mappings = session.query(UidMapping).all()
            p_session_context.set_cache(p_name="uid_mappings", p_object=current_uid_mappings)

        return current_uid_mappings

    @staticmethod
    def get_by_uid_and_server_group(p_session_context: SessionContext, p_uid: int,
                                    p_server_group: str = DEFAULT_SERVER_GROUP) -> Optional[UidMapping]:

        session = p_session_context.get_session()
        query = session.query(UidMapping).filter(UidMapping.uid == p_uid and UidMapping.server_group == p_server_group)

        if query.count() == 1:
            return query.one()

        else:
            return None

    @staticmethod
    def get_by_server_group(p_session_context: SessionContext,
                            p_server_group: str = DEFAULT_SERVER_GROUP) -> list[UidMapping]:

        session = p_session_context.get_session()
        query = session.query(UidMapping).filter(UidMapping.server_group == p_server_group)

        return query.all()

    @staticmethod
    def get_server_groups(p_session_context: SessionContext):
        session = p_session_context.get_session()
        query = session.query(UidMapping.server_group)
        return [entry[0] for entry in query.distinct().all()]

    @staticmethod
    def get_by_username_and_server_group(p_session_context: SessionContext, p_username: str,
                                         p_server_group: str = DEFAULT_SERVER_GROUP) -> Optional[UidMapping]:

        session = p_session_context.get_session()
        query = session.query(UidMapping).filter(UidMapping.username == p_username and
                                                 UidMapping.server_group == p_server_group)

        if query.count() == 1:
            return query.one()

        else:
            return None

    def insert_or_update_uid_mapping(self, p_session_context, p_uid_mapping: UidMapping) -> int:

        session = p_session_context.get_session()

        uid_mapping = self.get_by_uid_and_server_group(p_session_context=p_session_context,
                                                       p_uid=p_uid_mapping.uid,
                                                       p_server_group=p_uid_mapping.server_group)

        if uid_mapping is not None:
            uid_mapping.username = p_uid_mapping.username
            self._logger.info(f"Updating mapping {str(uid_mapping)} to username '{str(p_uid_mapping.username)}'")
            session.commit()
            return uid_mapping.id

        else:
            session.add(p_uid_mapping)
            session.commit()
            self._logger.info(f"Creating new mapping {str(p_uid_mapping)}")
            return p_uid_mapping.id
