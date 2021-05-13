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

class SessionContext(object):
    _session_registry = []

    def __init__(self, p_persistence, p_register=False):

        self._persistence = p_persistence
        self._session = None
        self._caches = {}

        if p_register:
            SessionContext._session_registry.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_session()

        if exc_val is not None:
            return False

        return True

    def get_cache(self, p_name):

        # result =
        # print(str(self) + " get_cache " + p_name + " " + str(result if result is not None else "NONE"))
        return self._caches.get(p_name)

    def clear_cache(self):

        # print(str(self) + "clear_cache " + str(self._caches))

        #        if self._session is not None:
        #            self._session.close()
        #            self._session = None

        self._caches = {}

    def get_session(self):

        if self._session is None:
            self._session = self._persistence.get_session()

        return self._session

    def close_session(self):
        if self._session is not None:
            self._session.close()
            self._session = None

    def set_cache(self, p_name, p_object):

        # print(str(self) + " set_cache " + p_name + " " + str(p_object))

        if self._persistence.enable_caching():
            self._caches[p_name] = p_object

    @classmethod
    def clear_caches(cls):

        for context in cls._session_registry:
            context.clear_cache()
