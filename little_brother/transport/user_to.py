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


class UserTO:

    def __init__(self,
                 p_username: str | None = None,
                 p_configured: bool | None = None,
                 p_id: int | None = None,
                 p_first_name: str | None = None,
                 p_last_name: str | None = None,
                 p_locale: str | None = None,
                 p_process_name_pattern: str | None = None,
                 p_prohibited_process_name_pattern: str | None = None,
                 p_active: bool | None = None):
        self.id = p_id
        self.username = p_username
        self.configured = p_configured
        self.first_name = p_first_name
        self.last_name = p_last_name
        self.locale = p_locale
        self.process_name_pattern = p_process_name_pattern
        self.prohibited_process_name_pattern = p_prohibited_process_name_pattern
        self.active = p_active
