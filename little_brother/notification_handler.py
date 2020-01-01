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

import abc
import datetime
import locale

from python_base_app import configuration
from python_base_app import log_handling
from python_base_app import tools

REPLACE_PATTERN_AUDIO_TEXT_FILENAME = "infile"
REPLACE_PATTERN_BINARY = "binary"
REPLACE_PATTERN_AUDIO_TEXT = "text"
REPLACE_PATTERN_ENCODING = "encoding"

DEFAULT_MINIMUM_WAIT_BEFORE_REPEAT = 30  # seconds


class NotificationHandlerConfigModel(configuration.ConfigModel):

    def __init__(self, p_section_name):
        super().__init__(p_section_name=p_section_name)

        self.cache_audio_files = False
        self.mininum_waiting_time_before_repeat = DEFAULT_MINIMUM_WAIT_BEFORE_REPEAT  # seconds
        self.locale = None


class NotificationHandler(object):

    def __init__(self, p_config):

        self._config = p_config

        self._logger = log_handling.get_logger(self.__class__.__name__)

        self._recent_texts = {}

        if self._config.locale is None:
            self._config.locale = locale.getdefaultlocale()[0]

        self.init_engine()

    def init_engine(self):

        pass

    def stop_engine(self):

        pass

    def notify(self, p_text, p_locale=None):

        last_time_spoken = self._recent_texts.get(p_text)

        if p_locale is None:
            p_locale = self._config.locale

        if last_time_spoken is not None:
            if datetime.datetime.now() < last_time_spoken + datetime.timedelta(
                    seconds=self._config.mininum_waiting_time_before_repeat):
                fmt = "Text '{text}' has been output less than {waiting_time} seconds ago -> ignoring"
                self._logger.info(fmt.format(text=p_text, waiting_time=self._config.mininum_waiting_time_before_repeat))
                return None

        a_thread =  tools.start_simple_thread(method=self._notify, p_text=p_text, p_locale=p_locale)
        self._recent_texts[p_text] = datetime.datetime.now()

        return a_thread

    @abc.abstractmethod
    def _notify(self, p_text, p_locale=None):
        pass
