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

import os
import unittest

import prometheus_client

from little_brother import prometheus
from python_base_app.test import base_test


class TestPrometheus(base_test.BaseTestCase):

    def test_create(self):
        # Reset Prometheus
        prometheus_client.registry.REGISTRY = prometheus_client.CollectorRegistry(auto_describe=True)

        config = prometheus.PrometheusClientConfigModel()
        client = prometheus.PrometheusClient(p_logger=self._logger, p_config=config)

        self.assertIsNotNone(client)

        client.stop()

    def test_start(self):
        # Reset Prometheus
        prometheus_client.registry.REGISTRY = prometheus_client.CollectorRegistry(auto_describe=True)

        config = prometheus.PrometheusClientConfigModel()
        config.port = int(os.getenv("PROMETHEUS_SERVER_PORT", "8889"))
        client = prometheus.PrometheusClient(p_logger=self._logger, p_config=config)

        self.assertIsNotNone(client)

        client.start()

        client.stop()


if __name__ == "__main__":
    unittest.main()
