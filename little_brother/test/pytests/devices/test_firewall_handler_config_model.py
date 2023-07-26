# -*- coding: utf-8 -*-

#    Copyright (C) 2021-2022  Marcus Rickert
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

from little_brother.devices.firewall_handler_config_model import FirewallHandlerConfigModel

DEFAULT_TARGET_IP = "8.8.8.8"


def test_create_firewall_handler_config_model():
    config = FirewallHandlerConfigModel()
    assert config is not None
    assert not config.is_active()


def test_create_active_firewall_handler_config_model():
    config = FirewallHandlerConfigModel()
    assert config is not None
    config.target_ip = DEFAULT_TARGET_IP
    assert config.is_active()
