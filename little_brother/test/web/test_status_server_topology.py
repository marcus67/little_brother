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
from little_brother.test.web.base_test_status_server import BaseTestStatusServer
from python_base_app.test import base_test


class TestStatusServerTopology(BaseTestStatusServer):

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_topology(self):
        self.create_dummy_status_server()
        self._status_server.start_server()

        self.create_selenium_driver()

        # When we load the admin page the first time...
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=constants.TOPOLOGY_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        # ...we end up on the login page.
        self.login()

        # After logging in we are on the users page
        xpath = "//DIV/DIV[DIV[1] = 'Node Type' and DIV[2] = 'Node Name']"
        assert "Topology" in self._driver.title
        self._driver.find_element_by_xpath(xpath)

        # The second time we call the users page.
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=constants.TOPOLOGY_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title
        assert "Topology" in self._driver.title

        # we are on the users page right away...
        xpath = "//DIV/DIV[DIV[1] = 'Node Type' and DIV[2] = 'Node Name']"
        self._driver.find_element_by_xpath(xpath)


if __name__ == "__main__":
    unittest.main()
