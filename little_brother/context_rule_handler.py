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

from little_brother import dependency_injection
from python_base_app.locale_helper import LocaleHelper

_ = lambda x:x

class RuleHandlerRunTimeException(RuntimeError):
    pass

class AbstractContextRuleHandler(object, metaclass=abc.ABCMeta):

    def __init__(self, p_context_name, p_locale_helper=None):

        self._context_name = p_context_name
        self._locale_helper = p_locale_helper

    @property
    def locale_helper(self) -> LocaleHelper:

        if self._locale_helper is None:
            self._locale_helper = dependency_injection.container[LocaleHelper]

        return self._locale_helper

    @abc.abstractmethod
    def is_active(self, p_reference_date, p_details):
        pass

    def get_configuration_section_handler(self):
        return None

    @property
    def context_name(self):
        return self._context_name

    def get_choices(self):
        return []

    def validate_context_details(self, p_context_detail):
        pass # default action: none

    def summary(self, p_context_detail):
        if p_context_detail is not None and p_context_detail != "":
            return [_("Details"), ": ", p_context_detail]

        else:
            return []

    def check_data(self):
        pass # default action: none
