# -*- coding: utf-8 -*-

# Copyright (C) 2019-2024  Marcus Rickert
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

from sqlalchemy import Column, Integer, String, UniqueConstraint

from little_brother.persistence.base_entity import BaseEntity
from little_brother.persistence.persistence_base import Base
from little_brother.persistence.session_context import SessionContext

DEFAULT_SERVER_GROUP = "default-group"


def _(x):
    return x


class UidMapping(Base, BaseEntity):
    __tablename__ = 'uid_mapping'

    id = Column(Integer, primary_key=True)
    uid = Column(Integer, nullable=False)
    username = Column(String(64), nullable=False)
    server_group = Column(String(64), nullable=False)

    UniqueConstraint('uid', 'server_group', name='uid_server_group')

    def __init__(self):
        super(BaseEntity).__init__()
        self.server_group = None
        self.uid = None
        self.username = None

    def populate_test_data(self, p_session_context: SessionContext):
        self.server_group = "SOME-SERVER"
        self.uid = 123
        self.username = "willi"

    def __str__(self):
        return f"UID '{self.uid}' on '{self.server_group}' -> username '{self.username}'"
