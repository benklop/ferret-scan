# -*- coding: utf-8 -*-
# GTK/wxGTK workarounds (Fedora dark theme: widgets invisible until hover).

from __future__ import absolute_import

import wx

from ferret_scan.util import system as sys


def walk_widgets(root):
    stack = [root]
    while stack:
        window = stack.pop()
        yield window
        stack.extend(window.GetChildren())


def dialog_colours():
    return (
        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW),
        wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT),
    )


def style_panel(panel, fg=None, custom_paint=False):
    """Set dialog colours on a panel.

    Avoid wx.BG_STYLE_PAINT on panels that contain native controls (buttons);
    on wxGTK that style often leaves children invisible until the mouse hovers.
    """
    bg, default_fg = dialog_colours()
    if fg is None:
        fg = default_fg
    if custom_paint and hasattr(wx, 'BG_STYLE_PAINT'):
        panel.SetBackgroundStyle(wx.BG_STYLE_PAINT)
    elif hasattr(wx, 'BG_STYLE_COLOUR'):
        panel.SetBackgroundStyle(wx.BG_STYLE_COLOUR)
    panel.SetBackgroundColour(bg)
    panel.SetForegroundColour(fg)
    return fg


def style_label(ctrl, fg):
    ctrl.SetForegroundColour(fg)


def style_button(btn):
    """GTK needs explicit button colours or controls stay transparent until hover."""
    face = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
    text = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT)
    btn.SetBackgroundColour(face)
    btn.SetForegroundColour(text)
    if hasattr(btn, 'SetOwnBackgroundColour'):
        btn.SetOwnBackgroundColour(face)
    if hasattr(btn, 'SetOwnForegroundColour'):
        btn.SetOwnForegroundColour(text)


def style_checkbox(ctrl, fg):
    ctrl.SetForegroundColour(fg)
    if hasattr(ctrl, 'SetOwnForegroundColour'):
        ctrl.SetOwnForegroundColour(fg)


def _wx_window(window):
    """Return a wx window for repaint helpers."""
    if window is None:
        return None
    if hasattr(window, 'Layout') and hasattr(window, 'Refresh'):
        return window
    return None


def force_window_paint(window):
    """Queue a full repaint of window and descendants (Linux GTK)."""
    window = _wx_window(window)
    if window is None:
        return
    if hasattr(window, 'Layout'):
        window.Layout()
    for widget in walk_widgets(window):
        if hasattr(widget, 'Refresh'):
            widget.Refresh(False)
        if hasattr(widget, 'Update'):
            widget.Update()
    if hasattr(window, 'Refresh'):
        window.Refresh(False)
    if hasattr(window, 'Update'):
        window.Update()
    app = wx.GetApp()
    if app is not None:
        app.ProcessPendingEvents()


class GtkRepaintTimer(wx.EvtHandler):
    """Fire several repaints after show; fixes one-shot GTK expose bugs."""

    def __init__(self, window, interval_ms=50, count=6):
        wx.EvtHandler.__init__(self)
        self._window = window
        self._remaining = count
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer)
        self._timer.Start(interval_ms)

    def _on_timer(self, event):
        try:
            force_window_paint(self._window)
        finally:
            self._remaining -= 1
            if self._remaining <= 0:
                self._timer.Stop()


def schedule_repaint_burst(window):
    if sys.is_linux():
        GtkRepaintTimer(window)
    else:
        force_window_paint(window)
