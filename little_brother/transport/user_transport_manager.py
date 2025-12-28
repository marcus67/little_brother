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
    def get_user_to(p_user: User) -> UserTO:
        return UserTO(
            p_id=p_user.id,
            p_username=p_user.username,
            p_configured=True,
            p_first_name=p_user.first_name,
            p_last_name=p_user.last_name,
            p_process_name_pattern=p_user.process_name_pattern,
            p_prohibited_process_name_pattern=p_user.prohibited_process_name_pattern,
            p_locale=p_user.locale,
            p_active=p_user.active)

    @staticmethod
    def get_user_tos(p_users: List[User],
                     p_unmonitored_users: List[str],
                     p_active_user_id: int) -> List[UserTO]:
        tos = [ UserTransportManager.get_user_to(user) for user in p_users
                if user.id == p_active_user_id or p_active_user_id is None]

        if p_active_user_id is None:
            tos.extend(
                [ UserTO(
                    p_username=username,
                    p_configured=False
                ) for username in p_unmonitored_users
                ]
            )

        return tos
