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
from little_brother import settings
from little_brother.test.web.base_test_status_server import BaseTestStatusServer
from python_base_app.test import base_test


class TestStatusServerAbout(BaseTestStatusServer):

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_about(self):
        self.create_dummy_status_server()
        self._status_server.start_server()

        self.create_selenium_driver()
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=constants.ABOUT_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title
        assert "About" in self._driver.title

        xpath = "//DIV[DIV[1] = 'Version' and DIV[2] = '{version}']"
        self._driver.find_element_by_xpath(xpath.format(version=settings.settings['version']))

        xpath = "//DIV[DIV[1] = 'Debian Package Revision' and DIV[2] = '{debian_package_revision}']"
        self._driver.find_element_by_xpath(
            xpath.format(debian_package_revision=settings.extended_settings['debian_package_revision']))


if __name__ == "__main__":
    unittest.main()
