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

from little_brother import constants
from little_brother import simple_context_rule_handlers
from little_brother.persistence.base_entity_manager import BaseEntityManager
from little_brother.persistence.persistent_rule_set import RuleSet
from little_brother.persistence.session_context import SessionContext


class RuleSetEntityManager(BaseEntityManager):

    def __init__(self):
        super().__init__(p_entity_class=RuleSet)

    @classmethod
    def get_default_ruleset(cls, p_priority: int = constants.DEFAULT_RULE_SET_PRIORITY) -> RuleSet:

        default_ruleset = RuleSet()
        default_ruleset.priority = p_priority
        default_ruleset.context = simple_context_rule_handlers.DEFAULT_CONTEXT_RULE_HANDLER_NAME
        return default_ruleset

    def delete_ruleset(self, p_session_context: SessionContext, p_ruleset_id) -> None:

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

    def move_up_ruleset(self, p_session_context: SessionContext, p_ruleset_id: int) -> None:

        session = p_session_context.get_session()

        ruleset: RuleSet = self.get_by_id(p_session_context=p_session_context, p_id=p_ruleset_id)
        sorted_rulesets = sorted(ruleset.user.rulesets, key=lambda ruleset: ruleset.priority)
        self.move_ruleset(p_ruleset=ruleset, p_sorted_rulesets=sorted_rulesets)
        session.commit()

        self.persistence.clear_cache()

    def move_down_ruleset(self, p_session_context: SessionContext, p_ruleset_id: int) -> None:

        session = p_session_context.get_session()

        ruleset: RuleSet = self.get_by_id(p_session_context=p_session_context, p_id=p_ruleset_id)
        sorted_rulesets = sorted(ruleset.user.rulesets, key=lambda ruleset: -ruleset.priority)
        self.move_ruleset(p_ruleset=ruleset, p_sorted_rulesets=sorted_rulesets)
        session.commit()

        self.persistence.clear_cache()

    @classmethod
    def move_ruleset(cls, p_ruleset: RuleSet, p_sorted_rulesets):

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
