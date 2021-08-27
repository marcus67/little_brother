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

from sqlalchemy import Column, Integer, String, Boolean, Date, Time

from little_brother.persistence.base_entity import BaseEntity
from little_brother.persistence.persistence_base import Base
from little_brother.persistence.session_context import SessionContext


class RuleOverride(Base, BaseEntity):
    __tablename__ = 'rule_override'

    id = Column(Integer, primary_key=True)
    key = Column(String(256))
    username = Column(String(256))
    reference_date = Column(Date)
    max_time_per_day = Column(Integer)
    min_time_of_day = Column(Time)
    max_time_of_day = Column(Time)
    min_break = Column(Integer)
    free_play = Column(Boolean)
    max_activity_duration = Column(Integer)

    def populate_test_data(self, p_session_context: SessionContext):
        self.key = "SomeKey"
        self.username = "some_user"
        self.reference_date = datetime.datetime.today()
        self.max_time_per_day = 123
        self.min_time_of_day = datetime.datetime.now().time()
        self.max_time_of_day = datetime.datetime.now().time()
        self.min_break = 456
        self.free_play = True
        self.max_activity_duration = 567
