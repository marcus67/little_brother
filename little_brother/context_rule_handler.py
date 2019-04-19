# -*- coding: utf-8 -*-

# Copyright (C) 2019  Marcus Rickert
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

import abc

class AbstractContextRuleHandler(object, metaclass=abc.ABCMeta):

    def __init__(self, p_context_name):

        self._context_name = p_context_name

    @abc.abstractmethod
    def is_active(self, p_reference_date, p_details):
        pass

    def get_configuration_section_handler(self):
        return None

    @property
    def context_name(self):
        return self._context_name

    def check_data(self):
        pass
