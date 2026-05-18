from __future__ import absolute_import

import wx

from ferret_scan.gui.util import gtk_compat
from ferret_scan.gui.widgets.panels import ControlPanel
from ferret_scan.util import profile
from ferret_scan.util import system as sys


class Slider(ControlPanel):
    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        self.flag_first_move = True

        # Elements
        self.label = wx.StaticText(self, label=_(self.setting._label), size=(130, -1))
        self.control = wx.Slider(
            self,
            value=profile.settings[name],
            minValue=profile.settings.get_min_value(name),
            maxValue=profile.settings.get_max_value(name),
            size=(150, -1),
            style=wx.SL_LABELS,
        )

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        if sys.is_wx30():
            hbox.Add(self.label, 0, wx.BOTTOM | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
            hbox.AddStretchSpacer()
            hbox.Add(self.control, 0, wx.BOTTOM | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        else:
            hbox.Add(self.label, 0, wx.TOP | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
            hbox.AddStretchSpacer()
            hbox.Add(self.control, 0, wx.TOP | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_COMMAND_SCROLL_LINEUP, self._on_slider)
        self.control.Bind(wx.EVT_COMMAND_SCROLL_LINEDOWN, self._on_slider)
        self.control.Bind(wx.EVT_SCROLL_THUMBRELEASE, self._on_slider_released)
        self.control.Bind(wx.EVT_SCROLL_THUMBTRACK, self._on_slider_tracked)

    def _on_slider(self, event):
        self.append_undo()
        self.release_undo()
        value = self.control.GetValue()
        self.update_to_profile(value)
        self.set_engine(value)

    def _on_slider_released(self, event):
        self.flag_first_move = True
        self.release_undo()
        self.update_to_profile(self.control.GetValue())

    def _on_slider_tracked(self, event):
        if self.flag_first_move:
            self.append_undo()
            self.flag_first_move = False
        self.set_engine(self.control.GetValue())


class ComboBox(ControlPanel):
    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        choices = self.setting._possible_values
        _choices = [_(i) for i in choices]

        self.key_dict = dict(zip(_choices, choices))

        # Elements
        label = wx.StaticText(self, label=_(self.setting._label), size=(130, -1))
        self.control = wx.ComboBox(
            self,
            wx.ID_ANY,
            value=_(profile.settings[self.name]),
            choices=_choices,
            size=(150, -1),
            style=wx.CB_READONLY,
        )

        self.control.SetValue_original = self.control.SetValue
        self.control.SetValue = self.SetValue_overwrite

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.AddStretchSpacer()
        hbox.Add(self.control, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_COMBOBOX, self._on_combo_box_changed)

    def SetValue_overwrite(self, value):
        self.control.SetValue_original(_(str(value)))

    def _on_combo_box_changed(self, event):
        value = self.key_dict[self.control.GetValue()]
        self.update_to_profile(value)
        self.set_engine(value)
        self.release_restore()


class CheckBox(ControlPanel):
    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        fg = gtk_compat.style_panel(self)
        label = wx.StaticText(self, label=_(self.setting._label), size=(130, -1))
        gtk_compat.style_label(label, fg)
        self.control = wx.CheckBox(self, size=(150, -1))
        self.control.SetValue(profile.settings[self.name])
        gtk_compat.style_checkbox(self.control, fg)

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.AddStretchSpacer()
        hbox.Add(self.control, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_CHECKBOX, self._on_check_box_changed)

    def _on_check_box_changed(self, event):
        value = self.control.GetValue()
        self.update_to_profile(value)
        self.set_engine(value)
        self.release_restore()

    def GetValue(self):
        return self.control.GetValue()

    def SetValue(self, value):
        self.control.SetValue(value)
        self.update_to_profile(value)
        self.set_engine(value)


class RadioButton(ControlPanel):
    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        label = wx.StaticText(self, label=_(self.setting._label))
        self.control = wx.RadioButton(self, style=wx.ALIGN_RIGHT)
        self.control.SetValue(profile.settings[self.name])

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.TOP | wx.RIGHT | wx.EXPAND, 15)
        hbox.Add(self.control, 1, wx.TOP | wx.EXPAND, 16)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_RADIOBUTTON, self._on_radio_button_changed)

    def _on_radio_button_changed(self, event):
        value = self.control.GetValue()
        self.update_to_profile(value)
        self.set_engine(value)
        self.release_restore()


class TextBox(ControlPanel):
    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        label = wx.StaticText(self, size=(140, -1), label=_(self.setting._label))
        self.control = wx.TextCtrl(self, size=(120, -1), style=wx.TE_RIGHT)
        self.control.SetValue(profile.settings[self.name])

        # Layout
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.hbox.AddStretchSpacer()
        self.hbox.Add(self.control, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(self.hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_KILL_FOCUS, self._on_text_box_changed)

    def _on_text_box_changed(self, event):
        value = self.control.GetValue()
        self.update_to_profile(value)
        self.set_engine(value)
        self.release_restore()
        event.Skip(True)


class IntLabel(ControlPanel):
    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        label = wx.StaticText(self, size=(130, -1), label=_(self.setting._label))
        self.control = wx.StaticText(self, size=(150, -1), style=wx.TE_RIGHT)
        self.control.SetLabel(str(profile.settings[self.name]))

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 7)
        hbox.Add(self.control, 0, wx.TOP | wx.ALIGN_CENTER_VERTICAL, 4)
        self.SetSizer(hbox)
        self.Layout()

    def update_from_profile(self):
        value = profile.settings[self.name]
        self.control.SetLabel(str(value))


class IntBox(wx.TextCtrl):
    def __init__(self, *args, **kwargs):
        wx.TextCtrl.__init__(self, *args, **kwargs)
        self.old_value = 0

    def SetValue(self, value):
        self.old_value = value
        wx.TextCtrl.SetValue(self, str(int(value)))

    def GetValue(self):
        try:
            value = int(wx.TextCtrl.GetValue(self))
        except Exception:
            value = self.old_value
            self.SetValue(value)
            return value
        else:
            self.old_value = value
            self.SetValue(value)
            return value


class IntTextBox(ControlPanel):
    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        label = wx.StaticText(self, size=(130, -1), label=_(self.setting._label))
        self.control = IntBox(self, size=(150, -1), style=wx.TE_RIGHT)
        self.control.SetValue(profile.settings[self.name])

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.AddStretchSpacer()
        hbox.Add(self.control, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_KILL_FOCUS, self._on_text_box_lost_focus)

    def GetValue(self):
        return self.control.GetValue()

    def SetValue(self, value):
        self.control.SetValue(value)
        self.update_to_profile(value)
        self.set_engine(value)

    def _on_text_box_lost_focus(self, event):
        value = self.GetValue()
        self.SetValue(value)
        self.release_restore()
        event.Skip(True)


class FloatBox(wx.TextCtrl):
    def __init__(self, *args, **kwargs):
        wx.TextCtrl.__init__(self, *args, **kwargs)
        self.old_value = 0.0

    def SetValue(self, value):
        self.old_value = value
        wx.TextCtrl.SetValue(self, str(round(value, 4)))

    def GetValue(self):
        try:
            value = float(wx.TextCtrl.GetValue(self))
        except Exception:
            value = self.old_value
            self.SetValue(value)
            return value
        else:
            self.old_value = value
            self.SetValue(value)
            return value


class FloatTextBox(ControlPanel):
    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        label = wx.StaticText(self, size=(130, -1), label=_(self.setting._label))
        self.control = FloatBox(self, size=(150, -1), style=wx.TE_RIGHT)
        self.control.SetValue(profile.settings[self.name])

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.AddStretchSpacer()
        hbox.Add(self.control, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_KILL_FOCUS, self._on_text_box_lost_focus)

    def _on_text_box_lost_focus(self, event):
        value = self.control.GetValue()
        self.update_to_profile(value)
        self.set_engine(value)
        self.release_restore()
        event.Skip(True)


class FloatBoxArray(wx.Panel):
    def __init__(self, parent, value, size, onedit_callback=None):
        wx.Panel.__init__(self, parent)
        self.onedit_callback = onedit_callback
        self.value = value
        self.size = size
        if len(self.value.shape) == 1:
            self.r, self.c = 1, self.value.shape[0]
        elif len(self.value.shape) == 2:
            self.r, self.c = self.value.shape
        self.texts = [[0 for j in range(self.c)] for i in range(self.r)]

        ibox = wx.BoxSizer(wx.VERTICAL)
        for i in range(self.r):
            jbox = wx.BoxSizer(wx.HORIZONTAL)
            for j in range(self.c):
                self.texts[i][j] = FloatBox(self, size=self.size, style=wx.TE_RIGHT)
                if self.r == 1:
                    self.texts[i][j].SetValue(self.value[j])
                else:
                    self.texts[i][j].SetValue(self.value[i][j])
                self.texts[i][j].Bind(wx.EVT_KILL_FOCUS, self._on_edit_lost_focus)
                # self.texts[i][j].SetEditable(False)
                # self.texts[i][j].Disable()
                jbox.Add(self.texts[i][j], 1, wx.ALL | wx.EXPAND, 2)
            ibox.Add(jbox, 1, wx.ALL | wx.EXPAND, 1)
        self.SetSizer(ibox)
        self.Layout()

    def SetValue(self, value):
        self.value = value
        for i in range(self.r):
            for j in range(self.c):
                if self.r == 1:
                    self.texts[i][j].SetValue(self.value[j])
                else:
                    self.texts[i][j].SetValue(self.value[i][j])

    def GetValue(self):
        for i in range(self.r):
            for j in range(self.c):
                if self.r == 1:
                    self.value[j] = self.texts[i][j].GetValue()
                else:
                    self.value[i][j] = self.texts[i][j].GetValue()
        return self.value

    def _on_edit_lost_focus(self, event):
        if self.onedit_callback is not None:
            self.onedit_callback(event)
        event.Skip(True)


class FloatTextBoxArray(ControlPanel):
    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        label = wx.StaticText(self, size=(140, -1), label=_(self.setting._label))
        self.control = FloatBoxArray(
            self, value=profile.settings[name], size=(50, -1), onedit_callback=self._on_text_box_lost_focus
        )

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(label, 0, wx.BOTTOM | wx.EXPAND, 3)
        vbox.AddStretchSpacer()
        vbox.Add(self.control, 0, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(vbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_KILL_FOCUS, self._on_text_box_lost_focus)

    def _on_text_box_lost_focus(self, event):
        value = self.control.GetValue()
        self.update_to_profile(value)
        self.set_engine(value)
        self.release_restore()
        event.Skip(True)


class FloatLabel(ControlPanel):
    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        label = wx.StaticText(self, size=(160, -1), label=_(self.setting._label))
        self.control = wx.StaticText(self, size=(100, -1), style=wx.TE_RIGHT)
        self.control.SetLabel(str(round(profile.settings[self.name], 4)))

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, 0, wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 7)
        hbox.Add(self.control, 0, wx.TOP | wx.ALIGN_CENTER_VERTICAL, 4)
        self.SetSizer(hbox)
        self.Layout()

    def update_from_profile(self):
        value = profile.settings[self.name]
        self.control.SetLabel(str(round(value, 3)))


class FloatStaticArray(wx.Panel):
    def __init__(self, parent, value, size):
        wx.Panel.__init__(self, parent)
        self.value = value
        self.size = size
        if len(self.value.shape) == 1:
            self.r, self.c = 1, self.value.shape[0]
        elif len(self.value.shape) == 2:
            self.r, self.c = self.value.shape
        self.texts = [[0 for j in range(self.c)] for i in range(self.r)]

        ibox = wx.BoxSizer(wx.VERTICAL)
        for i in range(self.r):
            jbox = wx.BoxSizer(wx.HORIZONTAL)
            for j in range(self.c):
                self.texts[i][j] = wx.StaticText(self, size=self.size, style=wx.TE_RIGHT)
                if self.r == 1:
                    self.texts[i][j].SetLabel(str(round(self.value[j], 4)))
                else:
                    self.texts[i][j].SetLabel(str(round(self.value[i][j], 4)))
                jbox.Add(self.texts[i][j], 1, wx.ALL | wx.EXPAND, 2)
            ibox.Add(jbox, 1, wx.ALL | wx.EXPAND, 1)
        self.SetSizer(ibox)
        self.Layout()

    def SetValue(self, value):
        self.value = value
        for i in range(self.r):
            for j in range(self.c):
                if self.r == 1:
                    self.texts[i][j].SetLabel(str(round(self.value[j], 4)))
                else:
                    self.texts[i][j].SetLabel(str(round(self.value[i][j], 4)))


class FloatLabelArray(ControlPanel):
    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        label = wx.StaticText(self, size=(140, -1), label=_(self.setting._label))
        self.control = FloatStaticArray(self, value=profile.settings[name], size=(50, -1))

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(label, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 2)
        vbox.AddStretchSpacer()
        vbox.Add(self.control, 0, wx.TOP | wx.EXPAND, 10)
        self.SetSizer(vbox)
        self.Layout()


class Button(ControlPanel):
    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        gtk_compat.style_panel(self)
        self.control = wx.Button(self, label=_(self.setting._label))
        gtk_compat.style_button(self.control)

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.control, 1, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.EXPAND, 2)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_BUTTON, self._on_button_clicked)

    def _on_button_clicked(self, event):
        if self.engine_callback is not None:
            self.engine_callback()

    def set_engine(self, value):
        pass


class CallbackButton(ControlPanel):
    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        gtk_compat.style_panel(self)
        self.control = wx.Button(self, label=_(self.setting._label))
        gtk_compat.style_button(self.control)

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.control, 1, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.EXPAND, 2)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_BUTTON, self._on_button_clicked)

    def _on_button_clicked(self, event):
        if self.engine_callback is not None:
            self.control.Disable()
            self.wait_cursor = wx.BusyCursor()
            self.engine_callback(lambda r: wx.CallAfter(self._on_finish_callback, r))

    def _on_finish_callback(self, ret):
        self.control.Enable()
        del self.wait_cursor


class ToggleButton(ControlPanel):
    def __init__(self, parent, name, engine_callback=None):
        ControlPanel.__init__(self, parent, name, engine_callback)

        # Elements
        self.control = wx.ToggleButton(self, label=_(self.setting._label))

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.control, 1, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.EXPAND, 2)
        self.SetSizer(hbox)
        self.Layout()

        # Events
        self.control.Bind(wx.EVT_TOGGLEBUTTON, self._on_button_toggle)

    def _on_button_toggle(self, event):
        if self.engine_callback is not None:
            if event.IsChecked():
                function = 0
            else:
                function = 1

            if self.engine_callback[function] is not None:
                self.engine_callback[function]()
