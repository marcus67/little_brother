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
from little_brother.persistence.persistent_time_extension import TimeExtension


class TimeExtensionEntityManager(BaseEntityManager):

    def __init__(self):
        super().__init__(p_entity_class=TimeExtension)

    @classmethod
    def get_active_time_extensions(cls, p_session_context, p_reference_datetime):

        session = p_session_context.get_session()

        result = session.query(TimeExtension).filter(
            and_(
                (p_reference_datetime >= TimeExtension.reference_datetime),
                (p_reference_datetime < TimeExtension.end_datetime)
            )
        ).all()

        return {play_time.username: play_time for play_time in result}

    @classmethod
    def set_time_extension(cls, p_session_context, p_username, p_reference_datetime, p_start_datetime, p_time_delta):

        session = p_session_context.get_session()
        result = session.query(TimeExtension).filter(
            and_(
                (p_reference_datetime >= TimeExtension.reference_datetime),
                (p_reference_datetime < TimeExtension.end_datetime),
                (p_username == TimeExtension.username)
            )
        ).all()

        if len(result) == 0:
            time_extension = TimeExtension()
            session.add(time_extension)
            time_extension.username = p_username
            time_extension.reference_datetime = p_reference_datetime
            time_extension.start_datetime = p_start_datetime
            time_extension.end_datetime = p_start_datetime + datetime.timedelta(minutes=p_time_delta)
            session.commit()

        elif len(result) == 1:
            time_extension = result.pop()
            new_end_datetime = time_extension.end_datetime + datetime.timedelta(minutes=p_time_delta)

            if new_end_datetime <= time_extension.start_datetime or p_time_delta == 0:
                session.delete(time_extension)
                session.commit()

            else:
                time_extension.end_datetime = new_end_datetime
                session.commit()
