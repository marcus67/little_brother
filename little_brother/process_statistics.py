# -*- coding: utf-8 -*-

# Copyright (C) 2019  Marcus Rickert
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

from python_base_app import log_handling
from python_base_app import tools


class Activity(object):

    def __init__(self, p_start_time=None):

        self.host_process_counts = {}
        self.start_time = p_start_time
        self.end_time = None
        self.downtime = 0

    def add_host_process(self, p_hostname):

        process_count = self.host_process_counts.get(p_hostname)

        if process_count is None:
            process_count = 0

        process_count = process_count + 1
        self.host_process_counts[p_hostname] = process_count


    def set_end_time(self, p_end_time):

        self.end_time = p_end_time


    def set_downtime(self, p_downtime):

        if p_downtime > self.downtime:
            self.downtime = p_downtime


    @property
    def duration(self, p_reference_time=None):

        if self.end_time is not None and self.start_time is not None:
            return max((self.end_time - self.start_time).total_seconds() - self.downtime, 0)

        else:
            return None

    def current_duration(self, p_reference_time):

        return max((p_reference_time - self.start_time).total_seconds() -self.downtime, 0)

    def __str__(self):

        fmt = "Activity([{start_time}, {end_time}], {duration}, downtime={downtime})"
        return  fmt.format(start_time=tools.get_timestamp_as_string(self.start_time),
                           end_time=tools.get_timestamp_as_string(self.end_time),
                           duration=tools.get_duration_as_string(self.duration),
                           downtime=tools.get_duration_as_string(self.downtime))

    @property
    def host_infos(self):

        return ", ".join(
            "%s(%d)" % (hostname, process_count) for hostname, process_count in self.host_process_counts.items())


class DayStatistics(object):

    def __init__(self):

        self.activities = []
        self.min_time = None
        self.max_time = None
        self.host_process_counts = {}

    def add_activity(self, p_activity):

        self.activities.append(p_activity)

        for hostname, new_count in p_activity.host_process_counts.items():
            count = self.host_process_counts.get(hostname)

            if count is None:
                count = 0

            count = count + new_count
            self.host_process_counts[hostname] = count

        if self.min_time is None or p_activity.start_time < self.min_time:
            self.min_time = p_activity.start_time

        if p_activity.end_time is not None:
            if self.max_time is None or p_activity.end_time > self.max_time:
                self.max_time = p_activity.end_time

    @property
    def duration(self):

        seconds = 0

        for activity in self.activities:
            secs = activity.duration

            if secs is not None:
                seconds = seconds + secs

        return seconds

    @property
    def downtime(self):

        seconds = 0

        for activity in self.activities:
            secs = activity.downtime

            if secs is not None:
                seconds = seconds + secs

        return seconds

    @property
    def host_infos(self):

        return ", ".join(
            "%s(%d)" % (hostname, process_count) for hostname, process_count in self.host_process_counts.items())


class ProcessStatisticsInfo(object):

    def __init__(self, p_username, p_reference_time, p_max_lookback_in_days, p_min_activity_duration):

        self._logger = log_handling.get_logger(self.__class__.__name__)

        self.username = p_username
        self.reference_time = p_reference_time
        self.reference_date = p_reference_time.date()
        self.max_lookback_in_days = p_max_lookback_in_days
        self.min_activity_duration = p_min_activity_duration

        self.active_processes = 0

        self.last_inactivity_start_time = None
        self.current_activity = None
        self.previous_activity = None

        self.accumulated_break_time = 0

        self.day_statistics = [DayStatistics() for _i in range(0, p_max_lookback_in_days + 1)]
        self.currently_active_host_processes = {}

    def add_process_start(self, p_process_info, p_start_time):

        if self.active_processes == 0:
            self.current_activity = Activity(p_start_time=p_start_time)

        self.current_activity.add_host_process(p_process_info.hostname)
        self.current_activity.set_downtime(p_downtime=p_process_info.downtime)
        self.active_processes = self.active_processes + 1

    def add_process_end(self, p_process_info, p_end_time):

        # if the process is still running we store it as a candidate to be killed if required
        if p_process_info.end_time is None:
            process_list = self.currently_active_host_processes.get(p_process_info.hostname)

            if process_list is None:
                process_list = []
                self.currently_active_host_processes[p_process_info.hostname] = process_list

            process_list.append((p_process_info.processhandler, p_process_info.pid, p_process_info.start_time))

        if self.active_processes == 0:
            fmt = "Active processes smaller than zero"
            self._logger.warning(fmt)
            return

        self.active_processes = self.active_processes - 1

        login_date = self.current_activity.start_time.date()
        lookback = int((self.reference_date - login_date).total_seconds() / (24 * 3600))

        if self.active_processes == 0:
            if p_process_info.end_time is not None:
                self.current_activity.set_end_time(p_end_time=p_end_time)
                self.current_activity.set_downtime(p_downtime=p_process_info.downtime)

                if lookback <= self.max_lookback_in_days:
                    self.day_statistics[lookback].add_activity(self.current_activity)

                if self.current_activity.duration > self.min_activity_duration:
                    self.last_inactivity_start_time = p_end_time
                    self.previous_activity = self.current_activity

                self.current_activity = None

    @property
    def current_activity_start_time(self):

        if self.current_activity is None:
            return None

        else:
            return self.current_activity.start_time

    @property
    def previous_activity_start_time(self):

        if self.previous_activity is None:
            return None

        else:
            return self.previous_activity.start_time

    @property
    def previous_activity_end_time(self):

        if self.previous_activity is None:
            return None

        else:
            return self.previous_activity.end_time

    @property
    def previous_activity_duration(self):

        if self.previous_activity is None:
            return None

        else:
            return self.previous_activity.duration

    @property
    def todays_activity_duration(self):

        duration = self.day_statistics[0].duration

        active_duration = self.current_activity_duration

        if active_duration is not None:
            duration = duration + active_duration

        return duration

    @property
    def todays_downtime(self):

        downtime = self.day_statistics[0].downtime

        active_downtime = self.current_activity_downtime

        if active_downtime is not None:
            downtime = downtime + active_downtime

        return downtime

    @property
    def seconds_since_last_activity(self):

        if self.last_inactivity_start_time is not None:
            return (self.reference_time - self.last_inactivity_start_time).total_seconds()

        if self.active_processes > 0:
            return 0

        return None

    @property
    def current_activity_duration(self):

        if self.current_activity is None:
            return None

        else:
            return self.current_activity.current_duration(p_reference_time=self.reference_time)

    @property
    def current_activity_downtime(self):

        if self.current_activity is None:
            return None

        else:
            return self.current_activity.downtime

    # @property
    # def seconds_in_last_activity(self):
    #
    #     return self.last_activity.duration

    def __str__(self):

        return "StatInfo (user=%s, today:%d[s], yesterday:%d[s], ref-time:%s, previous %s, "\
               "current %s, secs-since-last-activity:%s)" % (
                    self.username,
                    self.day_statistics[0].duration,
                    self.day_statistics[1].duration,
                    tools.get_timestamp_as_string(p_timestamp=self.reference_time),
                    str(self.previous_activity) if self.previous_activity is not None else "---",
                    str(self.current_activity) if self.current_activity is not None else "---",
                    tools.get_duration_as_string(p_seconds=self.seconds_since_last_activity)
                )


def get_empty_stat_infos(
        p_rule_set_configs,
        p_reference_time,
        p_max_lookback_in_days,
        p_min_activity_duration):
    stat_infos = {}

    for username, rulesets in p_rule_set_configs.items():
        user_stat_infos = {}

        for ruleset in rulesets:
            stat_info = ProcessStatisticsInfo(
                p_username=username,
                p_reference_time=p_reference_time,
                p_max_lookback_in_days=p_max_lookback_in_days,
                p_min_activity_duration=p_min_activity_duration)
            user_stat_infos[ruleset.context] = stat_info

        stat_infos[username] = user_stat_infos

    return stat_infos


def get_process_statistics(
        p_rule_set_configs,
        p_process_infos,
        p_reference_time,
        p_max_lookback_in_days,
        p_min_activity_duration):

    users_stat_infos = get_empty_stat_infos(
        p_rule_set_configs=p_rule_set_configs,
        p_reference_time=p_reference_time,
        p_max_lookback_in_days=p_max_lookback_in_days,
        p_min_activity_duration=p_min_activity_duration)

    process_info_boundaries = [(pinfo.start_time, pinfo.get_key(), pinfo, "START") for pinfo in
                               p_process_infos.values()]
    process_info_boundaries.extend(
        [(pinfo.end_time, pinfo.get_key(), pinfo, "END") for pinfo in p_process_infos.values() if
         pinfo.end_time is not None])
    sorted_process_info_boundaries = sorted(process_info_boundaries)

    if len(sorted_process_info_boundaries) > 0:
        maximum_boundary_time = sorted_process_info_boundaries[-1][0]

        if p_reference_time > maximum_boundary_time:
            maximum_boundary_time = p_reference_time

        sorted_process_info_boundaries.extend([(maximum_boundary_time, pinfo.get_key(), pinfo, "END")
                                               for pinfo in p_process_infos.values() if pinfo.end_time is None])

        for (boundary_time, _key, pinfo, boundary_type) in sorted_process_info_boundaries:
            user_stat_infos = users_stat_infos.get(pinfo.username)

            if user_stat_infos is None:
                user_stat_infos = {}
                users_stat_infos[pinfo.username] = user_stat_infos

            if pinfo.username in p_rule_set_configs:
                for ruleset in p_rule_set_configs[pinfo.username]:

                    if ((pinfo.processname is None and ruleset.scan_devices) or
                            (pinfo.processname is not None and ruleset.regex_process_name_pattern.match(
                                pinfo.processname))):
                        stat_info = user_stat_infos.get(ruleset.context)

                        if boundary_type == "START":
                            stat_info.add_process_start(p_process_info=pinfo, p_start_time=boundary_time)

                        else:
                            stat_info.add_process_end(p_process_info=pinfo, p_end_time=boundary_time)

    # Add statistics entries for current entries
    for user_stat_infos in users_stat_infos.values():
        for user_stat_info in user_stat_infos.values():
            if user_stat_info.current_activity is not None:
                login_date = user_stat_info.current_activity.start_time.date()
                lookback = int((user_stat_info.reference_date - login_date).total_seconds() / (24 * 3600))
                user_stat_info.day_statistics[lookback].add_activity(user_stat_info.current_activity)

    return users_stat_infos
