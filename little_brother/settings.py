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

settings = {
    "name": "little-brother",
    "url": "https://github.com/marcus67/little_brother",
    "version": "0.4.11",
    "description": "Simple parental control application monitoring specific processes on Linux hosts "
                   "to monitor and limit the play time of (young) children.",
    "author": "Marcus Rickert",
    "author_email": "little-brother@web.de",
}

extended_settings = {
    "display_url": "github.com/marcus67/little_brother",
    "debian_package_revision": "110",
    "debian_package_architecture": "all",
    "babel_rel_directory": "translations",
    "analyze_extra_coverage_exclusions": "run_python_base_app_test_suite_no_venv.py",
}

RELEASE_BRANCH_NAME = "release"
MASTER_BRANCH_NAME = "master"

SOURCEFORGE_CHANNELS = [
    MASTER_BRANCH_NAME,
    RELEASE_BRANCH_NAME
]

DOCKER_CHANNELS = [
    MASTER_BRANCH_NAME,
    RELEASE_BRANCH_NAME
]
