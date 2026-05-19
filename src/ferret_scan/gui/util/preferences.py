import copy
import logging
import threading
import time

import wx

from ferret_scan.gui.util.preference_builder import (
    PreferenceControl,
    build_control,
    read_control_value,
    write_control_value,
)
from ferret_scan.hardware.migration import migrate_hardware_settings
from ferret_scan.hardware.registry import get_registry
from ferret_scan.runtime_engine import driver
from ferret_scan.util import profile, resources

logger = logging.getLogger(__name__)

_HEX_DEFAULT = 'default'
_HEX_EXTERNAL = 'external'


class PreferencesDialog(wx.Dialog):
    def __init__(self, basic=False, parent=None):
        wx.Dialog.__init__(self, parent, title=_('Preferences'))

        self.hex_path = None
        self.hex_source = _HEX_DEFAULT
        self.basic = basic
        self.registry = get_registry()
        self._preference_controls: list[PreferenceControl] = []
        self._advanced_controls: list[PreferenceControl] = []
        self._snapshot = self._build_snapshot()
        self._pending_scanner_id = self.registry.active_scanner_id()
        self._pending_turntable_id = self.registry.active_turntable_id()

        vbox = wx.BoxSizer(wx.VERTICAL)

        device_box = wx.StaticBox(self, label=_('Devices'))
        device_sizer = wx.StaticBoxSizer(device_box, wx.VERTICAL)

        self.scanner_label = wx.StaticText(self, label=_('Scanner'))
        scanners = self.registry.available_scanners()
        self.scanner_id_by_label = {s.label: s.id for s in scanners}
        self.scanner_label_by_id = {s.id: s.label for s in scanners}
        self.scanner_combo = wx.ComboBox(
            self, choices=[s.label for s in scanners], size=(220, -1), style=wx.CB_READONLY
        )
        self.scanner_combo.SetValue(self.scanner_label_by_id.get(self._pending_scanner_id, scanners[0].label))

        self.turntable_label = wx.StaticText(self, label=_('Turntable'))
        turntables = self.registry.available_turntables()
        self.turntable_id_by_label = {t.label: t.id for t in turntables}
        self.turntable_label_by_id = {t.id: t.label for t in turntables}
        self.turntable_combo = wx.ComboBox(
            self, choices=[t.label for t in turntables], size=(220, -1), style=wx.CB_READONLY
        )
        self.turntable_combo.SetValue(self.turntable_label_by_id.get(self._pending_turntable_id, turntables[0].label))

        self._add_label_control(device_sizer, self.scanner_label, self.scanner_combo)
        self._add_label_control(device_sizer, self.turntable_label, self.turntable_combo)
        vbox.Add(device_sizer, 0, wx.EXPAND | wx.ALL, 8)

        self.scanner_combo.Bind(wx.EVT_COMBOBOX, self._on_device_changed)
        self.turntable_combo.Bind(wx.EVT_COMBOBOX, self._on_device_changed)

        self.fields_panel = wx.Panel(self)
        self.fields_sizer = wx.BoxSizer(wx.VERTICAL)
        self.fields_panel.SetSizer(self.fields_sizer)
        vbox.Add(self.fields_panel, 0, wx.EXPAND | wx.ALL, 4)

        self._rebuild_field_controls()

        if not self.basic:
            self.advanced_panel = wx.Panel(self)
            self.advanced_sizer = wx.BoxSizer(wx.VERTICAL)
            self.advanced_panel.SetSizer(self.advanced_sizer)
            vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
            adv_label = wx.StaticText(self, label=_('Advanced'))
            font = adv_label.GetFont()
            font.SetWeight(wx.BOLD)
            adv_label.SetFont(font)
            vbox.Add(adv_label, 0, wx.LEFT | wx.TOP, 8)
            vbox.Add(self.advanced_panel, 0, wx.EXPAND | wx.ALL, 4)
            self._rebuild_advanced_controls()

            if self._pending_turntable_id == 'ciclop_grbl':
                self._build_firmware_section(vbox)

            self.language_label = wx.StaticText(self, label=_('Language'))
            self.languages = [row[1] for row in resources.get_language_options()]
            self.language_combo = wx.ComboBox(
                self, choices=self.languages, value=profile.settings['language'], size=(220, -1), style=wx.CB_READONLY
            )
            self._add_label_control(vbox, self.language_label, self.language_combo)
            self.language_combo.Bind(wx.EVT_COMBOBOX, self.on_language_combo_changed)

        self.cancel_button = wx.Button(self, label=_('Cancel'), size=(110, -1))
        self.save_button = wx.Button(self, label=_('Save'), size=(110, -1))
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.cancel_button, 0, wx.ALL ^ wx.RIGHT, 10)
        hbox.Add(self.save_button, 0, wx.ALL, 10)
        vbox.Add(hbox, 0, wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.SetSizerAndFit(vbox)
        self.Centre()
        self.Layout()
        self.Fit()

        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save_button)
        self.Bind(wx.EVT_CLOSE, self.on_cancel)

    def _preference_keys(self):
        keys = {'scanner_id', 'turntable_id', 'language', 'board'}
        for backend in list(self.registry._scanners.values()) + list(self.registry._turntables.values()):
            for field in backend.preference_fields():
                keys.add(field.key)
        return keys

    def _build_snapshot(self):
        snap = {}
        for key in self._preference_keys():
            if profile.settings.setting_exists(key):
                val = profile.settings[key]
                if hasattr(val, 'copy'):
                    snap[key] = val.copy()
                else:
                    snap[key] = copy.copy(val)
        return snap

    def _restore_snapshot(self):
        for key, val in self._snapshot.items():
            if profile.settings.setting_exists(key):
                profile.settings[key] = val

    def _on_device_changed(self, event):
        sl = self.scanner_combo.GetValue()
        tl = self.turntable_combo.GetValue()
        if sl in self.scanner_id_by_label:
            self._pending_scanner_id = self.scanner_id_by_label[sl]
        if tl in self.turntable_id_by_label:
            self._pending_turntable_id = self.turntable_id_by_label[tl]
        self._rebuild_field_controls()
        if not self.basic and hasattr(self, 'advanced_sizer'):
            self._rebuild_advanced_controls()

    def _field_list(self, advanced: bool):
        return self.registry.preference_fields(
            advanced=advanced,
            scanner_id=self._pending_scanner_id,
            turntable_id=self._pending_turntable_id,
        )

    def _clear_sizer(self, sizer):
        panel = self.fields_panel if sizer is self.fields_sizer else self.advanced_panel
        for child in list(panel.GetChildren()):
            child.Destroy()
        sizer.Clear(True)

    def _rebuild_field_controls(self):
        self._clear_sizer(self.fields_sizer)
        self._preference_controls = []
        for field in self._field_list(advanced=False):
            if field.key in ('scanner_id', 'turntable_id'):
                continue
            pc = build_control(self.fields_panel, field)
            self._preference_controls.append(pc)
            self._add_label_control(self.fields_sizer, pc.label, pc.control)
        self.fields_panel.Layout()

    def _rebuild_advanced_controls(self):
        if self.basic:
            return
        self._clear_sizer(self.advanced_sizer)
        self._advanced_controls = []
        for field in self._field_list(advanced=True):
            if field.key in ('scanner_id', 'turntable_id', 'ferret_calibration_board_sn'):
                continue
            pc = build_control(self.advanced_panel, field)
            self._advanced_controls.append(pc)
            self._add_label_control(self.advanced_sizer, pc.label, pc.control)
        self.advanced_panel.Layout()

    def _build_firmware_section(self, vbox):
        self.board_label = wx.StaticText(self, label=_('AVR board'))
        self.boards = profile.settings.get_possible_values('board')
        self.boards_combo = wx.ComboBox(self, choices=self.boards, size=(220, -1), style=wx.CB_READONLY)
        self.boards_combo.SetValue(profile.settings['board'])

        self.hex_label = wx.StaticText(self, label=_('Binary file'))
        self._hex_labels = [_('Default'), _('External file...')]
        self.hex_combo = wx.ComboBox(
            self,
            choices=self._hex_labels,
            value=self._hex_labels[0],
            size=(220, -1),
            style=wx.CB_READONLY,
        )
        self.clear_check_box = wx.CheckBox(self, label=_('Clear EEPROM'))
        self.upload_firmware_button = wx.Button(self, label=_('Upload firmware'))
        self.gauge = wx.Gauge(self, range=100, size=(220, -1))
        self.gauge.Hide()
        self.enable_firmware_section(not driver.is_connected)

        self._add_label_control(vbox, self.board_label, self.boards_combo)
        self._add_label_control(vbox, self.hex_label, self.hex_combo)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.upload_firmware_button, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(self.clear_check_box, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)
        vbox.Add(self.gauge, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)

        self.hex_combo.Bind(wx.EVT_COMBOBOX, self.on_hex_combo_changed)
        self.upload_firmware_button.Bind(wx.EVT_BUTTON, self.on_upload_firmware)

    def _add_label_control(self, vbox, label, combo):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(combo, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 8)

    def on_hex_combo_changed(self, event):
        idx = self.hex_combo.GetSelection()
        if idx == 1:
            self.hex_source = _HEX_EXTERNAL
            dlg = wx.FileDialog(self, _('Select binary file to load'), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            dlg.SetWildcard('hex files (*.hex)|*.hex')
            if dlg.ShowModal() == wx.ID_OK:
                self.hex_path = dlg.GetPath()
                self.hex_combo.SetValue(dlg.GetFilename())
            else:
                self.hex_source = _HEX_DEFAULT
                self.hex_combo.SetSelection(0)
            dlg.Destroy()
        else:
            self.hex_source = _HEX_DEFAULT
            self.hex_path = None
            self.hex_combo.SetSelection(0)

    def on_upload_firmware(self, event):
        serial_pc = next(
            (p for p in self._preference_controls + self._advanced_controls if p.field.key == 'serial_name'), None
        )
        serial = read_control_value(serial_pc) if serial_pc else profile.settings.get('serial_name', '')
        if not serial:
            wx.MessageBox(
                _('Select a serial port before uploading firmware.'),
                _('Serial required'),
                wx.OK | wx.ICON_WARNING,
            )
            return
        self.before_load_firmware()
        baud_rate = self._get_baud_rate(self.boards_combo.GetValue())
        clear_eeprom = self.clear_check_box.GetValue()
        threading.Thread(target=self.load_firmware, args=(serial, baud_rate, clear_eeprom)).start()

    def _get_baud_rate(self, value):
        if value == 'Arduino Uno':
            return 115200
        if value == 'BT ATmega328':
            return 19200
        return 115200

    def load_firmware(self, port, hex_baud_rate, clear_eeprom):
        from ferret_scan.util.avr_helpers import AvrDude, AvrError

        try:
            avr_dude = AvrDude(port=port, baud_rate=hex_baud_rate)
            logger.info('Uploading firmware to %s', port)
            if clear_eeprom:
                avr_dude.flash(clear_eeprom=True)
                time.sleep(3)
            self.count = -50
            out = avr_dude.flash(hex_path=self.hex_path, callback=self.increment_progress)
            if 'not in sync' in out or 'Invalid' in out or 'is not responding' in out:
                wx.CallAfter(self.wrong_board_message)
            wx.CallAfter(self.after_load_firmware)
        except Exception as e:
            wx.CallAfter(self.after_load_firmware)
            if isinstance(e, AvrError):
                wx.CallAfter(self.avr_error_message)
            else:
                wx.CallAfter(lambda: wx.MessageBox(str(e), _('Firmware upload failed'), wx.OK | wx.ICON_ERROR))

    def increment_progress(self):
        self.count += 1
        if self.count >= 0:
            wx.CallAfter(self.gauge.SetValue, self.count)

    def avr_error_message(self):
        dlg = wx.MessageDialog(
            self,
            _('Avrdude is not installed. Please, install it on your system'),
            _('Avrdude not installed'),
            wx.OK | wx.ICON_ERROR,
        )
        dlg.ShowModal()
        dlg.Destroy()

    def wrong_board_message(self):
        dlg = wx.MessageDialog(
            self,
            _('Probably you have selected the wrong board. Select another board'),
            _('Wrong board'),
            wx.OK | wx.ICON_ERROR,
        )
        dlg.ShowModal()
        dlg.Destroy()

    def enable_firmware_section(self, value):
        self.upload_firmware_button.Enable(value)
        self.clear_check_box.Enable(value)
        self.boards_combo.Enable(value)
        self.hex_combo.Enable(value)

    def before_load_firmware(self):
        self.enable_firmware_section(False)
        self.cancel_button.Disable()
        self.save_button.Disable()
        self.gauge.SetValue(0)
        self.gauge.Show()
        self.wait_cursor = wx.BusyCursor()
        self.GetSizer().Layout()
        self.SetSizerAndFit(self.GetSizer())

    def after_load_firmware(self):
        self.enable_firmware_section(True)
        self.cancel_button.Enable()
        self.save_button.Enable()
        self.gauge.Hide()
        del self.wait_cursor
        self.GetSizer().Layout()
        self.SetSizerAndFit(self.GetSizer())

    def on_language_combo_changed(self, event):
        if profile.settings['language'] != self.language_combo.GetValue():
            wx.MessageBox(
                _('You need to restart the application for the changes to take effect'),
                _('Language modified'),
                wx.OK | wx.ICON_INFORMATION,
            )

    def on_save_button(self, event):
        self.registry.set_active_scanner(self._pending_scanner_id)
        self.registry.set_active_turntable(self._pending_turntable_id)

        for pc in self._preference_controls + self._advanced_controls:
            write_control_value(pc, read_control_value(pc))

        if not self.basic:
            if hasattr(self, 'boards_combo'):
                profile.settings['board'] = self.boards_combo.GetValue()
            if profile.settings['language'] != self.language_combo.GetValue():
                profile.settings['language'] = self.language_combo.GetValue()

        migrate_hardware_settings(profile.settings)
        profile.settings.save_settings(categories=['preferences'])
        driver.reset()
        parent = self.GetParent()
        if parent is not None and hasattr(parent, 'initialize_driver'):
            parent.initialize_driver()
        if parent is not None and hasattr(parent, 'refresh_device_ui'):
            parent.refresh_device_ui()
        self.EndModal(wx.ID_OK)
        self.Destroy()

    def on_cancel(self, event):
        self._restore_snapshot()
        self.EndModal(wx.ID_CANCEL)
        self.Destroy()
