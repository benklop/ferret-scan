import time

import wx
import wx.adv

from ferret_scan.util.resources import get_path_for_image


class SplashScreen(wx.adv.SplashScreen):
    def __init__(self, callback):
        self.callback = callback
        self._callback_done = False

        bitmap = wx.Image(get_path_for_image('splash.png'), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        super().__init__(bitmap, wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_NO_TIMEOUT, 0, None)
        # TODO: fix in wx.SplashScreen class
        time.sleep(0.03)
        wx.CallAfter(self.do_callback)

    def do_callback(self):
        if self._callback_done:
            return
        self._callback_done = True
        self.callback()
