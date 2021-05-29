# -*- coding: utf-8 -*-

#    Copyright (C) 2019-21  Marcus Rickert
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
import re

from little_brother import login_mapping
from little_brother import process_info
from little_brother import rule_handler
from little_brother.persistence.persistent_user import User

USER_1 = "user1"
UID_1 = 123
PROCESS_NAME_1 = "process1"


def get_user_object_1():
    user = User()
    user.process_name_pattern = PROCESS_NAME_1
    user.prohibited_process_name_pattern = ""
    return user


def get_process_pattern_regex():
    return get_user_object_1().regex_process_name_pattern

def get_prohibited_process_pattern_regex():
    # todo: Write meaningful test case
    return get_user_object_1().regex_prohibited_process_name_pattern


PROCESS_PATH_1 = "/usr/bin/process1"
PID_1 = 12345

PROCESS_CMD_LINE_OPTION_1 = "Minecraft"
PROCESS_CMD_LINE_1 = ["/usr/bin/process1", PROCESS_CMD_LINE_OPTION_1]


def get_user_object_2():
    user = User()
    user.process_name_pattern = PROCESS_CMD_LINE_OPTION_1
    return user


def get_cmd_line_option_regex():
    return get_user_object_2().regex_process_name_pattern


def get_user_object_3():
    user = User()
    user.process_name_pattern = "bin"
    return user


def get_cmd_line_option_regex_part_of_path():
    return get_user_object_3().regex_process_name_pattern


HOSTNAME_1 = "host1"

START_TIME_1 = datetime.datetime(2018, 1, 1, 10, 10, 10)
END_TIME_1 = datetime.datetime(2018, 1, 1, 10, 10, 20)

MAX_TIME_PER_DAY_1 = 3600
MAX_TIME_PER_DAY_2 = 7200
MIN_TIME_OF_DAY_1 = datetime.time(hour=10)
MAX_TIME_OF_DAY_1 = datetime.time(hour=22)

MIN_BREAK_1 = 1800
FREEPLAY_1 = True

LOGIN_MAPPING = login_mapping.LoginMapping(p_default_server_group=login_mapping.DEFAULT_SERVER_GROUP)
LOGIN_UID_MAPPING_ENTRY = p_login_uid_mapping_entry = login_mapping.LoginUidMappingEntry(USER_1, UID_1)
LOGIN_MAPPING.add_entry(p_server_group=login_mapping.DEFAULT_SERVER_GROUP,
                        p_login_uid_mapping_entry=LOGIN_UID_MAPPING_ENTRY)


def get_process_regex_map_1():
    return {USER_1: get_process_pattern_regex()}

def get_prohibited_process_regex_map_1():
    return {USER_1: get_prohibited_process_pattern_regex()}


def get_process_path_regex_map_1():
    return {USER_1: re.compile(PROCESS_PATH_1)}


def get_process_cmd_line_option_regex_map_1():
    return {USER_1: get_cmd_line_option_regex()}


def get_process_cmd_line_option_part_of_path_regex_map_1():
    return {USER_1: get_cmd_line_option_regex_part_of_path()}


PINFO_1 = process_info.ProcessInfo(p_username=USER_1, p_processname=PROCESS_NAME_1,
                                   p_pid=PID_1, p_start_time=START_TIME_1)
PINFO_PATH_1 = process_info.ProcessInfo(p_username=USER_1, p_processname=PROCESS_PATH_1,
                                        p_pid=PID_1, p_start_time=START_TIME_1)
PINFO_CMD_LINE_1 = process_info.ProcessInfo(p_username=USER_1, p_processname=PROCESS_PATH_1,
                                            p_pid=PID_1, p_start_time=START_TIME_1,
                                            p_cmd_line=PROCESS_CMD_LINE_1)
PINFO_2 = process_info.ProcessInfo(p_username=USER_1, p_processname=PROCESS_NAME_1,
                                   p_pid=PID_1, p_start_time=START_TIME_1, p_end_time=END_TIME_1)

START_TIME_NOW = datetime.datetime.utcnow()
END_TIME_NOW = START_TIME_NOW + datetime.timedelta(minutes=5)

PINFO_3 = process_info.ProcessInfo(p_username=USER_1, p_processname=PROCESS_NAME_1,
                                   p_pid=PID_1, p_start_time=START_TIME_NOW, p_end_time=END_TIME_NOW)

RULESET_CONFIG_USER1_NO_RESTRICTIONS = rule_handler.RuleSetConfigModel()
RULESET_CONFIG_USER1_NO_RESTRICTIONS.username = USER_1
RULESET_CONFIG_USER1_NO_RESTRICTIONS.process_name_pattern = PROCESS_NAME_1

RULESET_CONFIGS_USER1_NO_RESTRICTIONS = [RULESET_CONFIG_USER1_NO_RESTRICTIONS]

RULESET_CONFIG_USER1_ALL_RESTRICTIONS = rule_handler.RuleSetConfigModel()
RULESET_CONFIG_USER1_ALL_RESTRICTIONS.username = USER_1
RULESET_CONFIG_USER1_ALL_RESTRICTIONS.process_name_pattern = PROCESS_NAME_1
RULESET_CONFIG_USER1_ALL_RESTRICTIONS.min_time_of_day = "00:00"
RULESET_CONFIG_USER1_ALL_RESTRICTIONS.max_time_of_day = "00:01"
RULESET_CONFIG_USER1_ALL_RESTRICTIONS.max_activity_duration = "0s"
RULESET_CONFIG_USER1_ALL_RESTRICTIONS.min_break = "5m"
RULESET_CONFIG_USER1_ALL_RESTRICTIONS.max_time_per_day = "0s"
RULESET_CONFIG_USER1_ALL_RESTRICTIONS.post_process()

RULESET_CONFIGS_USER1_ALL_RESTRICTIONS = [RULESET_CONFIG_USER1_ALL_RESTRICTIONS]

PROCESSES_1 = [
    PINFO_1
]

PROCESSES_PATH_1 = [
    PINFO_PATH_1
]

PROCESSES_CMD_LINE_1 = [
    PINFO_CMD_LINE_1
]

PROCESSES_2 = [
    PINFO_2
]

PROCESSES_3 = [
    PINFO_3
]


def get_process_dict(p_processes):
    return {process.get_key(): process for process in p_processes}


def get_active_processes(p_start_time, p_end_time=None):
    return [
        process_info.ProcessInfo(p_username=USER_1, p_processname=PROCESS_NAME_1,
                                 p_pid=PID_1, p_start_time=p_start_time, p_end_time=p_end_time)
    ]


def get_dummy_ruleset_configs(p_ruleset_config):
    return {
        USER_1: p_ruleset_config
    }
