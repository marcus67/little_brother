# -*- coding: utf-8 -*-

# Copyright (C) 2019-2023  Marcus Rickert
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
from typing import List, Type

import sqlalchemy
from sqlalchemy.orm import Session

from little_brother import dependency_injection
from little_brother import process_info
from little_brother.persistence import base_entity_manager
from little_brother.persistence.persistent_blacklisted_token import BlacklistedToken
from little_brother.persistence.persistent_device_entity_manager import DeviceEntityManager
from little_brother.persistence.persistent_process_info import ProcessInfo
from little_brother.persistence.session_context import SessionContext
from python_base_app import tools


class BlacklistedTokenEntityManager(base_entity_manager.BaseEntityManager):

    def __init__(self):
        super().__init__(p_entity_class=BlacklistedToken)

    def get_old_tokens(self, p_session:Session, p_cut_off_time: datetime.datetime) -> List[Type[BlacklistedToken]]:

        try:
            query = p_session.query(BlacklistedToken).filter(BlacklistedToken.deletion_time < p_cut_off_time)

            tokens_to_be_deleted = [ token for token in query]
            return tokens_to_be_deleted

        except Exception as e:
            self._logger.error(f"Exception '{str(e)}' while cleaning out old tokens.")
            return []
