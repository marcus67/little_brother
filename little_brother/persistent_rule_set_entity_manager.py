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

from little_brother import base_entity_manager
from little_brother import constants
from little_brother import persistence
from little_brother import persistent_rule_set
from little_brother import persistent_user
from little_brother import simple_context_rule_handlers


class RuleSetEntityManager(base_entity_manager.BaseEntityManager):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_by_id(cls, p_session_context: persistence.SessionContext, p_id: int) -> persistent_rule_set.RuleSet:

        session = p_session_context.get_session()
        query = session.query(persistent_rule_set.RuleSet).filter(persistent_rule_set.RuleSet.id == p_id)

        if query.count() == 1:
            return query.one()

        else:
            return None

    @classmethod
    def get_default_ruleset(cls, p_priority: int = constants.DEFAULT_RULE_SET_PRIORITY) -> persistent_rule_set.RuleSet:

        default_ruleset = persistent_rule_set.RuleSet()
        default_ruleset.priority = p_priority
        default_ruleset.context = simple_context_rule_handlers.DEFAULT_CONTEXT_RULE_HANDLER_NAME
        return default_ruleset

    def add_ruleset(self, p_session_context: persistence.SessionContext, p_username: str) -> None:

        session = p_session_context.get_session()
        user = persistent_user.User.get_by_username(p_session=session, p_username=p_username)

        if user is None:
            msg = "Cannot add rule set to user {username}. Not in database!"
            self._logger.warning(msg.format(username=p_username))
            session.close()
            return

        new_priority = max([ruleset.priority for ruleset in user.rulesets]) + 1

        default_ruleset = self.get_default_ruleset(p_priority=new_priority)
        default_ruleset.user = user
        session.add(default_ruleset)
        session.commit()

        self.persistence.clear_cache()

    def delete_ruleset(self, p_session_context: persistence.SessionContext, p_ruleset_id) -> None:

        session = p_session_context.get_session()
        ruleset = self.get_by_id(p_session_context=p_session_context, p_id=p_ruleset_id)

        if ruleset is None:
            msg = "Cannot delete ruleset {id}. Not in database!"
            self._logger.warning(msg.format(id=p_ruleset_id))
            session.close()
            return

        session.delete(ruleset)
        session.commit()
        self.persistence.clear_cache()

    def move_up_ruleset(self, p_session_context: persistence.SessionContext, p_ruleset_id: int) -> None:

        session = p_session_context.get_session()

        ruleset = persistent_rule_set.RuleSet.get_by_id(p_session=session, p_id=p_ruleset_id)
        sorted_rulesets = sorted(ruleset.user.rulesets, key=lambda ruleset: ruleset.priority)
        self.move_ruleset(p_ruleset=ruleset, p_sorted_rulesets=sorted_rulesets)
        session.commit()

        self.persistence.clear_cache()

    def move_down_ruleset(self, p_session_context: persistence.SessionContext, p_ruleset_id: int) -> None:

        session = p_session_context.get_session()

        ruleset = persistent_rule_set.RuleSet.get_by_id(p_session=session, p_id=p_ruleset_id)
        sorted_rulesets = sorted(ruleset.user.rulesets, key=lambda ruleset: -ruleset.priority)
        self.move_ruleset(p_ruleset=ruleset, p_sorted_rulesets=sorted_rulesets)
        session.commit()

        self.persistence.clear_cache()

    @classmethod
    def move_ruleset(cls, p_ruleset: persistent_rule_set.RuleSet, p_sorted_rulesets):

        found = False
        index = 0

        while not found:
            if p_sorted_rulesets[index].priority == p_ruleset.priority:
                found = True

            else:
                index += 1

        other_ruleset = p_sorted_rulesets[index + 1]

        tmp = p_ruleset.priority
        p_ruleset.priority = other_ruleset.priority
        other_ruleset.priority = tmp
