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

import locale

from little_brother import constants
from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn


class UserLocaleHandler(PersistenceDependencyInjectionMixIn):

    def get_user_locale(self, p_session_context, p_username):

        user = self.user_entity_manager.user_map(p_session_context).get(p_username)

        if user is not None and user.locale is not None:
            return user.locale

        default_locale = locale.getdefaultlocale()

        if default_locale is not None:
            # The first entry of the tuple is the language code
            # See https://docs.python.org/3.6/library/locale.html
            return default_locale[0]

        return constants.DEFAULT_LOCALE
