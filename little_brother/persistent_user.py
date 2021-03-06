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

import re

import sqlalchemy.orm
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from little_brother import constants
from little_brother import persistence_base
from python_base_app import tools

_ = lambda x: x


class User(persistence_base.Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    process_name_pattern = Column(String(256))
    username = Column(String(256))
    first_name = Column(String(256))
    last_name = Column(String(256))
    locale = Column(String(5))
    active = Column(Boolean)
    rulesets = relationship("RuleSet", back_populates="user", lazy="joined")
    devices = relationship("User2Device", back_populates="user", lazy="joined")

    def __init__(self):

        self.process_name_pattern = None
        self.username = None
        self.first_name = None
        self.last_name = None
        self.locale = None
        self.active = False

        self.init_on_load()

    @staticmethod
    def get_by_username(p_session, p_username):
        query = p_session.query(User).filter(User.username == p_username)

        if query.count() == 1:
            return query.one()

        else:
            return None

    @property
    def notification_name(self):
        if self.first_name is not None and self.first_name != '':
            return self.first_name

        else:
            return self.username.capitalize()

    @property
    def full_name(self):
        if self.first_name is not None and self.first_name != '':
            if self.last_name is not None and self.last_name != '':
                return self.first_name + " " + self.last_name

            else:
                return self.first_name

        else:
            return self.username.capitalize()

    @property
    def device_list(self):
        if len(self.devices) == 0:
            return tools.value_or_not_set(None)

        else:
            return ", ".join([user2device.device.device_name for user2device in self.devices])

    @property
    def html_key(self):
        return "user_{id}".format(id=self.id)

    @property
    def rulesets_html_key(self):
        return "rulesets_user_{id}".format(id=self.id)

    @property
    def devices_html_key(self):
        return "devices_user_{id}".format(id=self.id)

    @property
    def delete_html_key(self):
        return "delete_user_{id}".format(id=self.id)

    @property
    def new_ruleset_html_key(self):
        return "new_ruleset_user_{id}".format(id=self.id)

    @property
    def new_device_html_key(self):
        return "new_device_user_{id}".format(id=self.id)

    @sqlalchemy.orm.reconstructor
    def init_on_load(self):
        self._regex_process_name_pattern = None

    @property
    def regex_process_name_pattern(self):

        if self._regex_process_name_pattern is None:

            if "/" in self.process_name_pattern:
                self._regex_process_name_pattern = re.compile(self.process_name_pattern)

            else:
                self._regex_process_name_pattern = re.compile(".*(" + self.process_name_pattern + ").*")

        return self._regex_process_name_pattern

    @property
    def sorted_rulesets(self):
        return sorted(self.rulesets, key=lambda ruleset: -ruleset.priority)

    @property
    def maximum_rule_priority(self):
        return max([rule_set.priority for rule_set in self.rulesets])

    @property
    def sorted_user2devices(self):
        return sorted(self.devices, key=lambda user2device: (-user2device.percent, user2device.device.device_name))

    @property
    def summary(self):

        texts = []

        if self.username.upper() != self.full_name.upper():
            texts.extend([_("Username"), ":", self.username])

        texts.extend([constants.TEXT_SEPERATOR, _("Monitored"), ": ", tools.format_boolean(p_value=self.active)])

        if self.locale is not None:
            lang = constants.LANGUAGES.get(self.locale)

            if lang is None:
                lang = _("Unknown")

            texts.extend([constants.TEXT_SEPERATOR, _("Locale"), ": ", lang])

        return texts

    def __str__(self):
        fmt = "User (username='{username}, active={active}, process_name_pattern='{process_name_pattern}')"
        return fmt.format(username=self.username, active=self.active, process_name_pattern=self.process_name_pattern)
