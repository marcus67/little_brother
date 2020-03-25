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

import datetime
import hashlib
import locale
import os.path
import shlex
import subprocess

#import pyttsx3

from little_brother import mpg123_audio_player
from little_brother import notification_handler
#from little_brother import playsound_audio_player
from little_brother import pyglet_audio_player
from python_base_app import configuration

DEFAULT_SPEECH_GENERATOR_CMD_LINE = '/usr/bin/festival --tts --language american_english {{{pattern}}}'.format(
    pattern=notification_handler.REPLACE_PATTERN_AUDIO_TEXT_FILENAME)
DEFAULT_AUDIO_MIXER_BIN = '/usr/bin/amixer'
DEFAULT_AUDIO_FILE_PREFIX = "little-brother-speech-"
DEFAULT_SPOOL_DIRECTORY = "/var/spool/little-brother"
DEFAULT_SPEECH_WORDS_PER_MINUTE = 100

SECTION_NAME = "AudioHandler"

#SPEECH_ENGINE_PYTTSX3 = "pyttsx3"
SPEECH_ENGINE_GOOGLE = "google"
SPEECH_ENGINE_EXTERNAL = "external"

AUDIO_TEXT_FILE = "audio.txt"

#AUDIO_PLAYER_PLAYSOUND = "playsound"
AUDIO_PLAYER_PYGLET = "pyglet"
AUDIO_PLAYER_MPG123 = "mpg123"

DEFAULT_MPG123_binary = "/usr/bin/mpg123"

DEFAULT_AUDIO_PLAYER = AUDIO_PLAYER_MPG123


class AudioHandlerConfigModel(notification_handler.NotificationHandlerConfigModel):

    def __init__(self):
        super().__init__(p_section_name=SECTION_NAME)

        self.cache_audio_files = False
        self.speech_engine = configuration.NONE_STRING
        self.speech_words_per_minute = DEFAULT_SPEECH_WORDS_PER_MINUTE
        self.spool_dir = DEFAULT_SPOOL_DIRECTORY
        self.audio_file_prefix = DEFAULT_AUDIO_FILE_PREFIX
        self.audio_mixer_bin = DEFAULT_AUDIO_MIXER_BIN
        self.audio_mixer_volume = configuration.NONE_INTEGER  # in percent
        self.speech_generator_cmd_line = DEFAULT_SPEECH_GENERATOR_CMD_LINE
        self.audio_player = DEFAULT_AUDIO_PLAYER
        self.mpg123_binary = DEFAULT_MPG123_binary

    def is_active(self):
        return self.speech_engine is not None


class AudioHandler(notification_handler.NotificationHandler):

    def __init__(self, p_config):

        self._google_speak = None
        self._audio_player = None

        super().__init__(p_config=p_config)

    # def init_engine_pyttsx3(self):
    #
    #     self._pyttsx3_engine = pyttsx3.init()
    #     self._pyttsx3_engine.setProperty('rate', self._config.speech_words_per_minute)

    def check_audio_player(self):

        try:
            # if self._config.audio_player == AUDIO_PLAYER_PLAYSOUND:
            #     self._audio_player = playsound_audio_player.PlaysoundAudioPlayer()

            if self._config.audio_player == AUDIO_PLAYER_PYGLET:
                self._audio_player = pyglet_audio_player.PygletAudioPlayer()

            elif self._config.audio_player == AUDIO_PLAYER_MPG123:
                self._audio_player = mpg123_audio_player.Mpg123AudioPlayer(self._config.mpg123_binary)

            else:
                fmt = "Invalid audio player '{player}'"
                self._logger.error(fmt, player=self._config.audio_player)
                raise configuration.ConfigurationException(fmt)

        except Exception:
            fmt = "Cannot load audio player '{player}'"
            self._logger.error(fmt, player=self._config.audio_player)
            raise configuration.ConfigurationException(fmt)

    def init_engine_google(self):

        try:
            import python_google_speak.speech_generator
            self._google_speak = python_google_speak.speech_generator

        except:
            fmt = "init_engine_google(): cannot load module 'python_google_speak'"
            self._logger.error(fmt)
            raise configuration.ConfigurationException(fmt)

        self.check_audio_player()

    def init_engine(self):

        if self._config.speech_engine == SPEECH_ENGINE_EXTERNAL:
            pass

        # elif self._config.speech_engine == SPEECH_ENGINE_PYTTSX3:
        #     self.init_engine_pyttsx3()

        elif self._config.speech_engine == SPEECH_ENGINE_GOOGLE:
            self.init_engine_google()

        else:
            fmt = "init_engine(): invalid speech engine '%s'" % self._config.speech_engine
            self._logger.error(fmt)
            raise configuration.ConfigurationException(fmt)

    def stop_engine(self):
        if self._audio_player is not None:
            self._audio_player.stop()

        super().stop_engine()

    def get_audio_filename(self, p_text, p_locale=None):

        if p_locale is None:
            p_locale = locale.getdefaultlocale()[0]

        text = (p_text + p_locale).encode("UTF-8")
        hash_value = hashlib.sha224(text).hexdigest()
        return os.path.join(self._config.spool_dir, self._config.audio_file_prefix + hash_value)

    def _notify(self, p_text, p_locale=None):

        if self._config.speech_engine == SPEECH_ENGINE_EXTERNAL:
            self.speak_external_command(p_text=p_text, p_locale=p_locale)

        # elif self._config.speech_engine == SPEECH_ENGINE_PYTTSX3:
        #     self.speak_pyttsx(p_text=p_text, p_locale=p_locale)

        elif self._config.speech_engine == SPEECH_ENGINE_GOOGLE:
            self.speak_google(p_text=p_text, p_locale=p_locale)

        else:
            fmt = "_notify(): invalid speech engine '%s'" % self._config.speech_engine
            self._logger.error(fmt)
            raise configuration.ConfigurationException(fmt)

        self._recent_texts[p_text] = datetime.datetime.now()

    # def speak_pyttsx(self, p_text, p_locale=None):
    #
    #     if self._config.audio_mixer_volume is not None:
    #         fmt = "speak_pyttsx(): set volume to %d%%" % self._config.audio_mixer_volume
    #         self._logger.debug(fmt)
    #
    #         self._pyttsx3_engine.setProperty("volume", 1.0 * self._config.audio_mixer_volume / 100.0)
    #
    #     fmt = "speak_pyttsx(): speak '%s'" % p_text
    #     self._logger.debug(fmt)
    #
    #     self._pyttsx3_engine.say(p_text)
    #     self._pyttsx3_engine.runAndWait()

    def speak_google(self, p_text, p_locale=None):

        self.set_volume()

        audio_filename = self.get_audio_filename(p_text=p_text, p_locale=p_locale)

        if not os.path.exists(path=audio_filename):
            google_speak = self._google_speak.SpeechGenerator(p_locale=p_locale)
            data = google_speak.generate_audio_data(p_text=p_text)

            with open(audio_filename, "wb") as f:
                f.write(data)

        self._audio_player.play_audio_file(audio_filename)

    def set_volume(self):

        if self._config.audio_mixer_volume is not None:
            cmd_line = "%s -q sset Master %d%%" % (
                shlex.quote(self._config.audio_mixer_bin),
                self._config.audio_mixer_volume)

            try:
                fmt = "speak_external_command(): set volume to %d%%" % self._config.audio_mixer_volume
                self._logger.debug(fmt)

                subprocess.run(cmd_line, shell=True)

            except Exception as e:

                fmt = "cannot set audio volume using '%s': exception %s" % (cmd_line, str(e))
                self._logger.warning(fmt)

    def speak_external_command(self, p_text, p_locale=None):

        self.set_volume()

        audio_text_filename = "<UNDEFINED>"

        if notification_handler.REPLACE_PATTERN_AUDIO_TEXT_FILENAME in self._config.speech_generator_cmd_line:
            audio_text_filename = os.path.join(self._config.spool_dir, AUDIO_TEXT_FILE)

            try:
                with open(audio_text_filename, "w") as f:
                    f.write(p_text)

            except Exception as e:
                fmt = "exception '{estr}' while writing text '{text}' into audio playback file {filename}"
                self._logger.warning(fmt.format(estr=str(e), text=p_text, filename=audio_text_filename))
                return

        replacements = {
            notification_handler.REPLACE_PATTERN_AUDIO_TEXT_FILENAME: audio_text_filename,
            notification_handler.REPLACE_PATTERN_AUDIO_TEXT: p_text
        }

        cmd_line = self._config.speech_generator_cmd_line.format(**replacements)

        try:

            fmt = "speak_external_command(): execute '%s'" % cmd_line
            self._logger.debug(fmt)
            subprocess.run(cmd_line, shell=True)

        except Exception as e:

            fmt = "cannot playback text '%s': exception %s" % (p_text, str(e))
            self._logger.warning(fmt)
