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

from sqlalchemy import Column, Integer, String, DateTime

from little_brother.persistence.base_entity import BaseEntity
from little_brother.persistence.persistence_base import Base


class BlacklistedToken(Base, BaseEntity):
    __tablename__ = 'blacklisted_token'

    id = Column(Integer, primary_key=True)
    token = Column(String(255), unique=True)
    deletion_time = Column(DateTime)
