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

import little_brother.persistence.session_context
from little_brother import constants
from little_brother import dependency_injection
from little_brother.persistence.base_entity_manager import BaseEntityManager
from little_brother.persistence.persistent_rule_set_entity_manager import RuleSetEntityManager
from little_brother.persistence.persistent_user import User


class UserEntityManager(BaseEntityManager):

    def __init__(self):
        super().__init__(p_entity_class=User)

        self._users = None
        self._rule_set_entity_manager = None

    @property
    def rule_set_entity_manager(self):

        if self._rule_set_entity_manager is None:
            self._rule_set_entity_manager: RuleSetEntityManager = dependency_injection.container[RuleSetEntityManager]

        return self._rule_set_entity_manager

    def get_by_username(self, p_session_context: little_brother.persistence.session_context.SessionContext,
                        p_username: str):
        session = p_session_context.get_session()
        query = session.query(User).filter(User.username == p_username)

        if query.count() == 1:
            return query.one()

        else:
            return None

    def users(self, p_session_context):

        current_users = p_session_context.get_cache("users")

        if current_users is None:
            session = p_session_context.get_session()
            current_users = session.query(User).all()
            p_session_context.set_cache(p_name="users", p_object=current_users)

        return current_users

    def user_map(self, p_session_context):

        return {user.username: user for user in self.users(p_session_context=p_session_context)}

    def add_new_user(self, p_session_context, p_username, p_locale=None):

        if p_username in self.user_map(p_session_context):
            msg = "Cannot create new user {username}. Already in database!"
            self._logger.warning(msg.format(username=p_username))
            return

        session = p_session_context.get_session()
        new_user = User()
        new_user.username = p_username
        new_user.locale = p_locale
        new_user.process_name_pattern = constants.DEFAULT_PROCESS_NAME_PATTERN
        session.add(new_user)

        default_ruleset = self.rule_set_entity_manager.get_default_ruleset()
        default_ruleset.user = new_user
        session.add(default_ruleset)

        session.commit()
        self.persistence.clear_cache()

    def delete_user(self, p_session_context, p_username):

        session = p_session_context.get_session()
        user = self.get_by_username(p_session_context=p_session_context, p_username=p_username)

        if user is None:
            msg = "Cannot delete user {username}. Not in database!"
            self._logger.warning(msg.format(username=p_username))
            return

        for ruleset in user.rulesets:
            session.delete(ruleset)

        for user2device in user.devices:
            session.delete(user2device)

        session.delete(user)
        session.commit()
        self.persistence.clear_cache()