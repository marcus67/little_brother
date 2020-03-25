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
import tempfile

from little_brother import audio_handler
from python_base_app import configuration
from python_base_app import log_handling
from python_base_app.test import base_test

SPOOL_DIR = tempfile.gettempdir()
TEXT = "hallo"
LOCALE = "de_DE"


class TestAudioHandler(base_test.BaseTestCase):

    @staticmethod
    def delete_audio_file(p_audio_handler):

        audio_file = p_audio_handler.get_audio_filename(p_text=TEXT, p_locale=None)

        try:
            os.unlink(audio_file)

        except Exception as e:
            logger = log_handling.get_logger()
            fmt = "Cannot delete audio file {filename}: {exception}"
            logger.warning(fmt.format(filename=audio_file, exception=str(e)))

    @base_test.skip_if_env("NO_AUDIO_OUTPUT")
    def test_engine_google_init(self):

        a_config = audio_handler.AudioHandlerConfigModel()
        a_config.speech_engine = audio_handler.SPEECH_ENGINE_GOOGLE
        a_handler = audio_handler.AudioHandler(p_config=a_config)

        self.assertIsNotNone(a_handler)

    @base_test.skip_if_env("NO_AUDIO_OUTPUT")
    def test_engine_google_speak(self):

        a_config = audio_handler.AudioHandlerConfigModel()
        a_config.speech_engine = audio_handler.SPEECH_ENGINE_GOOGLE
        a_config.spool_dir = SPOOL_DIR
        a_config.locale = LOCALE
        a_handler = audio_handler.AudioHandler(p_config=a_config)

        self.assertIsNotNone(a_handler)

        self.delete_audio_file(p_audio_handler=a_handler)
        a_handler.notify(p_text=TEXT, p_locale=LOCALE)
        a_handler.notify(p_text=TEXT, p_locale=LOCALE)
        a_handler.stop_engine()

    @base_test.skip_if_env("NO_AUDIO_OUTPUT")
    def test_spool_dir_and_file(self):

        a_config = audio_handler.AudioHandlerConfigModel()
        a_config.speech_engine = audio_handler.SPEECH_ENGINE_GOOGLE
        a_config.spool_dir = SPOOL_DIR
        a_handler = audio_handler.AudioHandler(p_config=a_config)

        self.assertIsNotNone(a_handler)

        audio_file = a_handler.get_audio_filename(p_text=TEXT, p_locale=None)

        self.assertTrue(audio_file.startswith(SPOOL_DIR))

        self.delete_audio_file(p_audio_handler=a_handler)
        a_thread = a_handler.notify(p_text=TEXT)
        a_thread.join()
        #        time.sleep(1)

        self.assertTrue(os.path.exists(audio_file))

        a_handler.stop_engine()

    # @base_test.skip_if_env("NO_AUDIO_OUTPUT")
    # def test_engine_pyttsx3_init(self):
    #
    #     a_config = audio_handler.AudioHandlerConfigModel()
    #     a_config.speech_engine = audio_handler.SPEECH_ENGINE_PYTTSX3
    #     a_handler = audio_handler.AudioHandler(p_config=a_config)
    #
    #     self.assertIsNotNone(a_handler)
    #
    #     a_handler.stop_engine()

    # @base_test.skip_if_env("NO_AUDIO_OUTPUT")
    # def test_engine_pyttsx3_speak(self):
    #
    #     a_config = audio_handler.AudioHandlerConfigModel()
    #     a_config.speech_engine = audio_handler.SPEECH_ENGINE_PYTTSX3
    #     a_config.spool_dir = SPOOL_DIR
    #     a_handler = audio_handler.AudioHandler(p_config=a_config)
    #
    #     self.assertIsNotNone(a_handler)
    #
    #     self.delete_audio_file(p_audio_handler=a_handler)
    #     a_thread = a_handler.notify(p_text=TEXT)
    #     a_thread.join()
    #
    #     a_handler.stop_engine()
    #
    # @base_test.skip_if_env("NO_AUDIO_OUTPUT")
    # def test_engine_pyttsx3_speak_mixer(self):
    #
    #     a_config = audio_handler.AudioHandlerConfigModel()
    #     a_config.speech_engine = audio_handler.SPEECH_ENGINE_PYTTSX3
    #     a_config.spool_dir = SPOOL_DIR
    #     a_config.audio_mixer_volume = 50
    #     a_handler = audio_handler.AudioHandler(p_config=a_config)
    #
    #     self.assertIsNotNone(a_handler)
    #
    #     self.delete_audio_file(p_audio_handler=a_handler)
    #     a_thread = a_handler.notify(p_text=TEXT)
    #     a_thread.join()
    #
    #     a_handler.stop_engine()

    def test_engine_external_init(self):

        a_config = audio_handler.AudioHandlerConfigModel()
        a_config.speech_engine = audio_handler.SPEECH_ENGINE_EXTERNAL
        a_handler = audio_handler.AudioHandler(p_config=a_config)

        self.assertIsNotNone(a_handler)

        a_handler.stop_engine()

    @base_test.skip_if_env("NO_AUDIO_OUTPUT")
    def test_engine_external_speak(self):

        a_config = audio_handler.AudioHandlerConfigModel()
        a_config.speech_engine = audio_handler.SPEECH_ENGINE_EXTERNAL
        a_config.spool_dir = SPOOL_DIR
        a_handler = audio_handler.AudioHandler(p_config=a_config)

        self.assertIsNotNone(a_handler)

        self.delete_audio_file(p_audio_handler=a_handler)
        a_handler.notify(p_text=TEXT)

        a_handler.stop_engine()

    @base_test.skip_if_env("NO_AUDIO_OUTPUT")
    def test_engine_external_speak_mixer(self):

        a_config = audio_handler.AudioHandlerConfigModel()
        a_config.speech_engine = audio_handler.SPEECH_ENGINE_EXTERNAL
        a_config.spool_dir = SPOOL_DIR
        a_config.audio_mixer_volume = 50
        a_handler = audio_handler.AudioHandler(p_config=a_config)

        self.assertIsNotNone(a_handler)

        self.delete_audio_file(p_audio_handler=a_handler)
        a_handler.notify(p_text=TEXT)

        a_handler.stop_engine()

    def test_engine_invalid(self):

        a_config = audio_handler.AudioHandlerConfigModel()
        a_config.speech_engine = "NOT-EXISTING"

        with self.assertRaises(configuration.ConfigurationException):
            a_handler = audio_handler.AudioHandler(p_config=a_config)
            self.assertIsNotNone(a_handler)

