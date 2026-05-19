"""Ferret calibration board workbench page (instructions + wizard launcher)."""

import wx


class FerretBoardPages(wx.Panel):
    def __init__(self, parent, open_wizard_callback):
        wx.Panel.__init__(self, parent)
        self.open_wizard_callback = open_wizard_callback

        text = wx.StaticText(
            self,
            label=_(
                'Optional high-precision calibration board. Enter the board serial number and '
                'follow guided poses. Factory parameter lookup from the SN is not implemented yet; '
                'see doc/FERRET_BOARD_CALIBRATION.md.'
            ),
        )
        text.Wrap(480)
        btn = wx.Button(self, label=_('Open calibration wizard…'))
        btn.Bind(wx.EVT_BUTTON, lambda e: self.open_wizard_callback())

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(text, 0, wx.ALL | wx.EXPAND, 12)
        vbox.Add(btn, 0, wx.ALL, 12)
        self.SetSizer(vbox)

    def play(self):
        pass

    def stop(self):
        pass

    def reset(self):
        pass
