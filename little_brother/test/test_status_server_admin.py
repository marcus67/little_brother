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

import unittest

from little_brother import constants
from little_brother import status_server
from little_brother.test import test_data
from little_brother.test.base_test_status_server import BaseTestStatusServer
from python_base_app.test import base_test


class TestStatusServerAdmin(BaseTestStatusServer):

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_admin_without_process(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        # When we load the admin page the first time...
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=status_server.ADMIN_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        # ...we end up on the login page.
        self.login()

        # The second time we call the admin page.
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=status_server.ADMIN_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title
        assert "Administration" in self._driver.title

        # we are on the admin page right away...
        self.check_empty_user_list()

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_admin_with_process(self):
        ruleset_configs = test_data.get_dummy_ruleset_configs(
            p_ruleset_config=test_data.RULESET_CONFIGS_USER1_ALL_RESTRICTIONS)
        self.create_status_server_using_ruleset_configs(ruleset_configs)

        self.create_selenium_driver()

        # When we load the admin page the first time...
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=status_server.ADMIN_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        # ...we end up on the login page.
        self.login()

        # The second we call the admin page.
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=status_server.ADMIN_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        # we are on the admin page right away...
        self.check_empty_user_list()


if __name__ == "__main__":
    unittest.main()
