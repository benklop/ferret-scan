import logging

import wx

from ferret_scan.engine.driver.board import BoardNotConnected, OldFirmware, WrongFirmware
from ferret_scan.engine.driver.camera import CameraNotConnected, InvalidVideo, WrongCamera, WrongDriver
from ferret_scan.engine.driver.camera_ferret import FerretNotAvailable
from ferret_scan.hardware.types import DeviceCapabilities
from ferret_scan.runtime_engine import driver
from ferret_scan.util import profile, resources, system

logger = logging.getLogger(__name__)


class MainToolbar(wx.Panel):
    def __init__(self, parent, on_connect_callback=None, on_disconnect_callback=None):
        wx.Panel.__init__(self, parent)

        # ====== common ======
        # Element
        self.toolbar_connect = wx.ToolBar(self)
        self.toolbar_connect.SetDoubleBuffered(True)

        self.toolbar_scan = wx.ToolBar(self)
        self.toolbar_scan.SetDoubleBuffered(True)

        self.toolbar_control = wx.ToolBar(self)
        self.toolbar_control.SetDoubleBuffered(True)

        self.combo = wx.ComboBox(self, -1, size=(250, -1), style=wx.CB_READONLY)

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.toolbar_connect, 0, wx.ALL | wx.EXPAND, 3)
        hbox.Add(self.toolbar_control, 0, wx.ALL | wx.EXPAND, 3)
        self.toolbar_control.Hide()
        hbox.Add(self.toolbar_scan, 0, wx.ALL | wx.EXPAND, 3)
        hbox.Add((0, 0), 1, wx.ALL | wx.EXPAND, 1)
        hbox.Add(self.combo, 0, wx.ALL, 10)
        self.SetSizer(hbox)
        self.Layout()

        # ======== Connect toolbar ========
        self.on_connect_callback = on_connect_callback
        self.on_disconnect_callback = on_disconnect_callback

        # Elements
        self.connect_tool = self.toolbar_connect.AddLabelTool(
            wx.NewId(), _('Connect'), wx.Bitmap(resources.get_path_for_image('connect.png')), shortHelp=_('Connect')
        )

        self.disconnect_tool = self.toolbar_connect.AddLabelTool(
            wx.NewId(),
            _('Disconnect'),
            wx.Bitmap(resources.get_path_for_image('disconnect.png')),
            shortHelp=_('Disconnect'),
        )

        self.toolbar_connect.Realize()

        self._enable_tool(self.connect_tool, True)
        self._enable_tool(self.disconnect_tool, False)

        # Events
        self.Bind(wx.EVT_TOOL, self.on_connect_tool_clicked, self.connect_tool)
        self.Bind(wx.EVT_TOOL, self.on_disconnect_tool_clicked, self.disconnect_tool)

        # ========= Control toolbar ========
        # Elements
        self.r_left_tool = self.toolbar_control.AddLabelTool(
            wx.NewId(),
            _('Rotate left'),
            wx.Bitmap(resources.get_path_for_image('baseline_rotate_left_black_24dp.png')),
            shortHelp=_('Rotate left'),
        )

        self.r_right_tool = self.toolbar_control.AddLabelTool(
            wx.NewId(),
            _('Rotate right'),
            wx.Bitmap(resources.get_path_for_image('baseline_rotate_right_black_24dp.png')),
            shortHelp=_('Rotate right'),
        )

        Laser_On_Bitmap = wx.Bitmap(resources.get_path_for_image('baseline_brightness_7_black_24dp.png'))
        wx.Bitmap(resources.get_path_for_image('baseline_brightness_5_black_24dp.png'))

        self.l1_tool = self.toolbar_control.AddTool(wx.NewId(), '', Laser_On_Bitmap, kind=wx.ITEM_CHECK)
        self.l2_tool = self.toolbar_control.AddTool(wx.NewId(), '', Laser_On_Bitmap, kind=wx.ITEM_CHECK)

        self.toolbar_control.Realize()

        self._enable_control_tools(False)

        # Events
        self.Bind(wx.EVT_TOOL, self.on_r_left_tool_clicked, self.r_left_tool)
        self.Bind(wx.EVT_TOOL, self.on_r_right_tool_clicked, self.r_right_tool)
        self.Bind(wx.EVT_TOOL, lambda v: self.on_laser_tool_clicked(0, v.IsChecked()), self.l1_tool)
        self.Bind(wx.EVT_TOOL, lambda v: self.on_laser_tool_clicked(1, v.IsChecked()), self.l2_tool)

        self._caps_rotate = False
        self._caps_lasers = False

    def on_connect_tool_clicked(self, event):
        try:
            video_list = driver.camera.get_video_list()
            current_video_id = profile.settings['camera_id']
            if len(video_list) > 0:
                if current_video_id not in video_list:
                    profile.settings['camera_id'] = str(video_list[0])
                    driver.camera.set_camera_id_from_settings(profile.settings['camera_id'])

            driver.set_callbacks(
                lambda: wx.CallAfter(self.before_connect), lambda r: wx.CallAfter(self.after_connect, r)
            )
            driver.connect()
        except Exception as exc:
            logger.exception('Connect failed before driver thread started')
            self._show_message(_('Connection failed'), wx.ICON_ERROR, str(exc))

    def on_disconnect_tool_clicked(self, event):
        self.wait_cursor = wx.BusyCursor()
        driver.disconnect()
        self.update_status(driver.is_connected)
        del self.wait_cursor

    def before_connect(self):
        self._enable_tool(self.connect_tool, False)
        self.GetParent().enable_gui(False)
        driver.board.set_unplug_callback(None)
        driver.camera.set_unplug_callback(None)
        self.wait_cursor = wx.BusyCursor()

    def after_connect(self, response):
        ret, result = response
        if not ret:
            if isinstance(result, WrongFirmware):
                self._show_message(
                    _(result),
                    wx.ICON_INFORMATION,
                    _(
                        'The board has the wrong firmware or an invalid baud rate.\n'
                        'Please select your board and press "Upload firmware"'
                    ),
                )
                self.update_status(False)
                self.GetParent().launch_preferences()
            elif isinstance(result, BoardNotConnected):
                self._show_message(
                    _(result),
                    wx.ICON_INFORMATION,
                    _('The board is not connected.\nPlease connect your board and select a valid Serial name'),
                )
                self.update_status(False)
                self.GetParent().launch_preferences(basic=True)
            elif isinstance(result, OldFirmware):
                self._show_message(
                    _(result),
                    wx.ICON_INFORMATION,
                    _('The board has and old firmware.\nPlease select your board and press "Upload firmware"'),
                )
                self.update_status(False)
                self.GetParent().launch_preferences()
            elif isinstance(result, WrongCamera):
                self._show_message(
                    _(result),
                    wx.ICON_INFORMATION,
                    _('You probably have selected the wrong camera.\nPlease select another Camera ID'),
                )
                self.update_status(False)
                wrong_camera_id = profile.settings['camera_id']
                self.GetParent().launch_preferences(basic=True)
                # Do not save camera id if it is wrong
                if profile.settings['camera_id'] == wrong_camera_id:
                    profile.settings['camera_id'] = ''
            elif isinstance(result, CameraNotConnected):
                self._show_message(_(result), wx.ICON_ERROR, _('Please plug your camera in and try to connect again'))
            elif isinstance(result, InvalidVideo):
                self._show_message(
                    _(result), wx.ICON_ERROR, _('Unplug and plug your camera USB cable and try to connect again')
                )
            elif isinstance(result, WrongDriver):
                if system.is_windows():
                    self._show_message(
                        _(result),
                        wx.ICON_ERROR,
                        _(
                            'Please, download and install the camera driver: \n'
                            'http://support.logitech.com/en_us/product/hd-webcam-c270'
                        ),
                    )
            elif isinstance(result, FerretNotAvailable):
                self._show_message(
                    _('Ferret not available'),
                    wx.ICON_ERROR,
                    _(
                        'Could not open the CR-Scan Ferret:\n\n{detail}\n\n'
                        'Plug in the scanner via USB, then run ./scripts/dev-setup '
                        '(builds libferret and pyorbbecsdk).'
                    ).format(detail=result),
                )
            else:
                logger.error('Unhandled connect failure: %s', result)
                self._show_message(_('Connection failed'), wx.ICON_ERROR, str(result))

        self.update_status(driver.is_connected)
        self.GetParent().enable_gui(True)
        del self.wait_cursor

    def update_status(self, status):
        self._enable_tool(self.connect_tool, not status)
        self._enable_tool(self.disconnect_tool, status)
        self._enable_control_tools(status)
        if status:
            if self.on_connect_callback is not None:
                self.on_connect_callback()
            callback = self.GetParent().on_board_unplugged
            driver.board.set_unplug_callback(lambda: wx.CallAfter(callback))
            callback = self.GetParent().on_camera_unplugged
            driver.camera.set_unplug_callback(lambda: wx.CallAfter(callback))
        else:
            if self.on_disconnect_callback is not None:
                self.on_disconnect_callback()
            driver.board.set_unplug_callback(None)
            driver.camera.set_unplug_callback(None)

    def _show_message(self, title, style, desc):
        dlg = wx.MessageDialog(self, desc, title, wx.OK | style)
        dlg.ShowModal()
        dlg.Destroy()

    def _enable_tool(self, item, enable):
        item.ToolBar.EnableTool(item.GetId(), enable)

    def scanning_mode(self, enable):
        if enable:
            self.toolbar_scan.Show()
        else:
            self.toolbar_scan.Hide()

    # ============= Control methods ===============
    def apply_capabilities(self, caps: DeviceCapabilities) -> None:
        self._caps_rotate = caps.toolbar_rotate
        self._caps_lasers = caps.toolbar_lasers
        show_control = caps.toolbar_rotate or caps.toolbar_lasers
        if show_control:
            self.toolbar_control.Show()
        else:
            self.toolbar_control.Hide()
        tb = self.toolbar_control
        tb.EnableTool(self.r_left_tool.GetId(), caps.toolbar_rotate)
        tb.EnableTool(self.r_right_tool.GetId(), caps.toolbar_rotate)
        tb.EnableTool(self.l1_tool.GetId(), caps.toolbar_lasers)
        tb.EnableTool(self.l2_tool.GetId(), caps.toolbar_lasers)
        self.Layout()

    def _enable_control_tools(self, enable):
        if not self.toolbar_control.IsShown():
            return
        if self._caps_rotate:
            self._enable_tool(self.r_left_tool, enable)
            self._enable_tool(self.r_right_tool, enable)
        if self._caps_lasers:
            self._enable_tool(self.l1_tool, enable)
            self._enable_tool(self.l2_tool, enable)

    def on_r_left_tool_clicked(self, item):
        step = profile.settings['motor_step_control']
        self._enable_control_tools(False)
        driver.board.motor_move(step, nonblocking=False, callback=lambda v: self._enable_control_tools(True))

    #        self._enable_control_tools(True)

    def on_r_right_tool_clicked(self, item):
        step = profile.settings['motor_step_control']
        self._enable_control_tools(False)
        driver.board.motor_move(-step, nonblocking=False, callback=lambda v: self._enable_control_tools(True))

    #        self._enable_control_tools(True)

    def on_laser_tool_clicked(self, laser_id, state):
        if state:
            driver.board.laser_on(laser_id)
        else:
            driver.board.laser_off(laser_id)
