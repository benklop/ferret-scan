from __future__ import absolute_import

from collections import OrderedDict

import wx

from ferret_scan.gui.util import gtk_compat
from ferret_scan.util import profile, resources
from ferret_scan.util import system as sys


class ExpandableCollection(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.expandable_panels = OrderedDict()

        # Layout
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.vbox)
        self.Layout()

    def add_panel(self, name, panel, on_selected_callback=None):
        panel = panel(self, on_selected_callback)
        panel.content.Disable()
        panel.set_expand_callback(self._expand_callback)
        self.expandable_panels.update({name: panel})
        self.vbox.Add(panel, 0, wx.ALL ^ wx.TOP | wx.EXPAND, 3)
        return panel

    def init_panels_layout(self):
        values = list(self.expandable_panels.values())
        if len(values) > 0:
            self._expand_callback(values[0])

    def _expand_callback(self, selected_panel):
        if sys.is_windows():
            selected_panel.show_content()
            for panel in self.expandable_panels.values():
                if panel is not selected_panel:
                    panel.hide_content()
        else:
            for panel in self.expandable_panels.values():
                if panel is not selected_panel:
                    panel.hide_content()
            selected_panel.show_content()

    # Engine callbacks
    def update_callbacks(self):
        for panel in self.expandable_panels.values():
            panel.content.update_callbacks()

    def enable_content(self):
        for panel in self.expandable_panels.values():
            panel.content.Enable()

    def disable_content(self):
        for panel in self.expandable_panels.values():
            panel.content.Disable()

    def update_from_profile(self):
        for panel in self.expandable_panels.values():
            panel.enable_restore(True)
            panel.content.update_from_profile()


class ExpandablePanel(wx.Panel):
    def __init__(
        self, parent, title='', selected_callback=None, has_undo=True, has_restore=True, restore_callback=None
    ):
        wx.Panel.__init__(self, parent, size=(-1, -1))

        # Elements
        self.parent = parent
        self.expand_callback = None
        self.selected_callback = selected_callback
        self.undo_objects = []
        self.title = title
        self.title_text = TitleText(self, title)
        self.has_undo = has_undo
        self.has_restore = has_restore
        self.restore_callback = restore_callback
        if self.has_undo:
            self.undo_button = wx.BitmapButton(
                self, wx.NewId(), wx.Bitmap(resources.get_path_for_image('undo.png'), wx.BITMAP_TYPE_ANY)
            )
            self.undo_button.Disable()
        if self.has_restore:
            self.restore_button = wx.BitmapButton(
                self, wx.NewId(), wx.Bitmap(resources.get_path_for_image('restore.png'), wx.BITMAP_TYPE_ANY)
            )

        self.content = ControlCollection(self, self.append_undo, self.release_undo)

        # Layout
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.title_text, 1, wx.ALIGN_CENTER_VERTICAL)
        if self.has_undo:
            self.hbox.Add(self.undo_button, 0, wx.RIGHT | wx.BOTTOM | wx.ALIGN_RIGHT, 5)
        if self.has_restore:
            self.hbox.Add(self.restore_button, 0, wx.RIGHT | wx.BOTTOM | wx.ALIGN_RIGHT, 5)
        self.vbox.Add(self.hbox, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)
        self.vbox.Add(self.content, 1, wx.ALL ^ wx.TOP ^ wx.BOTTOM | wx.EXPAND, 15)
        self.SetSizer(self.vbox)
        self.Layout()

        # Events
        if self.has_undo:
            self.undo_button.Bind(wx.EVT_BUTTON, self.on_undo_button_clicked)
        if self.has_restore:
            self.restore_button.Bind(wx.EVT_BUTTON, self.on_restore_button_clicked)
        self.title_text.title.Bind(wx.EVT_LEFT_DOWN, self.on_title_clicked)

        # Initialize
        self.add_controls()
        self.update_callbacks()

    def add_control(self, _name, _type, tooltip=None):
        self.content.add_control(_name, _type, tooltip)

    def get_control(self, _name):
        return self.content[_name]

    def update_callback(self, _name, _callback):
        self.content.update_callback(_name, _callback)

    def add_controls(self):
        pass

    def update_callbacks(self):
        pass

    def on_selected(self):
        if self.selected_callback is not None:
            self.selected_callback()

    def set_expand_callback(self, expand_callback):
        self.expand_callback = expand_callback

    def select_panel(self, invoke_callback=True):
        """Expand this panel; optionally run the selection callback (e.g. switch pages)."""
        if self.expand_callback is not None:
            self.expand_callback(self)
        if invoke_callback:
            self.on_selected()

    def on_title_clicked(self, event):
        self.select_panel(invoke_callback=True)

    def on_undo_button_clicked(self, event):
        if self.undo():
            self.undo_button.Enable()
        else:
            self.undo_button.Disable()

    def show_content(self):
        self.content.Show()
        if self.has_undo:
            self.undo_button.Show()
        if self.has_restore:
            self.restore_button.Show()
        self.parent.Refresh()
        self.parent.Layout()
        if sys.is_linux():
            gtk_compat.schedule_repaint_burst(self.GetTopLevelParent() or self)

    def hide_content(self):
        self.content.Hide()
        if self.has_undo:
            self.undo_button.Hide()
        if self.has_restore:
            self.restore_button.Hide()
        self.parent.Refresh()
        self.parent.Layout()

    def append_undo(self, _object):
        if self.has_undo:
            self.undo_objects.append(_object)

    def release_undo(self, undo=False, restore=False):
        if self.has_undo and undo:
            self.undo_button.Enable()
        if self.has_restore and restore:
            self.restore_button.Enable()

    def undo(self):
        if len(self.undo_objects) > 0:
            object_to_undo = self.undo_objects.pop()
            object_to_undo.undo()
        return len(self.undo_objects) > 0

    def on_restore_button_clicked(self, event):
        dlg = wx.MessageDialog(
            self,
            _(
                'This will reset all section settings to defaults. '
                'Unless you have saved your current profile, all section settings will be lost!\n'
                'Do you really want to reset?'
            ),
            self.title,
            wx.YES_NO | wx.ICON_QUESTION,
        )
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            self.restore_button.Disable()
            self.content.reset_profile()
            if self.restore_callback:
                self.restore_callback()
            if self.has_undo:
                del self.undo_objects[:]
                self.undo_button.Disable()

    def enable_restore(self, value):
        if hasattr(self, 'restore_button'):
            if value:
                self.restore_button.Enable()
            else:
                self.restore_button.Disable()


class TitleText(wx.Panel):
    def __init__(self, parent, title, hand_cursor=True):
        wx.Panel.__init__(self, parent)

        # Elements
        self.title = wx.StaticText(self, label=title)
        title_font = self.title.GetFont()
        title_font.SetWeight(wx.BOLD)
        self.title.SetFont(title_font)
        self.line = wx.StaticLine(self)

        if hand_cursor:
            self.title.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
            self.line.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.title, 0, wx.ALL ^ wx.TOP ^ wx.BOTTOM | wx.EXPAND, 10)
        vbox.Add(self.line, 1, wx.ALL | wx.EXPAND, 8)
        self.SetSizer(vbox)
        self.Layout()

    def font_normal(self):
        self.title.SetForegroundColour('#717577')
        self.Layout()

    def font_selected(self):
        self.title.SetForegroundColour('#000000')
        self.Layout()


class ControlCollection(wx.Panel):
    def __init__(self, parent, append_undo_callback=None, release_undo_callback=None):
        wx.Panel.__init__(self, parent, size=(100, 100))

        # Elements
        self.control_panels = OrderedDict()
        self.append_undo_callback = append_undo_callback
        self.release_undo_callback = release_undo_callback

        # Layout
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        if sys.is_wx30():
            self.SetSizerAndFit(self.vbox)
        else:
            self.SetSizer(self.vbox)
        self.Layout()

    def __getitem__(self, key):
        return self.control_panels[key]

    def add_control(self, _name, _type, tooltip=None):
        control = _type(self, _name, tooltip)
        control.set_undo_callbacks(self.append_undo_callback, self.release_undo_callback)
        self.control_panels.update({_name: control})
        self.vbox.Add(control, 0, wx.BOTTOM | wx.EXPAND, 5)
        self.vbox.Layout()
        if sys.is_wx30():
            self.SetSizerAndFit(self.vbox)

    def update_callback(self, _name, _callback):
        self.control_panels[_name].set_engine_callback(_callback)

    def reset_profile(self):
        for control in self.control_panels.values():
            control.reset_profile()

    def enable(self, _name):
        self.items[_name].Enable()

    def disable(self, _name):
        self.items[_name].Disable()

    def update_from_profile(self):
        for control in self.control_panels.values():
            control.update_from_profile()

    def show_item(self, _name):
        self.control_panels[_name].Show()
        self.Layout()

    def hide_item(self, _name):
        self.control_panels[_name].Hide()
        self.Layout()


class ControlPanel(wx.Panel):
    def __init__(self, parent, name, tooltip=None):
        wx.Panel.__init__(self, parent)
        self.name = name
        self.setting = profile.settings.get_setting(self.name)
        if tooltip:
            self.SetToolTip(wx.ToolTip(tooltip))

        self.control = None
        self.undo_values = []
        self.engine_callback = None
        self.append_undo_callback = None
        self.release_undo_callback = None

    def set_engine_callback(self, engine_callback=None):
        self.engine_callback = engine_callback

    def set_undo_callbacks(self, append_undo_callback, release_undo_callback):
        self.append_undo_callback = append_undo_callback
        self.release_undo_callback = release_undo_callback

    def append_undo(self):
        if self.append_undo_callback is not None:
            self.append_undo_callback(self)
            self.undo_values.append(profile.settings[self.name])

    def release_undo(self):
        if self.release_undo_callback is not None:
            self.release_undo_callback(undo=True, restore=True)

    def release_restore(self):
        if self.release_undo_callback is not None:
            self.release_undo_callback(restore=True)

    def undo(self):
        if len(self.undo_values) > 0:
            value = self.undo_values.pop()
            self.update_to_profile(value)
            self.set_control_value(value)
            self.set_engine(value)

    def reset_profile(self):
        profile.settings.reset_to_default(self.name)
        self.update_from_profile()
        del self.undo_values[:]

    def update_from_profile(self):
        value = profile.settings[self.name]
        # TODO:
        if (
            self.control is not None
            and not isinstance(self.control, wx.Button)
            and not isinstance(self.control, wx.ToggleButton)
        ):
            self.set_control_value(value)
            self.set_engine(value)

    def set_control_value(self, value):
        self.control.SetValue(value)

    def update_to_profile(self, value):
        profile.settings[self.name] = value

    def set_engine(self, value):
        if self.engine_callback is not None:
            self.engine_callback(value)
