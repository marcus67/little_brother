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

import time

import prometheus_client

from little_brother import settings

SECTION_NAME = "PrometheusClient"

DEFAULT_METRIC_PREFIX = "little_brother_"

from python_base_app import configuration

class PrometheusClientConfigModel(configuration.ConfigModel):

    def __init__(self):

        super().__init__(p_section_name=SECTION_NAME)

        self.port = configuration.NONE_INTEGER
        self.prefix = DEFAULT_METRIC_PREFIX

    def is_active(self):

        return self.port is not None


class PrometheusClient(object):

        def __init__(self, p_logger, p_config):

            self._logger = p_logger
            self._config = p_config
            self._gauge_monitored_users = prometheus_client.Gauge(self._config.prefix + "monitored_users",
                                                                  "number of monitored users")
            self._gauge_active_users = prometheus_client.Gauge(self._config.prefix + "active_users",
                                                               "number of active users",
                                                               ['username'])
            self._gauge_configured_users = prometheus_client.Gauge(self._config.prefix + "configured_users",
                                                               "number of configured users")
            self._gauge_monitored_hosts = prometheus_client.Gauge(self._config.prefix + "monitored_hosts",
                                                                  "number of monitored hosts",
                                                                  ['hostname'])
            self._gauge_monitored_devices = prometheus_client.Gauge(self._config.prefix + "monitored_devices",
                                                                  "number of monitored devices")
            self._gauge_active_devices = prometheus_client.Gauge(self._config.prefix + "active_devices",
                                                                  "number of active devices",
                                                                  ['devicename'])
            self._gauge_device_response_time = prometheus_client.Gauge(self._config.prefix + "device_response_time",
                                                                  "response time of device [ms]",
                                                                  ['devicename'])
            self._gauge_device_moving_average_response_time = \
                prometheus_client.Gauge(self._config.prefix + "device_moving_average_response_time",
                                        "moving average of response time of device [ms]",
                                        ['devicename'])
            self._counter_forced_logouts = prometheus_client.Counter(self._config.prefix + "forced_logouts",
                                                                     "number of forced logouts",
                                                                     ['username'])

            self._summary_http_requests = prometheus_client.Summary(self._config.prefix + "http_requests",
                                                                    "request duration [ms] and count",
                                                                    ['service', 'hostname'])

            self._info_system = prometheus_client.Info(self._config.prefix + "system",
                                                       "system information")
            self._info_system.info({ "version": settings.settings['version'],
                                     "revision": settings.extended_settings['debian_package_revision']})

            self._gauge_uptime = prometheus_client.Gauge(self._config.prefix + "uptime",
                                                         "uptime in seconds", ["hostname"])

            self._resident_memory_bytes_metric = prometheus_client.Gauge(
                'node_process_resident_memory_bytes',
                'resident memory in bytes on node', ['hostname'])
            self._cpu_seconds_total_metric = prometheus_client.Gauge(
                'node_process_cpu_seconds_total',
                'CPU time in seconds on node on node', ['hostname'])

        def start(self):

            try:
                fmt = "Starting Prometheus server on port {port}..."
                self._logger.info(fmt.format(port=self._config.port))

                prometheus_client.start_http_server(self._config.port)

            except OSError as e:
                fmt = "Exception {msg} while starting Prometheus server on port {port}"
                msg = fmt.format(msg=str(e), port=self._config.port)
                self._logger.error(msg)
                raise configuration.ConfigurationException(msg)

        def stop(self):

            # testing requires gauges to be removed again
            prometheus_client.REGISTRY.unregister(self._summary_http_requests)
            prometheus_client.REGISTRY.unregister(self._gauge_active_devices)
            prometheus_client.REGISTRY.unregister(self._gauge_device_response_time)
            prometheus_client.REGISTRY.unregister(self._gauge_monitored_devices)
            prometheus_client.REGISTRY.unregister(self._gauge_monitored_hosts)
            prometheus_client.REGISTRY.unregister(self._gauge_configured_users)
            prometheus_client.REGISTRY.unregister(self._gauge_monitored_users)
            prometheus_client.REGISTRY.unregister(self._counter_forced_logouts)
            prometheus_client.REGISTRY.unregister(self._gauge_active_users)
            prometheus_client.REGISTRY.unregister(self._gauge_device_moving_average_response_time)
            prometheus_client.REGISTRY.unregister(self._gauge_uptime)
            prometheus_client.REGISTRY.unregister(self._info_system)
            prometheus_client.REGISTRY.unregister(self._resident_memory_bytes_metric)
#            prometheus_client.REGISTRY.unregister(self._start_time_seconds_metric)
            prometheus_client.REGISTRY.unregister(self._cpu_seconds_total_metric)

        def set_client_stats(self, p_hostname, p_client_stats):

            self._cpu_seconds_total_metric.labels(hostname=p_hostname).set(p_client_stats.cpu_seconds_total)

            self.set_uptime(p_hostname=p_hostname, p_uptime=time.time() - p_client_stats.start_time_seconds)

            self._resident_memory_bytes_metric.labels(hostname=p_hostname).set(p_client_stats.resident_memory_bytes)

        def set_uptime(self, p_hostname, p_uptime):
            self._gauge_uptime.labels(hostname=p_hostname).set(p_uptime)

        def set_user_active(self, p_username, p_is_active):

            self._gauge_active_users.labels(username=p_username).set(1 if p_is_active else 0)

        def set_number_of_configured_users(self, p_count):

            self._gauge_configured_users.set(p_count)

        def set_number_of_monitored_users(self, p_count):

            self._gauge_monitored_users.set(p_count)

        def set_monitored_host(self, p_hostname, p_active):

            self._gauge_monitored_hosts.labels(hostname=p_hostname).set(1 if p_active else 0)

        def count_forced_logouts(self, p_username):

            self._counter_forced_logouts.labels(username=p_username).inc()

        def set_number_of_monitored_devices(self, p_count):

            self._gauge_monitored_devices.set(p_count)

        def set_device_response_time(self, p_device_name, p_time):

            self._gauge_device_response_time.labels(devicename=p_device_name).set(
                p_time if p_time is not None else 0)

        def set_device_active(self, p_device_name, p_active):

            self._gauge_active_devices.labels(devicename=p_device_name).set(1 if p_active else 0)

        def set_device_moving_average_response_time(self, p_device_name, p_time):

            self._gauge_device_moving_average_response_time.labels(devicename=p_device_name).set(
                p_time if p_time is not None else 0)

        def set_http_requests_summary(self, p_hostname, p_service, p_duration):

            self._summary_http_requests.labels(hostname=p_hostname, service=p_service).observe(p_duration)

        def get_http_requests_summary(self):

            return self._summary_http_requests
