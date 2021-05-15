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

import os
import sys
import unittest

from little_brother import dependency_injection
from little_brother.app import App, ProcessIteratorFactory, APP_NAME, get_argument_parser
from little_brother.master_connector import MasterConnector
from little_brother.test.persistence.test_persistence import TestPersistence
from little_brother.web import web_server
from python_base_app.configuration import Configuration
from python_base_app.test import base_test


class TestApp(base_test.BaseTestCase):

    def setUp(self):
        dependency_injection.reset()

    @classmethod
    def get_default_sys_args(cls):
        return [
            '--create-databases',
            '--config', 'little_brother/test/resources/app.config',

        ]

    def test_constructor(self):
        TestPersistence.create_dummy_persistence(self._logger)
        dependency_injection.container[MasterConnector] = None

        app = App(p_pid_file="/tmp/pid", p_app_name=APP_NAME, p_arguments=sys.argv)

        self.assertIsNotNone(app)

    def test_class_process_iterator_factory(self):
        f = ProcessIteratorFactory.process_iter()

        self.assertIsNotNone(f)

    def test_prepare_configuration(self):
        parser = get_argument_parser(p_app_name=APP_NAME)
        arguments = parser.parse_args([])

        app = App(p_pid_file="/tmp/pid", p_app_name=APP_NAME, p_arguments=arguments)

        configuration = Configuration()

        config = app.prepare_configuration(configuration)

        self.assertIsNotNone(config)

        self.assertEqual(13, len(configuration._sections))

    @classmethod
    def create_dummy_app(cls):

        parser = get_argument_parser(p_app_name=APP_NAME)
        arguments = parser.parse_args(cls.get_default_sys_args())

        app = App(p_pid_file="/tmp/pid", p_app_name=APP_NAME, p_arguments=arguments)

        app.load_configuration()

        web_server_config = app._config[web_server.SECTION_NAME]

        web_server_config.port = int(os.getenv("STATUS_SERVER_PORT", "5555"))

        return app

    @classmethod
    def start_dummy_app(cls, p_app: App):

        p_app.run_special_commands(p_arguments=p_app._arguments)
        p_app.prepare_services()
        p_app.start_services()

        p_app._persistence.check_schema(p_create_tables=True)


    def test_check_migrations(self):

        app = self.create_dummy_app()
        self.start_dummy_app(p_app=app)

        #app.check_migrations()
        app.stop_services()


if __name__ == "__main__":
    unittest.main()
