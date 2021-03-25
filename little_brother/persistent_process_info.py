# -*- coding: utf-8 -*-

# Copyright (C) 2019-2021  Marcus Rickert
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

from sqlalchemy import Column, Integer, String, DateTime

from little_brother import persistence_base


class ProcessInfo(persistence_base.Base):
    __tablename__ = 'process_info'

    id = Column(Integer, primary_key=True)
    key = Column(String(256))
    hostname = Column(String(256))
    username = Column(String(256))
    pid = Column(Integer)
    processhandler = Column(String(1024))
    processname = Column(String(1024))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    downtime = Column(Integer, server_default="0")
    percent = Column(Integer, server_default="100")
