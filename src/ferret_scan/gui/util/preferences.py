import logging
import threading
import time

import wx

from ferret_scan.diy import diy_available
from ferret_scan.revolve import revolve_available
from ferret_scan.runtime_engine import driver
from ferret_scan.util import profile, resources

logger = logging.getLogger(__name__)


class PreferencesDialog(wx.Dialog):
    def __init__(self, basic=False):
        wx.Dialog.__init__(self, None, title=_('Preferences'))

        self.hex_path = None
        self.basic = basic
        self.diy = diy_available()
        self.revolve = revolve_available()
        self.turntable_ui = self.diy or self.revolve

        # Elements
        self.turntable_backend_label = None
        self.turntable_backend_combo = None
        self.revolve_address_label = None
        self.revolve_address_combo = None
        self.camera_id_label = wx.StaticText(self, label=_('Camera ID'))
        self.camera_id_names = driver.camera.get_video_list()
        self.camera_id_combo = wx.ComboBox(self, choices=self.camera_id_names, size=(170, -1), style=wx.CB_READONLY)

        self.serial_name_label = None
        self.serial_name_combo = None
        self.luminosity_label = None
        self.luminosity_combo = None
        self.invert_motor_label = None
        self.invert_motor_check_box = None

        if self.turntable_ui:
            backends = list(profile.settings.get_possible_values('turntable_backend'))
            self.turntable_backend_label = wx.StaticText(self, label=_('Turntable'))
            self.turntable_backend_combo = wx.ComboBox(self, choices=backends, size=(170, -1), style=wx.CB_READONLY)
            current_backend = profile.settings.get('turntable_backend', 'None')
            if current_backend in backends:
                self.turntable_backend_combo.SetValue(current_backend)

        if self.revolve:
            self.revolve_address_label = wx.StaticText(self, label=_('Revopoint BLE address'))
            try:
                from librevolve import discover_turntables_sync

                revolve_addrs = [d.address for d in discover_turntables_sync(timeout=6.0)]
            except Exception:
                revolve_addrs = []
            self.revolve_address_combo = wx.ComboBox(self, choices=revolve_addrs, size=(170, -1))
            current_revolve = profile.settings.get('revolve_device_address', '')
            if current_revolve:
                self.revolve_address_combo.SetValue(current_revolve)

        if self.diy:
            self.serial_name_label = wx.StaticText(self, label=_('Serial name'))
            self.serial_names = driver.board.get_serial_list()
            self.serial_name_combo = wx.ComboBox(self, choices=self.serial_names, size=(170, -1))

            self.luminosity_values = []
            values = profile.settings.get_possible_values('luminosity')
            for value in values:
                self.luminosity_values.append(_(value))
            self.luminosity_dict = dict(zip(self.luminosity_values, values))
            self.luminosity_label = wx.StaticText(self, label=_('Luminosity'))
            self.luminosity_label.SetToolTip(
                wx.ToolTip(_('Change the luminosity until colored lines appear over the chess pattern in the video'))
            )
            self.luminosity_combo = wx.ComboBox(
                self, wx.ID_ANY, choices=self.luminosity_values, size=(170, -1), style=wx.CB_READONLY
            )

        if self.turntable_ui:
            self.invert_motor_label = wx.StaticText(self, label=_('Invert the motor direction'))
            self.invert_motor_check_box = wx.CheckBox(self)

        if not self.basic:
            self.baud_rate_label = wx.StaticText(self, label=_('Baud rate'))
            self.baud_rates = [str(b) for b in profile.settings.get_possible_values('baud_rate')]
            self.baud_rate_combo = wx.ComboBox(self, choices=self.baud_rates, size=(170, -1), style=wx.CB_READONLY)

            self.board_label = None
            self.boards_combo = None
            self.hex_label = None
            self.hex_combo = None
            self.clear_check_box = None
            self.upload_firmware_button = None
            self.gauge = None

            if self.diy:
                self.board_label = wx.StaticText(self, label=_('AVR board'))
                self.boards = profile.settings.get_possible_values('board')
                self.boards_combo = wx.ComboBox(self, choices=self.boards, size=(170, -1), style=wx.CB_READONLY)

                self.hex_label = wx.StaticText(self, label=_('Binary file'))
                self.hex_combo = wx.ComboBox(
                    self,
                    choices=[_('Default'), _('External file...')],
                    value=_('Default'),
                    size=(170, -1),
                    style=wx.CB_READONLY,
                )
                self.clear_check_box = wx.CheckBox(self, label=_('Clear EEPROM'))
                self.upload_firmware_button = wx.Button(self, label=_('Upload firmware'))
                self.gauge = wx.Gauge(self, range=100, size=(180, -1))
                self.gauge.Hide()

                self.enable_firmware_section(not driver.is_connected)

            self.language_label = wx.StaticText(self, label=_('Language'))
            self.languages = [row[1] for row in resources.get_language_options()]
            self.language_combo = wx.ComboBox(
                self, choices=self.languages, value=profile.settings['language'], size=(170, -1), style=wx.CB_READONLY
            )

        self.cancel_button = wx.Button(self, label=_('Cancel'), size=(110, -1))
        self.save_button = wx.Button(self, label=_('Save'), size=(110, -1))

        # Fill data
        current_video_id = profile.settings['camera_id']
        if len(self.camera_id_names) > 0:
            if current_video_id not in self.camera_id_names:
                self.camera_id_combo.SetValue(self.camera_id_names[0])
            else:
                self.camera_id_combo.SetValue(current_video_id)

        if self.diy and self.serial_name_combo is not None:
            current_serial = profile.settings['serial_name']
            if len(self.serial_names) > 0:
                if current_serial not in self.serial_names:
                    self.serial_name_combo.SetValue(self.serial_names[0])
                else:
                    self.serial_name_combo.SetValue(current_serial)

        if not self.basic:
            current_baud_rate = str(profile.settings['baud_rate'])
            self.baud_rate_combo.SetValue(current_baud_rate)

            if self.diy and self.boards_combo is not None:
                current_board = profile.settings['board']
                self.boards_combo.SetValue(current_board)

        if self.diy and self.luminosity_combo is not None:
            current_luminosity = profile.settings['luminosity']
            self.luminosity_combo.SetValue(_(current_luminosity))

        if self.turntable_ui and self.invert_motor_check_box is not None:
            self.invert_motor_check_box.SetValue(profile.settings['invert_motor'])

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)

        self._add_label_control(vbox, self.camera_id_label, self.camera_id_combo)
        if self.turntable_ui and self.turntable_backend_combo is not None:
            self._add_label_control(vbox, self.turntable_backend_label, self.turntable_backend_combo)
        if self.revolve and self.revolve_address_combo is not None:
            self._add_label_control(vbox, self.revolve_address_label, self.revolve_address_combo)
        if self.diy:
            self._add_label_control(vbox, self.serial_name_label, self.serial_name_combo)
        if not self.basic:
            self._add_label_control(vbox, self.baud_rate_label, self.baud_rate_combo)

        if self.turntable_ui:
            if self.diy:
                vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)
                self._add_label_control(vbox, self.luminosity_label, self.luminosity_combo)
            self._add_label_control(vbox, self.invert_motor_label, self.invert_motor_check_box)
            vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)

        if not self.basic:
            if self.diy:
                self._add_label_control(vbox, self.board_label, self.boards_combo)
                self._add_label_control(vbox, self.hex_label, self.hex_combo)

                hbox = wx.BoxSizer(wx.HORIZONTAL)
                hbox.Add(self.upload_firmware_button, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
                hbox.AddStretchSpacer()
                hbox.Add(self.clear_check_box, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
                vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)

                vbox.Add(self.gauge, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)

                vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL ^ wx.TOP, 5)

            self._add_label_control(vbox, self.language_label, self.language_combo)

            vbox.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.cancel_button, 0, wx.ALL ^ wx.RIGHT, 10)
        hbox.Add(self.save_button, 0, wx.ALL, 10)
        vbox.Add(hbox, 0, wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.SetSizerAndFit(vbox)
        self.Centre()
        self.Layout()
        self.Fit()

        # Events
        if not self.basic:
            if self.diy:
                self.hex_combo.Bind(wx.EVT_COMBOBOX, self.on_hex_combo_changed)
                self.upload_firmware_button.Bind(wx.EVT_BUTTON, self.on_upload_firmware)
            self.language_combo.Bind(wx.EVT_COMBOBOX, self.on_language_combo_changed)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_close)
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save_button)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def _add_label_control(self, vbox, label, combo):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)
        hbox.AddStretchSpacer()
        hbox.Add(combo, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)

    def on_hex_combo_changed(self, event):
        value = self.hex_combo.GetValue()
        if value == _('Default'):
            self.hex_path = None
        elif value == _('External file...'):
            dlg = wx.FileDialog(self, _('Select binary file to load'), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            dlg.SetWildcard('hex files (*.hex)|*.hex')
            if dlg.ShowModal() == wx.ID_OK:
                self.hex_path = dlg.GetPath()
                self.hex_combo.SetValue(dlg.GetFilename())
            else:
                self.hex_combo.SetValue(_('Default'))
            dlg.Destroy()

    def on_upload_firmware(self, event):
        if self.serial_name_combo.GetValue() != '':
            self.before_load_firmware()
            baud_rate = self._get_baud_rate(self.boards_combo.GetValue())
            clear_eeprom = self.clear_check_box.GetValue()
            threading.Thread(target=self.load_firmware, args=(baud_rate, clear_eeprom)).start()

    def _get_baud_rate(self, value):
        if value == 'Arduino Uno':
            return 115200
        elif value == 'BT ATmega328':
            return 19200

    def load_firmware(self, hex_baud_rate, clear_eeprom):
        from ferret_scan.util.avr_helpers import AvrDude, AvrError

        try:
            avr_dude = AvrDude(port=profile.settings['serial_name'], baud_rate=hex_baud_rate)
            logger.info('Uploading firmware: ')
            if clear_eeprom:
                avr_dude.flash(clear_eeprom=True)
                time.sleep(3)  # Clear EEPROM
            self.count = -50
            out = avr_dude.flash(hex_path=self.hex_path, callback=self.increment_progress)
            if 'not in sync' in out or 'Invalid' in out or 'is not responding' in out:
                wx.CallAfter(self.wrong_board_message)
            wx.CallAfter(self.after_load_firmware)
        except Exception as e:
            wx.CallAfter(self.after_load_firmware)
            if isinstance(e, AvrError):
                wx.CallAfter(self.avr_error_message)

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
        if value:
            self.upload_firmware_button.Enable()
            self.clear_check_box.Enable()
            self.boards_combo.Enable()
            self.hex_combo.Enable()
        else:
            self.upload_firmware_button.Disable()
            self.clear_check_box.Disable()
            self.boards_combo.Disable()
            self.hex_combo.Disable()

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
        # Update profile
        if len(self.camera_id_combo.GetValue()):
            profile.settings['camera_id'] = self.camera_id_combo.GetValue()
        if self.diy and self.serial_name_combo is not None and len(self.serial_name_combo.GetValue()):
            profile.settings['serial_name'] = self.serial_name_combo.GetValue()

        if self.turntable_ui and self.turntable_backend_combo is not None:
            profile.settings['turntable_backend'] = self.turntable_backend_combo.GetValue()
        if self.revolve and self.revolve_address_combo is not None:
            profile.settings['revolve_device_address'] = self.revolve_address_combo.GetValue()
        if self.turntable_ui and self.invert_motor_check_box is not None:
            profile.settings['invert_motor'] = self.invert_motor_check_box.GetValue()
        if self.diy and self.luminosity_combo is not None:
            luminosity = self.luminosity_dict[self.luminosity_combo.GetValue()]
            profile.settings['luminosity'] = luminosity

        if not self.basic:
            if self.baud_rate_combo.GetValue() in self.baud_rates:
                profile.settings['baud_rate'] = int(self.baud_rate_combo.GetValue())
            if self.diy and self.boards_combo is not None:
                profile.settings['board'] = self.boards_combo.GetValue()
            if profile.settings['language'] != self.language_combo.GetValue():
                profile.settings['language'] = self.language_combo.GetValue()
        profile.settings.save_settings(categories=['preferences'])
        # Update engine
        driver.camera.set_camera_id_from_settings(profile.settings['camera_id'])
        from ferret_scan.engine.driver.board import turntable_backend

        backend = turntable_backend()
        if backend == 'GRBL (Ciclop)' and self.diy:
            driver.board.serial_name = profile.settings['serial_name']
            driver.board.baud_rate = profile.settings['baud_rate']
        if backend == 'Revopoint DAT' and hasattr(driver.board, 'device_address'):
            driver.board.device_address = profile.settings.get('revolve_device_address', '')
        driver.board.motor_invert(profile.settings['invert_motor'])
        if self.diy:
            driver.camera.set_luminosity(profile.settings['luminosity'])
        self.on_close(None)

    def on_close(self, event):
        self.EndModal(wx.ID_OK)
        self.Destroy()
