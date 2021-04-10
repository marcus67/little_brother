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

from sqlalchemy import Column, Integer, String, DateTime

from little_brother.persistence.base_entity import BaseEntity
from little_brother.persistence.persistence_base import Base


class TimeExtension(Base, BaseEntity):
    __tablename__ = 'time_extension'

    id = Column(Integer, primary_key=True)
    username = Column(String(256))
    reference_datetime = Column(DateTime)
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)

    def __init__(self):

        self.username:str = None
        self.reference_datetime:datetime.datetime = None
        self.start_datetime:datetime.datetime = None
        self.end_datetime:datetime.datetime = None

    def get_length_in_minutes(self):

        return int((self.end_datetime - self.start_datetime).total_seconds() / 60.0 + 0.5)
