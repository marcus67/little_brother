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
from little_brother.persistence.base_entity import BaseEntity
from little_brother.persistence.persistence_base import Base
from little_brother.persistence.session_context import SessionContext
from python_base_app import tools


def _(x):
    return x


class User(Base, BaseEntity):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    process_name_pattern = Column(String(256))
    prohibited_process_name_pattern = Column(String(4096))
    username = Column(String(256))
    first_name = Column(String(256))
    last_name = Column(String(256))
    locale = Column(String(5))
    active = Column(Boolean)
    access_code = Column(String(256), default=constants.DEFAULT_ACCESS_CODE)
    rulesets = relationship("RuleSet", back_populates="user", lazy="joined")
    devices = relationship("User2Device", back_populates="user", lazy="joined")
    status = relationship("DailyUserStatus", back_populates="user", lazy="joined")

    def __init__(self):

        super(BaseEntity).__init__()
        self.process_name_pattern = None
        self.prohibited_process_name_pattern = None
        self.username = None
        self.first_name = None
        self.last_name = None
        self.locale = None
        self.active = False

        self._regex_process_name_pattern = None
        self._regex_prohibited_process_name_pattern = None

    @classmethod
    def get_regex_from_pattern_list(cls, p_pattern_list:str, p_check_path_component:bool):

        pattern_list = p_pattern_list.replace('\r', '').split("\n")
        normalized_pattern_list = [ entry.strip() for entry in pattern_list if len(entry.strip()) > 1 ]

        if len(normalized_pattern_list) == 0:
            # Return if none of the sub patterns contains more than one character
            return None

        if "/" in p_pattern_list and p_check_path_component:
            expanded_patterns = '|'.join(normalized_pattern_list)

        else:
            expanded_patterns = '(.*' + '.*)|(.*'.join(normalized_pattern_list) + '.*)'

        return re.compile(expanded_patterns)

    def populate_test_data(self, p_session_context: SessionContext):

        self.process_name_pattern = None
        self.prohibited_process_name_pattern = None
        self.username = "willi"
        self.first_name = "Willi"
        self.last_name = "Wusel"
        self.locale = "de"
        self.active = True

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
        self._regex_prohibited_process_name_pattern = None

    @property
    def regex_process_name_pattern(self):

        if self._regex_process_name_pattern is None:

            self._regex_process_name_pattern = \
                self.get_regex_from_pattern_list(p_pattern_list=self.process_name_pattern, p_check_path_component=True)

        return self._regex_process_name_pattern

    @property
    def regex_prohibited_process_name_pattern(self):


        if self._regex_prohibited_process_name_pattern is None and self.prohibited_process_name_pattern is not None:
            self._regex_prohibited_process_name_pattern = \
                self.get_regex_from_pattern_list(p_pattern_list=self.prohibited_process_name_pattern,
                                                 p_check_path_component=False)

        return self._regex_prohibited_process_name_pattern


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
        fmt = "User (username='{username}, active={active}, process_name_pattern='{process_name_pattern}', "\
              "prohibited_process_name_pattern='{prohibited_process_name_pattern}')"
        return fmt.format(username=self.username, active=self.active, process_name_pattern=self.process_name_pattern,
                          prohibited_process_name_pattern=self.prohibited_process_name_pattern)
