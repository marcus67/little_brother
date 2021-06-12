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

from sqlalchemy import Column, Integer, String, Boolean, Time, ForeignKey
from sqlalchemy.orm import relationship

from little_brother import constants
from little_brother import simple_context_rule_handlers
from little_brother.persistence.base_entity import BaseEntity
from little_brother.persistence.persistence_base import Base
from little_brother.persistence.persistent_user import User
from little_brother.persistence.session_context import SessionContext
from python_base_app import tools

_ = lambda x: x


class RuleSet(Base, BaseEntity):
    __tablename__ = 'ruleset'

    id = Column(Integer, primary_key=True)

    context_label = Column(String(256))
    context = Column(String(256))
    context_details = Column(String(256))
    priority = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="rulesets", lazy="joined")
    min_time_of_day = Column(Time)
    max_time_of_day = Column(Time)
    max_time_per_day = Column(Integer)
    max_activity_duration = Column(Integer)
    min_break = Column(Integer)
    free_play = Column(Boolean)
    # As of version 0.4.6
    optional_time_per_day = Column(Integer)

    def __init__(self):

        super(BaseEntity).__init__()
        self.context = None
        self.context_details = None
        self.context_label = None
        self.min_time_of_day = None
        self.max_time_of_day = None
        self.max_time_per_day = None
        self.max_activity_duration = None
        self.min_break = None
        self.free_play = False
        self.priority = constants.DEFAULT_RULE_SET_PRIORITY
        self._get_context_rule_handler = None

    def populate_test_data(self, p_session_context: SessionContext):

        session = p_session_context.get_session()

        user = User()
        user.populate_test_data(p_session_context=p_session_context)
        session.add(user)

        self.user = user
        self.context = simple_context_rule_handlers.DEFAULT_CONTEXT_RULE_HANDLER_NAME
        self.context_details = None
        self.context_label = None
        self.min_time_of_day = None
        self.max_time_of_day = None
        self.max_time_per_day = None
        self.max_activity_duration = None
        self.min_break = None
        self.free_play = False
        self.priority = constants.DEFAULT_RULE_SET_PRIORITY

    @property
    def label(self):
        if self.context_label:
            return self.context_label

        else:
            return self.context

    @property
    def summary(self):
        context_handler = self._get_context_rule_handler(p_context_name=self.context)

        texts = []

        if context_handler is not None:
            texts.extend(context_handler.summary(p_context_detail=self.context_details))

        if self.max_time_per_day is not None:
            texts.append(constants.TEXT_SEPERATOR)
            texts.append("Time per Day")
            texts.append(": " + tools.get_duration_as_string(p_seconds=self.max_time_per_day, p_include_seconds=False))

        return texts

    @property
    def html_key(self):
        return "ruleset_{id}".format(id=self.id)

    @property
    def delete_html_key(self):
        return "delete_ruleset_{id}".format(id=self.id)

    @property
    def move_up_html_key(self):
        return "move_up_ruleset_{id}".format(id=self.id)

    @property
    def move_down_html_key(self):
        return "move_down_ruleset_{id}".format(id=self.id)

    @property
    def can_move_up(self):

        return 1 < self.priority < self.user.maximum_rule_priority

    @property
    def can_move_down(self):

        return self.priority > 2

    @property
    def fixed_context(self):

        return self.priority == 1
