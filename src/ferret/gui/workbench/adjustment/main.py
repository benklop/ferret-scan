# This file is part of the Horus Project


__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

from ferret.gui.engine import calibration_data, driver, pattern
from ferret.gui.util.video_view import VideoView
from ferret.gui.workbench.adjustment.current_video import CurrentVideo
from ferret.gui.workbench.adjustment.panels import (
    CalibrationCapturePanel,
    CalibrationSegmentationPanel,
    ScanCapturePanel,
    ScanSegmentationPanel,
)
from ferret.gui.workbench.workbench import Workbench
from ferret.util import profile


class AdjustmentWorkbench(Workbench):
    def __init__(self, parent):
        Workbench.__init__(self, parent, name=_('Adjustment workbench'))

        self.current_video = CurrentVideo()

    def add_panels(self):
        self.add_panel('scan_capture', ScanCapturePanel)
        self.add_panel('scan_segmentation', ScanSegmentationPanel)
        self.add_panel('calibration_capture', CalibrationCapturePanel)
        self.add_panel('calibration_segmentation', CalibrationSegmentationPanel)

    def add_pages(self):
        self.add_page('video_view', VideoView(self, self._video_frame, wxtimer=False))
        self.panels_collection.expandable_panels[profile.settings['current_panel_adjustment']].on_title_clicked(None)

    def _video_frame(self):
        return self.current_video.get_frame()

    def on_open(self):
        current_video_mode = profile.settings['current_video_mode_adjustment']
        self.pages_collection['video_view'].play(
            flush=not (current_video_mode == 'Laser' or current_video_mode == 'Gray')
        )

    def on_close(self):
        try:
            self.pages_collection['video_view'].stop()
        except:
            pass

    def reset(self):
        self.pages_collection['video_view'].reset()

    def setup_engine(self):
        driver.camera.read_profile()
        self.current_video.mode = profile.settings['current_video_mode_adjustment']
        pattern.read_profile()
        calibration_data.read_profile_camera()
        calibration_data.read_profile_calibration()
        self.panels_collection.expandable_panels[profile.settings['current_panel_adjustment']].on_title_clicked(None)
