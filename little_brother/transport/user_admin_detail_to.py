# -*- coding: utf-8 -*-
# Copyright (C) 2019-24  Marcus Rickert
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

from little_brother.transport.rule_set_to import RuleSetTO


class UserAdminDetailTO:

    def __init__(self,
                 p_date_in_iso_8601: str,
                 p_long_format: str,
                 p_short_format: str,
                 p_rule_set: RuleSetTO,
                 p_override: RuleSetTO,
                 p_effective_rule_set: RuleSetTO):

        self.date_in_iso_8601 = p_date_in_iso_8601
        self.long_format = p_long_format
        self.short_format = p_short_format
        self.rule_set = p_rule_set
        self.override = p_override
        self.effective_rule_set = p_effective_rule_set
