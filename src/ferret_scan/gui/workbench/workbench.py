from collections import OrderedDict

import wx
import wx.lib.scrolledpanel

from ferret_scan.gui.util import gtk_compat
from ferret_scan.gui.widgets import ExpandableCollection
from ferret_scan.runtime_engine import driver
from ferret_scan.util import system as sys


class Workbench(wx.Panel):
    def __init__(self, parent, name='Workbench'):
        wx.Panel.__init__(self, parent)
        self.name = name

        # Elements
        self.scroll_panel = wx.lib.scrolledpanel.ScrolledPanel(self, size=(-1, -1))
        self.scroll_panel.SetupScrolling(scroll_x=False, scrollIntoView=False)
        self.scroll_panel.SetAutoLayout(1)
        if hasattr(wx, 'BG_STYLE_PAINT'):
            self.scroll_panel.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.panels_collection = ExpandableCollection(self.scroll_panel)
        self.pages_collection = OrderedDict()

        # Layout
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.scroll_panel, 0, wx.ALL ^ wx.RIGHT | wx.EXPAND, 1)
        self.SetSizer(self.hbox)

        self.add_panels()  # Add panels to collection
        self.panels_collection.init_panels_layout()

        vsbox = wx.BoxSizer(wx.VERTICAL)
        vsbox.Add(self.panels_collection, 1, wx.ALL | wx.EXPAND, 0)
        self.scroll_panel.SetSizer(vsbox)
        vsbox.Fit(self.scroll_panel)
        panel_size = self.scroll_panel.GetSize()[0] + wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)
        self.scroll_panel.SetMinSize((panel_size, -1))
        self.scroll_panel.Disable()

        self.add_pages()
        self.Layout()

        # Events
        self.Bind(wx.EVT_SHOW, self.on_show)

    def add_panels(self):
        raise NotImplementedError

    def add_pages(self):
        raise NotImplementedError

    def setup_engine(self):
        raise NotImplementedError

    def on_open(self):
        raise NotImplementedError

    def on_close(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def add_panel(self, name, panel, on_selected_callback=None):
        return self.panels_collection.add_panel(name, panel, on_selected_callback)

    def add_page(self, name, page):
        self.pages_collection[name] = page
        self.hbox.Add(page, 1, wx.ALL | wx.EXPAND, 2)
        return page

    def enable_content(self):
        self.scroll_panel.Enable()
        self.panels_collection.enable_content()
        if sys.is_linux():
            wx.CallAfter(gtk_compat.schedule_repaint_burst, self.scroll_panel)

    def disable_content(self):
        self.panels_collection.disable_content()
        self.scroll_panel.Disable()

    def update_controls(self):
        self.panels_collection.update_from_profile()
        if driver.is_connected:
            self.setup_engine()

    def on_connect(self):
        if driver.is_connected:
            self.setup_engine()
            for _, p in self.pages_collection.items():
                p.Enable()
            self.on_open()

    def on_disconnect(self):
        for _, p in self.pages_collection.items():
            p.Disable()
        self.on_close()
        self.disable_content()
        self.reset()

    def on_show(self, event):
        if event.IsShown():
            if driver.is_connected:
                self.setup_engine()
                self.on_open()
        else:
            self.on_close()
