# -*- coding: utf-8 -*-

# Copyright (C) 2019-2022  Marcus Rickert
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

def key(p_source, p_destination):
    return p_source + "|" + p_destination


class FirewallEntry:

    def key(self):
        return key(p_source=self.source, p_destination=self.destination)

    def __init__(self):

        self.index = None
        self.target = None
        self.source = None
        self.destination = None
        self.protocol = None
        self.comment = None
