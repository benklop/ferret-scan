import platform
import threading

from ferret_scan.engine.algorithms.image_capture import ImageCapture
from ferret_scan.engine.algorithms.image_detection import ImageDetection
from ferret_scan.engine.algorithms.laser_segmentation import LaserSegmentation
from ferret_scan.engine.algorithms.point_cloud_generation import PointCloudGeneration

system = platform.system()

"""
    Calibrations:

        - Autocheck Algorithm
        - Camera Intrinsics Calibration
        - Laser Triangulation Calibration
        - Platform Extrinsics Calibration
"""


class CalibrationCancel(Exception):
    def __init__(self):
        Exception.__init__(self, 'CalibrationCancel')


class Calibration:
    """Generic class for threading calibration"""

    def __init__(
        self,
        driver=None,
        pattern=None,
        calibration_data=None,
        image_capture=None,
        image_detection=None,
        laser_segmentation=None,
        point_cloud_generation=None,
    ):
        from ferret_scan.engine.calibration.calibration_data import calibration_data as _calibration_data
        from ferret_scan.engine.calibration.pattern import pattern as _pattern
        from ferret_scan.engine.driver.driver import driver as _driver

        self.driver = driver if driver is not None else _driver
        self.pattern = pattern if pattern is not None else _pattern
        self.calibration_data = calibration_data if calibration_data is not None else _calibration_data
        self.image_capture = (
            image_capture
            if image_capture is not None
            else ImageCapture(driver=self.driver, calibration_data=self.calibration_data)
        )
        self.image_detection = image_detection if image_detection is not None else ImageDetection()
        self.laser_segmentation = laser_segmentation if laser_segmentation is not None else LaserSegmentation()
        self.point_cloud_generation = (
            point_cloud_generation if point_cloud_generation is not None else PointCloudGeneration()
        )

        # TODO: Callbacks to Observer pattern
        self._before_callback = None
        self._progress_callback = None
        self._after_callback = None
        self._is_calibrating = False

    def set_callbacks(self, before, progress, after):
        self._before_callback = before
        self._progress_callback = progress
        self._after_callback = after

    def start(self):
        if not self._is_calibrating:
            if self._before_callback is not None:
                self._before_callback()

            if self._progress_callback is not None:
                self._progress_callback(0)

            self._is_calibrating = True
            threading.Thread(target=self._start).start()

    def _start(self):
        pass

    def cancel(self):
        self._is_calibrating = False
