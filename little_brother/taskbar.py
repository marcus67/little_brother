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

import wx
import wx.adv
import os.path

from python_base_app import exceptions

TRAY_TOOLTIP = 'LittleBrother Tray'
TRAY_ICON = os.path.join(os.path.dirname(__file__), 'static/icons/icon_baby-panda_32x32.png')

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, p_config, p_status_frame, p_base_app):
        super(TaskBarIcon, self).__init__()
        self._config = p_config
        self._status_frame = p_status_frame
        self._base_app = p_base_app
        self.set_icon(TRAY_ICON)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        self._status_frame.Show(not self._status_frame.IsShown())

    def on_exit(self, event):
        self.shut_down()

    def shut_down(self):
        wx.CallAfter(self.Destroy)
        self._status_frame.Close()
        self._base_app.stop_event_queue()
