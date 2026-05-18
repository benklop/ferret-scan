# -*- coding: utf-8 -*-
from __future__ import absolute_import

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import os

import wx

from ferret_scan.gui.wizard.main import Wizard
from ferret_scan.util import profile, resources


def _logo_bitmap(max_height=120):
    try:
        image = wx.Image(resources.get_path_for_image('logo.png'))
    except Exception:
        image = wx.Image(resources.get_path_for_image('nusb.png'))
    width, height = image.GetSize()
    if height > max_height and height > 0:
        scale = float(max_height) / height
        image = image.Scale(int(width * scale), max_height, wx.IMAGE_QUALITY_HIGH)
    return wx.Bitmap(image)


class WelcomeDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(
            self,
            parent,
            title=_('Welcome'),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        self.parent = parent
        self.last_files = profile.settings['last_files']

        header = Header(self)
        content = Content(self)
        check_box_show = wx.CheckBox(self, label=_("Don't show this dialog again"))
        check_box_show.SetValue(not profile.settings['show_welcome'])

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(header, 0, wx.EXPAND | wx.ALL, 8)
        vbox.Add(content, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(check_box_show, 0, wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.EXPAND | wx.ALL, 12)
        self.SetSizerAndFit(vbox)
        self.SetMinSize((760, 520))
        self.CentreOnParent()

        check_box_show.Bind(wx.EVT_CHECKBOX, self.on_check_box_changed)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.ShowModal()

    def on_check_box_changed(self, event):
        profile.settings['show_welcome'] = not event.IsChecked()

    def on_close(self, event):
        self.EndModal(wx.ID_OK)
        self.Destroy()


class Header(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        logo = wx.StaticBitmap(self, wx.ID_ANY, _logo_bitmap())
        title_text = wx.StaticText(self, label=_('3D scanning for everyone'))
        title_font = title_text.GetFont()
        title_font.SetPointSize(13)
        title_font.SetWeight(wx.BOLD)
        title_text.SetFont(title_font)
        separator = wx.StaticLine(self)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(logo, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 16)
        vbox.Add(title_text, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 12)
        vbox.Add(separator, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 16)
        self.SetSizer(vbox)


class CreateNew(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        title_text = wx.StaticText(self, label=_('Create new'))
        title_font = title_text.GetFont()
        title_font.SetWeight(wx.BOLD)
        title_text.SetFont(title_font)

        scan_button = wx.Button(self, label=_('Scan using recent settings'))
        advanced_adjustment_button = wx.Button(self, label=_('Advanced adjustment'))
        advanced_calibration_button = wx.Button(self, label=_('Advanced calibration'))

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(title_text, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 8)
        vbox.Add(scan_button, 0, wx.EXPAND | wx.ALL, 4)
        vbox.Add(advanced_adjustment_button, 0, wx.EXPAND | wx.ALL, 4)
        vbox.Add(advanced_calibration_button, 0, wx.EXPAND | wx.ALL, 4)
        self.SetSizer(vbox)

        scan_button.Bind(wx.EVT_BUTTON, self.on_scan)
        advanced_adjustment_button.Bind(wx.EVT_BUTTON, self.on_advanced_adjustment)
        advanced_calibration_button.Bind(wx.EVT_BUTTON, self.on_advanced_calibration)

    def on_wizard(self, event):
        parent = self.GetParent().GetParent()
        parent.Hide()
        Wizard(parent.parent)

    def on_scan(self, event):
        profile.settings['workbench'] = 'scanning'
        parent = self.GetParent().GetParent()
        workbench = parent.parent.workbench[profile.settings['workbench']].name
        parent.parent.update_workbench(workbench)
        parent.Close()

    def on_advanced_control(self, event):
        profile.settings['workbench'] = 'control'
        parent = self.GetParent().GetParent()
        workbench = parent.parent.workbench[profile.settings['workbench']].name
        parent.parent.update_workbench(workbench)
        parent.Close()

    def on_advanced_adjustment(self, event):
        profile.settings['workbench'] = 'adjustment'
        parent = self.GetParent().GetParent()
        workbench = parent.parent.workbench[profile.settings['workbench']].name
        parent.parent.update_workbench(workbench)
        parent.Close()

    def on_advanced_calibration(self, event):
        profile.settings['workbench'] = 'calibration'
        parent = self.GetParent().GetParent()
        workbench = parent.parent.workbench[profile.settings['workbench']].name
        parent.parent.update_workbench(workbench)
        parent.Close()


class OpenRecent(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        title_text = wx.StaticText(self, label=_('Open recent file'))
        title_font = title_text.GetFont()
        title_font.SetWeight(wx.BOLD)
        title_text.SetFont(title_font)

        last_files = list(profile.settings['last_files'])
        last_files.reverse()

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(title_text, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 8)

        if last_files:
            for path in last_files:
                button = wx.Button(self, label=os.path.basename(path), name=path)
                button.Bind(wx.EVT_BUTTON, self.on_button_pressed)
                vbox.Add(button, 0, wx.EXPAND | wx.ALL, 4)
        else:
            vbox.Add(
                wx.StaticText(self, label=_('No recent scans yet')),
                0,
                wx.ALIGN_CENTER_HORIZONTAL | wx.ALL,
                4,
            )

        self.SetSizer(vbox)

    def on_button_pressed(self, event):
        button = event.GetEventObject()
        profile.settings['workbench'] = 'scanning'
        parent = self.GetParent().GetParent()
        workbench = parent.parent.workbench[profile.settings['workbench']].name
        parent.parent.update_workbench(workbench)
        parent.parent.append_last_file(button.GetName())
        parent.parent.workbench['scanning'].scene_view.load_file(button.GetName())
        parent.Close()


class Content(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        create_new = CreateNew(self)
        open_recent = OpenRecent(self)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(create_new, 1, wx.EXPAND | wx.ALL, 4)
        hbox.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        hbox.Add(open_recent, 1, wx.EXPAND | wx.ALL, 4)
        self.SetSizer(hbox)
