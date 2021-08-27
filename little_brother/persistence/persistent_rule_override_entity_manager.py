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

from sqlalchemy.sql.expression import and_

from little_brother.persistence import base_entity_manager
from little_brother.persistence.persistent_rule_override import RuleOverride
from little_brother.persistence.session_context import SessionContext
from python_base_app import tools


class RuleOverrideEntityManager(base_entity_manager.BaseEntityManager):

    def __init__(self):
        super().__init__(p_entity_class=RuleOverride)

    def update_rule_override(self, p_session_context: SessionContext, p_rule_override):

        session = p_session_context.get_session()
        query = session.query(RuleOverride).filter(RuleOverride.key == p_rule_override.get_key())

        if query.count() == 1:
            override = query.one()
            override.min_time_of_day = p_rule_override.min_time_of_day
            override.max_time_of_day = p_rule_override.max_time_of_day
            override.max_time_per_day = p_rule_override.max_time_per_day
            override.min_break = p_rule_override.min_break
            override.free_play = p_rule_override.free_play
            override.max_activity_duration = p_rule_override.max_activity_duration

        else:
            override = tools.create_class_instance(RuleOverride, p_initial_values=p_rule_override)
            override.key = p_rule_override.get_key()
            session.add(override)

        session.commit()

    def load_rule_overrides(self, p_session_context: SessionContext, p_lookback_in_days):

        session = p_session_context.get_session()
        reference_time = datetime.datetime.now() + datetime.timedelta(days=-p_lookback_in_days)
        result = session.query(RuleOverride).filter(RuleOverride.reference_date > reference_time).all()

        return result

    def get_rule_override_by_username_and_date(self, p_session_context: SessionContext,
                                               p_username: str, p_date: datetime.date):

        session = p_session_context.get_session()
        result = session.query(RuleOverride).filter(
         and_(RuleOverride.username == p_username, RuleOverride.reference_date == p_date))

        for item in result:
            print(str(item))

        if result.count() == 1:
            return result.one()

        else:
            return None

    def delete_historic_entries(self, p_session_context: SessionContext, p_history_length_in_days: int):

        session = p_session_context.get_session()
        reference_time = datetime.datetime.now() + datetime.timedelta(days=-p_history_length_in_days)
        reference_date = reference_time.date()

        result = session.query(RuleOverride).filter(RuleOverride.reference_date < reference_date).all()

        msg = "Deleting {count} rule override entries..."
        self._logger.info(msg.format(count=len(result)))

        for override in result:
            session.delete(override)
