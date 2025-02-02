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

from little_brother.transport.user_admin_detail_to import UserAdminDetailTO
from little_brother.transport.user_status_to import UserStatusTO


class UserAdminTO:

    def __init__(self,
                 p_username: str,
                 p_user_status: UserStatusTO,
                 p_max_lookahead_in_days: int,
                 p_user_admin_details: list[UserAdminDetailTO] = None):
        self.username = p_username
        self.user_status = p_user_status
        self.max_lookahead_in_days = p_max_lookahead_in_days
        self.user_admin_details = p_user_admin_details
