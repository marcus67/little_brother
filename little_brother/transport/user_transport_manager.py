# -*- coding: utf-8 -*-
# Copyright (C) 2019-24  Marcus Rickert
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
from typing import List

from little_brother.persistence.persistent_user import User
from little_brother.transport.user_to import UserTO


class UserTransportManager:

    @staticmethod
    def get_user_tos(p_users: List[User],
                     p_unmonitored_users: List[str]) -> List[UserTO]:
        tos = [ UserTO(
            p_id=user.id,
            p_username=user.username,
            p_configured=True,
            p_first_name=user.first_name,
            p_last_name=user.last_name,
            p_process_name_pattern=user.process_name_pattern,
            p_prohibited_process_name_pattern=user.prohibited_process_name_pattern,
            p_locale=user.locale,
            p_active=user.active)
            for user in p_users
        ]
        tos.extend(
            [ UserTO(
                p_username=username,
                p_configured=False
            ) for username in p_unmonitored_users
            ]
        )

        return tos
