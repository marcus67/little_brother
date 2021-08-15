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

from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship

from little_brother.persistence.base_entity import BaseEntity
from little_brother.persistence.persistence_base import Base
from little_brother.persistence.persistent_user import User
from little_brother.persistence.session_context import SessionContext

_ = lambda x: x


class DailyUserStatus(Base, BaseEntity):
    __tablename__ = 'user_status'

    id = Column(Integer, primary_key=True)

    reference_date =Column(Date, nullable=False)
    # Optional time (in minutes) used on the reference day
    optional_time_used = Column(Integer, nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="status", lazy="joined")

    def __init__(self):
        super(BaseEntity).__init__()
        self.optional_time_used = 0
        self.reference_date = datetime.date.today()

    def populate_test_data(self, p_session_context: SessionContext):
        session = p_session_context.get_session()

        user = User()
        user.populate_test_data(p_session_context=p_session_context)
        session.add(user)

        self.user = user
        self.optional_time_used = 0
        self.reference_date = datetime.date.today()
