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

# Make a copy of this file named '.dev-senv-settings.sh'. It will be read by some of the scripts to set the
# environment settings relating to your development environment.

# Set the URL of the SonarQube instance
SONAR_HOST_URL=TODO

# Set the token provided by SonarQube
SONAR_LOGIN=TODO

# Set the project key provided by SonarQube
SONAR_PROJECT_KEY=TODO

# Set status server port used in tests
export STATUS_SERVER_PORT=5556

# Set the Prometheus port used in tests
export PROMETHEUS_SERVER_PORT=8890

# Use Selenium Chrome driver in tests
export SELENIUM_CHROME_DRIVER=1

# Activate extra output in CI scripts
export CI_DEBUG=1
