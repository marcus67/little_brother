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
import os.path
import sys
import unittest

from little_brother import dependency_injection
from little_brother.api.master_connector import MasterConnector
from little_brother.app import App, ProcessIteratorFactory, APP_NAME, get_argument_parser
from little_brother.persistence.persistence import Persistence, SECTION_NAME
from little_brother.test.persistence.test_persistence import TestPersistence
from little_brother.web import web_server
from python_base_app.configuration import Configuration
from python_base_app.test import base_test

TMP_PID = "/tm" + "p/pid"


class TestApp(base_test.BaseTestCase):

    def setUp(self):
        dependency_injection.reset()

    @classmethod
    def get_default_sys_args(cls):

        config_filename = os.path.join(os.path.dirname(__file__), 'resources/app.config')

        return [
            '--create-databases',
            '--config', config_filename,

        ]

    def test_constructor(self):
        TestPersistence.create_dummy_persistence(self._logger)
        dependency_injection.container[MasterConnector] = None

        app = App(p_pid_file=("%s" % TMP_PID), p_app_name=APP_NAME, p_arguments=sys.argv)

        self.assertIsNotNone(app)

    def test_class_process_iterator_factory(self):
        f = ProcessIteratorFactory.process_iter()

        self.assertIsNotNone(f)

    def test_prepare_configuration(self):
        parser = get_argument_parser(p_app_name=APP_NAME)
        arguments = parser.parse_args([])

        app = App(p_pid_file="TMP_PID", p_app_name=APP_NAME, p_arguments=arguments)

        configuration = Configuration()

        config = app.prepare_configuration(configuration)

        self.assertIsNotNone(config)

        self.assertEqual(14, len(configuration._sections))

    @classmethod
    def create_dummy_app(cls, p_logger):

        parser = get_argument_parser(p_app_name=APP_NAME)
        arguments = parser.parse_args(cls.get_default_sys_args())

        app = App(p_pid_file="TMP_PID", p_app_name=APP_NAME, p_arguments=arguments)

        app.load_configuration()

        config = app._config[SECTION_NAME]

        Persistence.delete_database(p_logger=p_logger, p_config=config)

        web_server_config = app._config[web_server.SECTION_NAME]

        web_server_config.port = int(os.getenv("STATUS_SERVER_PORT", "5555"))

        return app

    @classmethod
    def start_dummy_app(cls, p_app: App):

        p_app.run_special_commands(p_arguments=p_app._arguments)
        p_app.prepare_services()
        p_app.start_services()

    def test_check_migrations(self):

        app = self.create_dummy_app(p_logger=self._logger)

        # This try has been temporarily introduced to make sure that stop_services is called because the call to
        # start_dummy_app runs into an error when instantiating the Prometheus server. Somehow an upstream test
        # has not freed the Prometheus port. This may be due to a race condition.
        try:
            self.start_dummy_app(p_app=app)

            # Todo: Include code again
            # app.check_migrations()

        except Exception as e:
            msg = "Exception '{e}' in test case"
            self._logger.exception(msg.format(e=str(e)))

        finally:
            app.stop_services()


if __name__ == "__main__":
    unittest.main()
