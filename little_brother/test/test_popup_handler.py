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

from little_brother import popup_handler
from python_base_app import configuration
from python_base_app.test import base_test

TEXT = "hallo"
LOCALE = "de_DE"


class TestPopupHandler(base_test.BaseTestCase):

    # @staticmethod
    # def delete_popup_file(p_popup_handler):
    #
    #     popup_file = p_popup_handler.get_popup_filename(p_text=TEXT, p_locale=None)
    #
    #     try:
    #         os.unlink(popup_file)
    #
    #     except Exception:
    #         logger = log_handling.get_logger()
    #         logger.warning("Cannot delete popup file!")

    def test_engine_bash_shell_init(self):

        a_config = popup_handler.PopupHandlerConfigModel()
        a_config.popup_engine = popup_handler.POPUP_ENGINE_SHELL_ECHO
        a_handler = popup_handler.PopupHandler(p_config=a_config)

        self.assertIsNotNone(a_handler)

        a_handler.notify(p_text=TEXT)

    @base_test.skip_if_env("NO_POPUPS")
    def test_engine_gxmessage_init(self):

        a_config = popup_handler.PopupHandlerConfigModel()
        a_config.popup_engine = popup_handler.POPUP_ENGINE_GXMESSAGE
        a_handler = popup_handler.PopupHandler(p_config=a_config)

        self.assertIsNotNone(a_handler)

        a_handler.notify(p_text=TEXT)

    @base_test.skip_if_env("NO_POPUPS")
    def test_engine_xmessage_init(self):

        a_config = popup_handler.PopupHandlerConfigModel()
        a_config.popup_engine = popup_handler.POPUP_ENGINE_XMESSAGE
        a_handler = popup_handler.PopupHandler(p_config=a_config)

        self.assertIsNotNone(a_handler)

        a_handler.notify(p_text=TEXT)

    @base_test.skip_if_env("NO_POPUPS")
    def test_engine_yad_init(self):

        a_config = popup_handler.PopupHandlerConfigModel()
        a_config.popup_engine = popup_handler.POPUP_ENGINE_YAD
        a_handler = popup_handler.PopupHandler(p_config=a_config)

        self.assertIsNotNone(a_handler)

        a_handler.notify(p_text=TEXT)

    @base_test.skip_if_env("NO_POPUPS")
    def test_engine_zenity_init(self):

        a_config = popup_handler.PopupHandlerConfigModel()
        a_config.popup_engine = popup_handler.POPUP_ENGINE_ZENITY
        a_handler = popup_handler.PopupHandler(p_config=a_config)

        self.assertIsNotNone(a_handler)

        a_handler.notify(p_text=TEXT)

    def test_engine_invalid(self):

        a_config = popup_handler.PopupHandlerConfigModel()
        a_config.popup_engine = "NOT-EXISTING"

        with self.assertRaises(configuration.ConfigurationException):
            a_handler = popup_handler.PopupHandler(p_config=a_config)
            self.assertIsNotNone(a_handler)
            a_handler.notify(p_text=TEXT)
