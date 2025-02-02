#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    Copyright (C) 2019-2022  Marcus Rickert
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

from little_brother.test import test_app, test_client_info, test_pytest, test_token_handler
from little_brother.test import test_app_control
from little_brother.test import test_client_device_handler
from little_brother.test import test_client_process_handler
from little_brother.test import test_german_vacation_context_rule_handler
from little_brother.test import test_language
from little_brother.test import test_process_handler
from little_brother.test import test_process_handler_manager
from little_brother.test import test_process_info
from little_brother.test import test_process_statistics
from little_brother.test import test_prometheus
from little_brother.test import test_rule_handler
from little_brother.test import test_simple_weekday_context_rule_handler
from little_brother.test import test_user_status
from little_brother.test.api import test_suite as api_test_suite
from little_brother.test.persistence import test_suite as persistence_test_suite
from little_brother.test.web import test_suite as web_test_suite
from little_brother.test.web_angular import test_suite as web_angular_test_suite
from python_base_app import log_handling
from python_base_app.test import base_test


def add_test_cases(p_test_suite, p_config_filename=None):
    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_token_handler.TestTokenHandler, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_pytest.TestPytest, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_process_info.TestProcessInfo, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_process_statistics.TestProcessStatistics, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_client_process_handler.TestClientProcessHandler, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_client_device_handler.TestClientDeviceHandler, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_process_handler.TestProcessHandler, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_german_vacation_context_rule_handler.TestGermanVacationContextRuleHandler,
        p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_simple_weekday_context_rule_handler.TestWeekDayContextRuleHandler,
        p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_rule_handler.TestRuleHandler, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_rule_handler.TestRuleSetConfigModel, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_rule_handler.TestRulesectionHandler, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_rule_handler.TestRuleOverride, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_prometheus.TestPrometheus, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_app_control.TestAppControl, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_language.TestLanguage, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_app.TestApp, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_user_status.TestUserStatus, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_process_handler_manager.TestProcessHandlerManager, p_config_filename=p_config_filename)

    base_test.add_tests_in_test_unit(
        p_test_suite=p_test_suite,
        p_test_unit_class=test_client_info.TestClientInfo, p_config_filename=p_config_filename)



def main():
    log_handling.start_logging(p_use_filter=False)
    test_suite = unittest.TestSuite()
    add_test_cases(p_test_suite=test_suite, p_config_filename=base_test.get_config_filename())

    persistence_test_suite.add_test_cases(p_test_suite=test_suite, p_config_filename=base_test.get_config_filename())
    web_test_suite.add_test_cases(p_test_suite=test_suite, p_config_filename=base_test.get_config_filename())
    web_angular_test_suite.add_test_cases(p_test_suite=test_suite, p_config_filename=base_test.get_config_filename())
    api_test_suite.add_test_cases(p_test_suite=test_suite, p_config_filename=base_test.get_config_filename())

    base_test.run_test_suite(p_test_suite=test_suite)


if __name__ == '__main__':
    main()
