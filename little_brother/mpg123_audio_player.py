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

import os.path
import shlex
import subprocess

from python_base_app import configuration

from little_brother import base_audio_player

class Mpg123AudioPlayer(base_audio_player.BaseAudioPlayer):


    def __init__(self, p_mpg123_binary):

        super().__init__()
        self._mpg123_binary = p_mpg123_binary

        if not os.path.exists(p_mpg123_binary):
            fmt = "Cannot find mpg123 binary at path '{path}'"
            raise configuration.ConfigurationException(fmt.format(path=p_mpg123_binary))

        fmt = "using audio player '{path}'"
        self._logger.info(fmt.format(path=p_mpg123_binary))


    def play_audio_file(self, p_audio_filename):  # pragma: no cover
        play_command = "{binary} {file}".format(binary=self._mpg123_binary, file=p_audio_filename)

        cmd_array = shlex.split(play_command)
        subprocess.run(cmd_array)
