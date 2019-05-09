# -*- coding: utf-8 -*-

#    Copyright (C) 2019  Marcus Rickert
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

import datetime
import unittest

import little_brother.process_info as process_info
from python_base_app.test import base_test

HOSTNAME = "hostname"
USERNAME = "username"
PROCESS_NAME = "processname"
PID = 123


class TestProcessInfo(base_test.BaseTestCase):

    def test_constructor(self):
        some_process_handler = object()
        some_start_time = datetime.datetime.now()
        some_end_time = some_start_time + datetime.timedelta(seconds=5)

        pi = process_info.ProcessInfo(p_hostname=HOSTNAME, p_username=USERNAME, p_processhandler=some_process_handler,
                                      p_processname=PROCESS_NAME, p_pid=PID, p_start_time=some_start_time,
                                      p_end_time=some_end_time)

        self.assertEqual(pi.hostname, HOSTNAME)


if __name__ == "__main__":
    unittest.main()
