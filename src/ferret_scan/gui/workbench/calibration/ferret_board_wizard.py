"""Wizard UI for CR-Scan Ferret optional calibration board."""

from __future__ import annotations

import wx

from ferret_scan.engine.calibration.ferret_board import get_ferret_board_calibration
from ferret_scan.runtime_engine import driver
from ferret_scan.util import profile


class FerretBoardWizard(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(
            self,
            parent,
            title=_('Ferret calibration board'),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
            size=(720, 520),
        )
        self._engine = get_ferret_board_calibration()
        self._step = 0
        self._build_ui()
        self.CentreOnParent()

    def _build_ui(self):
        self.content = wx.Panel(self)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)

        self.sn_label = wx.StaticText(self.content, label=_('Calibration board serial number (back of board):'))
        self.sn_text = wx.TextCtrl(self.content, value=profile.settings.get('ferret_calibration_board_sn', ''))
        self.start_over_btn = wx.Button(self.content, label=_('Start over'))

        self.temp_label = wx.StaticText(self.content, label='')
        self.hint_xy = wx.StaticText(self.content, label='')
        self.hint_z = wx.StaticText(self.content, label='')
        self.pose_label = wx.StaticText(self.content, label='')
        self.status_label = wx.StaticText(self.content, label='')

        self.content_sizer.Add(self.sn_label, 0, wx.ALL, 8)
        self.content_sizer.Add(self.sn_text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        self.content_sizer.Add(self.start_over_btn, 0, wx.ALL, 8)
        self.content_sizer.Add(self.temp_label, 0, wx.ALL, 8)
        self.content_sizer.Add(self.hint_xy, 0, wx.ALL, 8)
        self.content_sizer.Add(self.hint_z, 0, wx.ALL, 8)
        self.content_sizer.Add(self.pose_label, 0, wx.ALL, 8)
        self.content_sizer.Add(self.status_label, 0, wx.ALL, 8)
        self.content.SetSizer(self.content_sizer)

        self.prev_btn = wx.Button(self, label=_('Back'))
        self.next_btn = wx.Button(self, label=_('Next'))
        self.cancel_btn = wx.Button(self, label=_('Cancel'))

        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        btn_row.Add(self.cancel_btn, 0, wx.ALL, 6)
        btn_row.AddStretchSpacer()
        btn_row.Add(self.prev_btn, 0, wx.ALL, 6)
        btn_row.Add(self.next_btn, 0, wx.ALL, 6)

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(self.content, 1, wx.EXPAND | wx.ALL, 8)
        root.Add(btn_row, 0, wx.EXPAND)
        self.SetSizer(root)

        self.prev_btn.Bind(wx.EVT_BUTTON, self._on_back)
        self.next_btn.Bind(wx.EVT_BUTTON, self._on_next)
        self.cancel_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        self.start_over_btn.Bind(wx.EVT_BUTTON, self._on_start_over)
        self._refresh_step()

    def _on_start_over(self, event):
        if (
            wx.MessageBox(
                _('Clear saved poses for this board and start again?'),
                _('Start over'),
                wx.YES_NO | wx.ICON_QUESTION,
            )
            != wx.YES
        ):
            return
        self._engine.reset_session(delete_files=True)
        self._step = 0
        self._refresh_step()

    def _refresh_step(self):
        if self._step == 0:
            self.sn_label.Show()
            self.sn_text.Show()
            self.start_over_btn.Show()
            self.temp_label.SetLabel(
                _(
                    'Place the calibration board on a table with the arrow facing up. '
                    'Preheat the scanner ~30 minutes for best accuracy. '
                    'See doc/FERRET_BOARD_CALIBRATION.md for status.'
                )
            )
            self.hint_xy.Hide()
            self.hint_z.Hide()
            self.pose_label.Hide()
            self.status_label.Hide()
            self.prev_btn.Disable()
            self.next_btn.SetLabel(_('Start'))
        elif self._step == 1 and not self._engine.poses_done:
            self.sn_label.Hide()
            self.sn_text.Hide()
            self.start_over_btn.Hide()
            self.hint_xy.Show()
            self.hint_z.Show()
            self.pose_label.Show()
            self.status_label.Show()
            pose = self._engine.current_pose
            n = self._engine.current_pose_index + 1
            total = self._engine.pose_count
            self.pose_label.SetLabel(_('Pose {n} of {total}').format(n=n, total=total))
            self.hint_xy.SetLabel(_('Horizontal: {hint}').format(hint=pose['hint_xy']))
            self.hint_z.SetLabel(_('Height: {hint}').format(hint=pose['hint_z']))
            board_sn = profile.settings.get('ferret_calibration_board_sn', '')
            last_temp = None
            if self._engine.session.captures:
                last_temp = self._engine.session.captures[-1].temperature_c
            temp_txt = _('{temp} °C').format(temp=f'{last_temp:.1f}') if last_temp is not None else _('n/a')
            self.temp_label.SetLabel(
                _('Board SN: {sn}  |  Last capture temperature: {temp}').format(sn=board_sn, temp=temp_txt)
            )
            self.status_label.SetLabel(
                _(
                    'Align the scanner with the board, then press Capture pose. Visual guide overlays are not implemented yet.'
                )
            )
            self.prev_btn.Enable()
            self.next_btn.SetLabel(_('Capture pose'))
        else:
            self.sn_label.Hide()
            self.sn_text.Hide()
            self.start_over_btn.Hide()
            self.hint_xy.Hide()
            self.hint_z.Hide()
            self.pose_label.Hide()
            self.status_label.Show()
            if not self._engine.session.complete and self._engine.poses_done:
                self._engine.finish_acquisition()
            msg = self._engine.run_compute()
            self.temp_label.SetLabel(_('Capture saved'))
            self.status_label.SetLabel(msg)
            self.next_btn.SetLabel(_('Close'))
            self.prev_btn.Disable()

        self.content.Layout()
        self.Layout()

    def _on_back(self, event):
        if self._step == 1 and self._engine.session.captures:
            if (
                wx.MessageBox(
                    _('Going back will not remove captured poses. Use Start over to clear them.'),
                    _('Back'),
                    wx.OK | wx.CANCEL | wx.ICON_INFORMATION,
                )
                != wx.OK
            ):
                return
        if self._step > 0:
            self._step -= 1
            self._refresh_step()

    def _on_next(self, event):
        if self._step == 0:
            sn = self.sn_text.GetValue().strip()
            if not sn:
                wx.MessageBox(
                    _('Enter the serial number from the back of the calibration board.'),
                    _('Board SN required'),
                    wx.OK | wx.ICON_WARNING,
                )
                return
            if not driver.is_connected:
                wx.MessageBox(
                    _('Connect the scanner before starting calibration.'),
                    _('Not connected'),
                    wx.OK | wx.ICON_WARNING,
                )
                return
            self._engine.start(sn)
            self._step = 1
            self._refresh_step()
            return

        if self._engine.poses_done:
            self.EndModal(wx.ID_OK)
            return

        try:
            self._engine.capture_current_pose()
        except Exception as exc:
            wx.MessageBox(str(exc), _('Capture failed'), wx.OK | wx.ICON_ERROR)
            return

        if self._engine.poses_done:
            self._refresh_step()
        else:
            self._refresh_step()
