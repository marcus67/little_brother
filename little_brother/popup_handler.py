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
import subprocess

from little_brother import notification_handler
from python_base_app import configuration

SECTION_NAME = "PopupHandler"

POPUP_ENGINE_XMESSAGE = "xmessage"
POPUP_ENGINE_GXMESSAGE = "gxmessage"
POPUP_ENGINE_ZENITY = "zenity"
POPUP_ENGINE_YAD = "yad"

POPUP_ENGINES = {
    POPUP_ENGINE_XMESSAGE: "/usr/bin/xmessage -nearmouse {{{pattern}}}".format(
        pattern=notification_handler.REPLACE_PATTERN_AUDIO_TEXT),
    POPUP_ENGINE_GXMESSAGE: "/usr/bin/X11/gxmessage -title LittleBrother -encoding {{{encoding_pattern}}} -nearmouse {{{text_pattern}}}".format(
        text_pattern=notification_handler.REPLACE_PATTERN_AUDIO_TEXT,
        encoding_pattern=notification_handler.REPLACE_PATTERN_ENCODING),
    POPUP_ENGINE_ZENITY: "/usr/bin/X11/zenity --info --text='{{{pattern}}}'".format(
        pattern=notification_handler.REPLACE_PATTERN_AUDIO_TEXT),
    POPUP_ENGINE_YAD: "/usr/bin/X11/yad --text='{{{pattern}}}'".format(
        pattern=notification_handler.REPLACE_PATTERN_AUDIO_TEXT)
}


class PopupHandlerConfigModel(notification_handler.NotificationHandlerConfigModel):

    def __init__(self):
        super().__init__(p_section_name=SECTION_NAME)

        self.cache_popup_files = False
        self.popup_engine = configuration.NONE_STRING
        self.engine_cmd_line = configuration.NONE_STRING
        self.encoding = "UTF-8"

    def is_active(self):
        return self.popup_engine is not None


class PopupHandler(notification_handler.NotificationHandler):

    def __init__(self, p_config):

        super().__init__(p_config=p_config)

    def _notify(self, p_text, p_locale=None):

        popup_command_line = POPUP_ENGINES.get(self._config.popup_engine)

        if popup_command_line is not None:
            self.popup_command(p_text=p_text, p_locale=p_locale, p_command_line=popup_command_line)

        else:
            fmt = "_notify(): invalid popup engine '%s'" % self._config.popup_engine
            self._logger.error(fmt)
            raise configuration.ConfigurationException(fmt)

        self._recent_texts[p_text] = datetime.datetime.now()

    def init_engine(self):

        popup_command_line = POPUP_ENGINES.get(self._config.popup_engine)

        if popup_command_line is None:
            fmt = "init_engine(): invalid popup engine '%s'" % self._config.popup_engine
            self._logger.error(fmt)
            raise configuration.ConfigurationException(fmt)

    def popup_command(self, p_command_line, p_text, p_locale=None):

        replacements = {
            notification_handler.REPLACE_PATTERN_AUDIO_TEXT: p_text,
            notification_handler.REPLACE_PATTERN_ENCODING: self._config.encoding,
        }

        cmd_line = p_command_line.format(**replacements).encode(self._config.encoding)

        try:

            fmt = "popup_command(): execute '%s'" % cmd_line
            self._logger.debug(fmt)
            subprocess.run(cmd_line, shell=True)

        except Exception as e:

            fmt = "popup_command(): cannot output text '%s': exception %s" % (p_text, str(e))
            self._logger.warning(fmt)
