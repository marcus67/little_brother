# -*- coding: utf-8 -*-
#    Copyright (C) 2021-2023  Marcus Rickert
#
#    See https://github.com/marcus67/python_base_app
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
from little_brother.test.persistence import test_persistence
from little_brother.token_handler import TokenHandler
from python_base_app.base_token_handler import BaseTokenHandlerConfigModel, BaseTokenHandler
from python_base_app.test.test_base_token_handler import TestBaseTokenHandler

SECRET_KEY = "SOME_SEC_RET"


class TestTokenHandler(TestBaseTokenHandler):

    def setUp(self):
        dependency_injection.reset()

    def getDefaultTokenHandler(self, p_max_token_age_in_days=365, p_token_life_in_minutes=60) -> BaseTokenHandler:
        test_persistence.TestPersistence.create_dummy_persistence(self._logger)
        token_handler_config = BaseTokenHandlerConfigModel()
        token_handler_config.token_life_in_minutes = p_token_life_in_minutes
        token_handler_config.max_token_age_in_days = p_max_token_age_in_days
        return TokenHandler(p_config=token_handler_config, p_secret_key=SECRET_KEY)
