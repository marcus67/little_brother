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

from sqlalchemy.sql.expression import and_

from little_brother.persistence.base_entity_manager import BaseEntityManager
from little_brother.persistence.persistent_daily_user_status import DailyUserStatus
from little_brother.persistence.session_context import SessionContext


class DailyUserStatusEntityManager(BaseEntityManager):

    def __init__(self):
        super().__init__(p_entity_class=DailyUserStatus)

    def delete_user_status(self, p_session_context: SessionContext, p_user_status_id) -> None:
        session = p_session_context.get_session()
        user_status = self.get_by_id(p_session_context=p_session_context, p_id=p_user_status_id)

        if user_status is None:
            msg = "Cannot delete user status {id}. Not in database!"
            self._logger.warning(msg.format(id=p_user_status_id))
            session.close()
            return

        session.delete(user_status)
        session.commit()
        self.persistence.clear_cache()


    def get_user_status(self, p_session_context: SessionContext, p_user_id:int,
                        p_reference_date:datetime.date) -> DailyUserStatus:

        session = p_session_context.get_session()

        result = session.query(DailyUserStatus).filter(
            and_(
                (DailyUserStatus.reference_date == p_reference_date),
                (DailyUserStatus.user_id == p_user_id)
            )).all()

        if len(result) == 0:
            return None

        elif len(result) == 1:
            return result[0]

        msg = "user status for user id '{user_id}' and reference date '{reference_date}' is not unique"
        self._logger.error(msg.format(user_id=p_user_id, reference_date=p_reference_date))

        return None
