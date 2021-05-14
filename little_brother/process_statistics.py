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


class HostStat(object):

    def __init__(self, p_hostname, p_percent, p_count=1):

        self._hostname = p_hostname
        self._count = p_count
        self._percent = p_percent

    def add_occurence(self, p_percent, p_count=0):

        self._count += p_count

        if p_percent > self._percent:
            self._percent = p_percent

    @property
    def hostname(self):

        return self._hostname

    @property
    def percent(self):

        return self._percent

    @property
    def count(self):

        return self._count

    @property
    def summary(self):

        if self._percent == 100:
            return "{name}({count})".format(name=self._hostname, count=self._count)

        else:
            return "{name}({count}, {percent}%)".format(name=self._hostname, count=self._count, percent=self._percent)


class Activity(object):

    def __init__(self, p_start_time=None):

        self.host_stats = {}
        self.start_time = p_start_time
        self.end_time = None
        self.downtime = 0

    @property
    def percent(self):

        if len(self.host_stats) == 0:
            return 100

        max_host_stat = max(self.host_stats.values(), key=lambda host_stat: host_stat.percent)
        return max_host_stat.percent

    def add_host_process(self, p_hostname, p_percent=100):

        host_stat : HostStat = self.host_stats.get(p_hostname)

        if host_stat is None:
            host_stat = HostStat(p_hostname=p_hostname, p_percent=p_percent)
            self.host_stats[p_hostname] = host_stat

        else:
            host_stat.add_occurence(p_percent=p_percent)

    def set_end_time(self, p_end_time):

        self.end_time = p_end_time

    def set_downtime(self, p_downtime):

        if p_downtime > self.downtime:
            self.downtime = p_downtime

    @property
    def duration(self):

        if self.end_time is not None and self.start_time is not None:
            return max((self.end_time - self.start_time).total_seconds() * self.percent / 100 - self.downtime, 0)

        else:
            return None

    def current_duration(self, p_reference_time):

        return max((p_reference_time - self.start_time).total_seconds() * self.percent / 100 - self.downtime, 0)

    def __str__(self):

        fmt = "Activity([{start_time}, {end_time}], {duration}, downtime={downtime})"
        return fmt.format(start_time=tools.get_timestamp_as_string(self.start_time),
                          end_time=tools.get_timestamp_as_string(self.end_time),
                          duration=tools.get_duration_as_string(self.duration),
                          downtime=tools.get_duration_as_string(self.downtime))

    @property
    def host_infos(self):

        return ", ".join(host_stat.summary for host_stat in self.host_stats.values())


class DayStatistics(object):

    def __init__(self):

        self.activities = []
        self.min_time = None
        self.max_time = None
        self.host_stats = {}

    def add_activity(self, p_activity):

        self.activities.append(p_activity)

        for host_stat in p_activity.host_stats.values():
            day_host_stat = self.host_stats.get(host_stat.hostname)

            if day_host_stat is None:
                day_host_stat = HostStat(p_hostname=host_stat.hostname, p_count=host_stat.count,
                                         p_percent=host_stat.percent)
                self.host_stats[host_stat.hostname] = day_host_stat

            else:
                day_host_stat.add_occurence(p_count=host_stat.count,
                                            p_percent=host_stat.percent)

        if self.min_time is None or p_activity.start_time < self.min_time:
            self.min_time = p_activity.start_time

        if p_activity.end_time is not None and \
                (self.max_time is None or p_activity.end_time > self.max_time):
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

        return ", ".join(host_stat.summary for host_stat in self.host_stats.values())


class ProcessStatisticsInfo(object):

    def __init__(self, p_username, p_reference_time, p_max_lookback_in_days, p_min_activity_duration,
                 p_notification_name=None, p_full_name=None):

        self._logger = log_handling.get_logger(self.__class__.__name__)

        self.username = p_username
        self.notification_name = p_notification_name if p_notification_name is not None else self.username
        self.full_name = p_full_name if p_full_name is not None else self.username
        self.reference_time = p_reference_time
        self.reference_date = p_reference_time.date()
        self.max_lookback_in_days = p_max_lookback_in_days
        self.min_activity_duration = p_min_activity_duration

        self.active_processes = 0

        self.last_inactivity_start_time = None
        self.current_activity = None
        self.previous_activity = None

        self.accumulated_break_time = 0
        self.has_downtime = False

        self.day_statistics = [DayStatistics() for _i in range(0, p_max_lookback_in_days + 1)]
        self.currently_active_host_processes = {}

    def add_process_start(self, p_process_info, p_start_time):

        if self.active_processes == 0:
            self.current_activity = Activity(p_start_time=p_start_time)

        self.current_activity.add_host_process(p_process_info.hostlabel, p_percent=p_process_info.percent)
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
            fmt = "Active processes less than zero"
            self._logger.warning(fmt)
            return

        self.active_processes = self.active_processes - 1

        if self.active_processes == 0 and p_process_info.end_time is not None:
            self.current_activity.set_end_time(p_end_time=p_end_time)
            self.current_activity.set_downtime(p_downtime=p_process_info.downtime)

            login_date = self.current_activity.start_time.date()
            lookback = int((self.reference_date - login_date).total_seconds() / (24 * 3600))

            if self.current_activity.duration > self.min_activity_duration:
                if lookback <= self.max_lookback_in_days:
                    self.day_statistics[lookback].add_activity(self.current_activity)

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

        # TODO: downtime counted twice!
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

    def __str__(self):

        return "StatInfo (user=%s, today:%d[s], yesterday:%d[s], ref-time:%s, previous %s, " \
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
        p_user_map,
        p_reference_time,
        p_max_lookback_in_days,
        p_min_activity_duration):
    stat_infos = {}

    for user in p_user_map.values():
        user_stat_infos = {}

        for ruleset in user.rulesets:
            stat_info = ProcessStatisticsInfo(
                p_username=user.username,
                p_notification_name=user.notification_name,
                p_full_name=user.full_name,
                p_reference_time=p_reference_time,
                p_max_lookback_in_days=p_max_lookback_in_days,
                p_min_activity_duration=p_min_activity_duration)
            user_stat_infos[ruleset.context] = stat_info

        stat_infos[user.username] = user_stat_infos

    return stat_infos


def get_process_statistics(
        p_user_map,
        p_process_infos,
        p_reference_time,
        p_max_lookback_in_days,
        p_min_activity_duration):
    users_stat_infos = get_empty_stat_infos(
        p_user_map=p_user_map,
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

            if pinfo.username in p_user_map:
                user = p_user_map[pinfo.username]
                for ruleset in user.rulesets:

                    if (pinfo.processname is None or
                            (pinfo.processname is not None and user.regex_process_name_pattern.match(
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

                # If there's an actity more than lookback days back enlarge the stat array accordingly...
                if lookback >= len(user_stat_info.day_statistics):
                    for i in range(len(user_stat_info.day_statistics), lookback + 1):
                        user_stat_info.day_statistics.append(DayStatistics())

                user_stat_info.day_statistics[lookback].add_activity(user_stat_info.current_activity)

            user_stat_info.has_downtime = False

            for i in range(p_max_lookback_in_days):
                if user_stat_info.day_statistics[i].downtime:
                    user_stat_info.has_downtime = True
                    break

    return users_stat_infos
