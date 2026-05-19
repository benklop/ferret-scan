"""Build wx controls from hardware PreferenceField metadata."""

from __future__ import annotations

import logging
import threading
from typing import Any, List, Tuple

import wx

from ferret_scan.hardware.types import PreferenceField, WidgetType
from ferret_scan.runtime_engine import driver
from ferret_scan.util import profile

logger = logging.getLogger(__name__)


class PreferenceControl:
    def __init__(self, field: PreferenceField, label: wx.StaticText, control: wx.Control, extra=None):
        self.field = field
        self.label = label
        self.control = control
        self.extra = extra


def _luminosity_choices() -> Tuple[str, ...]:
    return tuple(profile.settings.get_possible_values('luminosity'))


def resolve_choices(field: PreferenceField) -> List[str]:
    if field.choices_fn == 'video_list':
        return list(driver.camera.get_video_list())
    if field.choices_fn == 'serial_list':
        return list(driver.board.get_serial_list())
    if field.choices_fn == 'revolve_address_list':
        return []
    if field.choices:
        return list(field.choices)
    if field.key == 'luminosity':
        return list(_luminosity_choices())
    values = profile.settings.get_possible_values(field.key)
    if values:
        return [str(v) for v in values]
    return []


def _populate_revolve_combo(combo: wx.ComboBox, addresses: List[str], current: str) -> None:
    combo.Clear()
    for addr in addresses:
        combo.Append(addr)
    if current:
        combo.SetValue(current)
    elif addresses:
        combo.SetSelection(0)


def start_revolve_scan(combo: wx.ComboBox, current: str = '') -> None:
    combo.Clear()
    combo.Append(_('Scanning…'))
    combo.SetSelection(0)
    combo.Enable(False)

    def worker():
        addrs: List[str] = []
        try:
            from librevolve import discover_turntables_sync

            addrs = [d.address for d in discover_turntables_sync(timeout=6.0)]
        except Exception:
            logger.debug('BLE scan failed', exc_info=True)

        def apply():
            if combo:
                combo.Enable(True)
                _populate_revolve_combo(combo, addrs, current)

        wx.CallAfter(apply)

    threading.Thread(target=worker, daemon=True).start()


def build_control(parent: wx.Window, field: PreferenceField) -> PreferenceControl:
    label = wx.StaticText(parent, label=field.label)
    if field.tooltip:
        label.SetToolTip(wx.ToolTip(field.tooltip))

    widget = field.widget
    if widget == WidgetType.CHECK:
        ctrl = wx.CheckBox(parent)
        if profile.settings.setting_exists(field.key):
            ctrl.SetValue(bool(profile.settings[field.key]))
        return PreferenceControl(field, label, ctrl)

    if widget == WidgetType.COMBO:
        if field.choices_fn == 'revolve_address_list':
            ctrl = wx.ComboBox(parent, size=(220, -1))
            current = str(profile.settings.get(field.key, ''))
            start_revolve_scan(ctrl, current)
            return PreferenceControl(field, label, ctrl)

        choices = resolve_choices(field)
        style = wx.CB_READONLY
        ctrl = wx.ComboBox(parent, choices=choices, size=(220, -1), style=style)
        current = str(profile.settings.get(field.key, ''))
        if current:
            ctrl.SetValue(current)
        elif choices:
            ctrl.SetValue(choices[0])
        return PreferenceControl(field, label, ctrl)

    if widget == WidgetType.SPIN_FLOAT:
        min_v = float(field.min_value or 0)
        max_v = float(field.max_value or 100)
        ctrl = wx.SpinCtrlDouble(parent, min=min_v, max=max_v, inc=0.5, size=(220, -1))
        ctrl.SetValue(float(profile.settings.get(field.key, min_v)))
        return PreferenceControl(field, label, ctrl)

    if widget == WidgetType.SPIN_INT:
        min_v = int(field.min_value or 0)
        max_v = int(field.max_value or 100)
        ctrl = wx.SpinCtrl(parent, min=min_v, max=max_v, size=(220, -1))
        ctrl.SetValue(int(profile.settings.get(field.key, min_v)))
        return PreferenceControl(field, label, ctrl)

    if widget == WidgetType.PATH:
        row = wx.Panel(parent)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        ctrl = wx.TextCtrl(row, value=str(profile.settings.get(field.key, '')), size=(170, -1))
        browse = wx.Button(row, label='…', size=(40, -1))

        def on_browse(event):
            dlg = wx.DirDialog(parent, _('Select directory'))
            if dlg.ShowModal() == wx.ID_OK:
                ctrl.SetValue(dlg.GetPath())
            dlg.Destroy()

        browse.Bind(wx.EVT_BUTTON, on_browse)
        hbox.Add(ctrl, 1, wx.EXPAND | wx.RIGHT, 4)
        hbox.Add(browse, 0)
        row.SetSizer(hbox)
        return PreferenceControl(field, label, row, extra=ctrl)

    ctrl = wx.TextCtrl(parent, value=str(profile.settings.get(field.key, '')), size=(220, -1))
    return PreferenceControl(field, label, ctrl)


def read_control_value(pc: PreferenceControl) -> Any:
    field = pc.field
    if field.widget == WidgetType.PATH and pc.extra is not None:
        return pc.extra.GetValue()
    ctrl = pc.control
    if field.widget == WidgetType.CHECK:
        return ctrl.GetValue()
    if field.widget == WidgetType.COMBO:
        val = ctrl.GetValue()
        if val == _('Scanning…'):
            return profile.settings.get(field.key, '')
        return val
    if field.widget == WidgetType.SPIN_FLOAT:
        return float(ctrl.GetValue())
    if field.widget == WidgetType.SPIN_INT:
        return int(ctrl.GetValue())
    if isinstance(ctrl, wx.Panel):
        return ''
    return ctrl.GetValue()


def write_control_value(pc: PreferenceControl, value: Any) -> None:
    if not profile.settings.setting_exists(pc.field.key):
        return
    profile.settings[pc.field.key] = value
