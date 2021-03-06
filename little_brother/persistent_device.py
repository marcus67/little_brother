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

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from little_brother import constants
from little_brother import persistence_base
from python_base_app import tools

_ = lambda x: x


class Device(persistence_base.Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True)
    device_name = Column(String(256), nullable=False)
    hostname = Column(String(256))
    min_activity_duration = Column(Integer)
    max_active_ping_delay = Column(Integer)
    sample_size = Column(Integer)
    users = relationship("User2Device", back_populates="device", lazy="joined")

    def __init__(self):

        self.device_name = None
        self.hostname = None
        self.min_activity_duration = None
        self.max_active_ping_delay = None
        self.sample_size = None

    @staticmethod
    def get_by_device_name(p_session, p_device_name):
        query = p_session.query(Device).filter(Device.device_name == p_device_name)

        if query.count() == 1:
            return query.one()

        else:
            return None

    @staticmethod
    def get_by_id(p_session, p_id):
        query = p_session.query(Device).filter(Device.id == p_id)

        if query.count() == 1:
            return query.one()

        else:
            return None

    @property
    def html_key(self):
        return "device_{id}".format(id=self.id)

    @property
    def delete_html_key(self):
        return "delete_device_{id}".format(id=self.id)

    def list_of_users(self, p_exclude=None):

        return ", ".join(["{name} ({percent}%)".format(name=user2device.user.full_name, percent=user2device.percent)
                          for user2device in self.users
                          if p_exclude is None or not user2device.user is p_exclude])

    @property
    def summary(self):
        texts = []

        if len(self.users) > 0:
            texts.extend([_("Assigned users"), ": ", self.list_of_users()])

        texts.extend([constants.TEXT_SEPERATOR, _("Host Name"), ": ", tools.value_or_not_set(self.hostname)])

        return texts
