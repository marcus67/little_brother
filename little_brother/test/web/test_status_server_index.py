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
from little_brother.test import test_data
from little_brother.test.web.base_test_status_server import BaseTestStatusServer
from python_base_app.test import base_test


class TestStatusServerIndex(BaseTestStatusServer):

    def check_index_page_visible(self):
        xpath = "//DIV[DIV[1] = 'User' and DIV[2] = 'Context' and DIV[12] = 'Reasons']"
        self._driver.find_element_by_xpath(xpath)

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_index_with_process_no_restrictions(self):
        ruleset_configs = test_data.get_dummy_ruleset_configs(
            p_ruleset_config=test_data.RULESET_CONFIGS_USER1_NO_RESTRICTIONS)
        self.create_status_server_using_ruleset_configs(ruleset_configs)

        self.create_selenium_driver()

        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=constants.STATUS_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        self.check_index_page_visible()

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_index_with_process_all_restrictions(self):
        ruleset_configs = test_data.get_dummy_ruleset_configs(
            p_ruleset_config=test_data.RULESET_CONFIGS_USER1_ALL_RESTRICTIONS)
        self.create_status_server_using_ruleset_configs(ruleset_configs)

        self.create_selenium_driver()

        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=constants.STATUS_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        self.check_index_page_visible()

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_index_without_process(self):
        self.create_dummy_status_server()
        self._status_server.start_server()

        self.create_selenium_driver()

        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=constants.STATUS_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title

        self.check_index_page_visible()


if __name__ == "__main__":
    unittest.main()
