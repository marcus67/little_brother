# -*- coding: utf-8 -*-

#    Copyright (C) 2019-2021  Marcus Rickert
#
#    See https://github.com/marcus67/little_brother
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from little_brother import dependency_injection
from little_brother.persistence.base_entity_manager import BaseEntityManager
from little_brother.persistence.persistent_device_entity_manager import DeviceEntityManager
from little_brother.test.persistence.base_test_case_persistent_entity_manager import BaseTestCasePersistentEntityManager


class TestDeviceEntityManager(BaseTestCasePersistentEntityManager):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._entity_manager: BaseEntityManager = DeviceEntityManager()

    def setUp(self):
        dependency_injection.reset()
