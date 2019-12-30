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

import threading

from little_brother import base_audio_player
from python_base_app import configuration


class PygletAudioPlayer(base_audio_player.BaseAudioPlayer):

    def __init__(self):

        super().__init__()

        self._player_thread = None

        try:
            import pyglet

            self._pyglet = pyglet
            run_method = self._pyglet.app.run
            self._pyglet.clock.schedule(lambda dt : 1)
            self._player_thread = threading.Thread(target=run_method)
            self._player_thread.start()

        except Exception:
            fmt = "Cannot load module 'pyglet'"
            self._logger.error(fmt)
            raise configuration.ConfigurationException(fmt)

        self._logger.info("audio player 'pyglet' loaded")

    def play_audio_file(self, p_audio_filename):  # pragma: no cover
        audio_file = self._pyglet.media.load(p_audio_filename)
        audio_file.play()

    def stop(self):
        if self._player_thread is not None:
            self._logger.info("audio player 'pyglet' deactivated")
            self._pyglet.app.exit()
            self._player_thread.join()
