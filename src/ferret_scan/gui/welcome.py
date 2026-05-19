# -*- coding: utf-8 -*-
from __future__ import absolute_import

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import os

import wx

from ferret_scan.gui.util.preferences import PreferencesDialog
from ferret_scan.hardware.registry import get_registry
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
    def __init__(self, parent, auto_connect=True):
        wx.Dialog.__init__(
            self,
            parent,
            title=_('Welcome'),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        self.parent = parent
        self.auto_connect = auto_connect
        self._open_preferences_after = False

        header = Header(self)
        hardware = HardwarePicker(self)
        content = Content(self)
        check_box_show = wx.CheckBox(self, label=_("Don't show this dialog again"))
        check_box_show.SetValue(not profile.settings['show_welcome'])

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(header, 0, wx.EXPAND | wx.ALL, 8)
        vbox.Add(hardware, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        vbox.Add(content, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(check_box_show, 0, wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.EXPAND | wx.ALL, 12)
        self.SetSizerAndFit(vbox)
        self.SetMinSize((760, 580))
        self.CentreOnParent()

        check_box_show.Bind(wx.EVT_CHECKBOX, self.on_check_box_changed)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.ShowModal()

    def on_check_box_changed(self, event):
        profile.settings['show_welcome'] = not event.IsChecked()

    def on_close(self, event):
        self.EndModal(wx.ID_OK)
        self.Destroy()
        if self._open_preferences_after:
            dlg = PreferencesDialog(parent=self.parent)
            dlg.ShowModal()
        from ferret_scan.hardware.migration import migrate_hardware_settings
        from ferret_scan.runtime_engine import driver

        migrate_hardware_settings(profile.settings)
        profile.settings.save_settings(categories=['preferences'])
        driver.reset()
        self.parent.initialize_driver()
        self.parent.refresh_device_ui()
        if self.auto_connect:
            wx.CallAfter(self.parent.auto_connect)


class HardwarePicker(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.registry = get_registry()

        box = wx.StaticBox(self, label=_('Hardware'))
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        self.scanner_label = wx.StaticText(self, label=_('Scanner'))
        self.scanner_combo = wx.ComboBox(self, size=(240, -1), style=wx.CB_READONLY)
        self.turntable_label = wx.StaticText(self, label=_('Turntable'))
        self.turntable_combo = wx.ComboBox(self, size=(240, -1), style=wx.CB_READONLY)
        self.more_btn = wx.Button(self, label=_('More options…'))

        self._scanner_map = {s.label: s.id for s in self.registry.available_scanners()}
        self._turntable_map = {t.label: t.id for t in self.registry.available_turntables()}
        self.scanner_combo.SetItems(list(self._scanner_map.keys()))
        self.turntable_combo.SetItems(list(self._turntable_map.keys()))
        self.scanner_combo.SetValue(self.registry.active_scanner().label)
        self.turntable_combo.SetValue(self.registry.active_turntable().label)

        row1 = wx.BoxSizer(wx.HORIZONTAL)
        row1.Add(self.scanner_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        row1.Add(self.scanner_combo, 1, wx.EXPAND)
        row2 = wx.BoxSizer(wx.HORIZONTAL)
        row2.Add(self.turntable_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        row2.Add(self.turntable_combo, 1, wx.EXPAND)
        sizer.Add(row1, 0, wx.EXPAND | wx.ALL, 6)
        sizer.Add(row2, 0, wx.EXPAND | wx.ALL, 6)
        sizer.Add(self.more_btn, 0, wx.ALIGN_RIGHT | wx.ALL, 6)

        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(sizer, 0, wx.EXPAND)
        self.SetSizer(outer)

        self.scanner_combo.Bind(wx.EVT_COMBOBOX, self._on_hardware_changed)
        self.turntable_combo.Bind(wx.EVT_COMBOBOX, self._on_hardware_changed)
        self.more_btn.Bind(wx.EVT_BUTTON, self._on_more_options)

    def _on_hardware_changed(self, event):
        sl = self.scanner_combo.GetValue()
        tl = self.turntable_combo.GetValue()
        if sl in self._scanner_map:
            self.registry.set_active_scanner(self._scanner_map[sl])
        if tl in self._turntable_map:
            self.registry.set_active_turntable(self._turntable_map[tl])

    def _on_more_options(self, event):
        welcome = self.GetParent()
        welcome._open_preferences_after = True
        welcome.Close()


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
        advanced_control_button = wx.Button(self, label=_('Advanced control'))
        advanced_adjustment_button = wx.Button(self, label=_('Advanced adjustment'))
        advanced_calibration_button = wx.Button(self, label=_('Advanced calibration'))

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(title_text, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 8)
        vbox.Add(scan_button, 0, wx.EXPAND | wx.ALL, 4)
        caps = get_registry().capabilities()
        if caps.has_control_workbench:
            vbox.Add(advanced_control_button, 0, wx.EXPAND | wx.ALL, 4)
        vbox.Add(advanced_adjustment_button, 0, wx.EXPAND | wx.ALL, 4)
        vbox.Add(advanced_calibration_button, 0, wx.EXPAND | wx.ALL, 4)
        self.SetSizer(vbox)

        scan_button.Bind(wx.EVT_BUTTON, self.on_scan)
        if caps.has_control_workbench:
            advanced_control_button.Bind(wx.EVT_BUTTON, self.on_advanced_control)
        advanced_adjustment_button.Bind(wx.EVT_BUTTON, self.on_advanced_adjustment)
        advanced_calibration_button.Bind(wx.EVT_BUTTON, self.on_advanced_calibration)

    def on_scan(self, event):
        profile.settings['workbench'] = 'scanning'
        parent = self.GetParent().GetParent()
        workbench = parent.parent.workbench[profile.settings['workbench']].name
        parent.parent.update_workbench(workbench)
        parent.Close()

    def on_advanced_control(self, event):
        if 'control' not in self.GetParent().GetParent().parent.workbench:
            return
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
        path = button.GetName()
        if not os.path.isfile(path):
            wx.MessageBox(
                _('File not found:\n{path}').format(path=path),
                _('Open recent'),
                wx.OK | wx.ICON_WARNING,
            )
            return
        profile.settings['workbench'] = 'scanning'
        parent = self.GetParent().GetParent()
        workbench = parent.parent.workbench[profile.settings['workbench']].name
        parent.parent.update_workbench(workbench)
        parent.parent.append_last_file(path)
        parent.parent.workbench['scanning'].scene_view.load_file(path)
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
