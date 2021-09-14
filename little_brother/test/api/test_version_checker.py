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

from little_brother import settings
from little_brother.api.version_checker import VersionCheckerConfigModel, VersionChecker, SOURCEFORGE_CHANNEL_INFOS
from python_base_app.test import base_test

HOSTNAME = "some.host"


class TestVersionChecker(base_test.BaseTestCase):

    def test_constructor(self):
        config = VersionCheckerConfigModel()
        checker = VersionChecker(p_channel_infos=SOURCEFORGE_CHANNEL_INFOS, p_config=config)
        self.assertIsNotNone(checker)

    def test_deactivated_checker(self):
        config = VersionCheckerConfigModel()
        config.check_interval_in_days = 0
        checker = VersionChecker(p_channel_infos=SOURCEFORGE_CHANNEL_INFOS, p_config=config)

        self.assertIsNone(checker.version_infos)
        self.assertIsNone(checker.is_revision_current(p_channel=settings.MASTER_BRANCH_NAME, p_revision=123))

    def test_get_version_infos(self):
        config = VersionCheckerConfigModel()
        checker = VersionChecker(p_channel_infos=SOURCEFORGE_CHANNEL_INFOS, p_config=config)

        version_infos = checker.version_infos

        for channel in SOURCEFORGE_CHANNEL_INFOS.keys():
            self.assertIn(channel, version_infos)

            suggested_version_info = checker.is_revision_current(p_channel=channel, p_revision=1)
            self.assertIsNotNone(suggested_version_info)
            self.assertEqual(suggested_version_info.revision, version_infos[channel].revision)

            suggested_version_info = checker.is_revision_current(p_channel=channel,
                                                                 p_revision=version_infos[channel].revision)
            self.assertIsNone(suggested_version_info)


if __name__ == "__main__":
    unittest.main()
