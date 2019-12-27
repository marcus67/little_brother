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

from little_brother import audio_handler
from little_brother import mpg123_audio_player
from little_brother import playsound_audio_player
from python_base_app.test import base_test

HELLO_MPG = os.path.join(os.path.dirname(__file__), "resources/hello.mpg")


class TestAudioPlayer(base_test.BaseTestCase):

    @base_test.skip_if_env("NO_AUDIO_OUTPUT")
    def test_mpg123_player(self):

        a_config = audio_handler.AudioHandlerConfigModel()
        a_player = mpg123_audio_player.Mpg123AudioPlayer(p_mpg123_binary = a_config.mpg123_binary)
        a_player.play_audio_file(HELLO_MPG)

    @base_test.skip_if_env("NO_AUDIO_OUTPUT")
    def test_playsound_player(self):

        a_player = playsound_audio_player.PlaysoundAudioPlayer()
        a_player.play_audio_file(HELLO_MPG)

