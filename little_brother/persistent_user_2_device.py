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

from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from little_brother import constants
from little_brother import persistence_base
from python_base_app import tools

_ = lambda x: x


class User2Device(persistence_base.Base):
    __tablename__ = 'user2device'

    id = Column(Integer, primary_key=True)
    active = Column(Boolean)
    percent = Column(Integer)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="devices", lazy="joined")

    device_id = Column(Integer, ForeignKey("device.id"), nullable=False)
    device = relationship("Device", back_populates="users", lazy="joined")

    @property
    def summary(self):

        texts = [constants.TEXT_SEPERATOR, _("Monitored"), ": ", tools.format_boolean(p_value=self.active),
                 constants.TEXT_SEPERATOR, "{percent}%".format(percent=self.percent)]

        if len(self.device.users) > 1:
            texts.extend([constants.TEXT_SEPERATOR, _("Shared with"), ": ",
                          self.device.list_of_users(p_exclude=self.user)])

        return texts

    @property
    def html_key(self):
        return "user2device_{id}".format(id=self.id)

    @property
    def delete_html_key(self):
        return "delete_user2device_{id}".format(id=self.id)
