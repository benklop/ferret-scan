import threading

from ferret_scan.engine.algorithms.depth_to_point_cloud import DepthToPointCloud
from ferret_scan.engine.algorithms.image_capture import ImageCapture
from ferret_scan.engine.algorithms.image_detection import ImageDetection
from ferret_scan.engine.algorithms.laser_segmentation import LaserSegmentation
from ferret_scan.engine.algorithms.point_cloud_generation import PointCloudGeneration
from ferret_scan.engine.algorithms.point_cloud_roi import PointCloudROI
from ferret_scan.engine.driver.driver import Driver


class ScanError(Exception):
    def __init__(self):
        Exception.__init__(self, 'Scan Error')


class Scan:
    """Generic class for threading scanning"""

    def __init__(self):
        self.driver = Driver()
        self.image_capture = ImageCapture()
        self.image_detection = ImageDetection()
        self.laser_segmentation = LaserSegmentation()
        self.point_cloud_generation = PointCloudGeneration()
        self.depth_to_point_cloud = DepthToPointCloud()
        self.point_cloud_roi = PointCloudROI()
        self.is_scanning = False

        # TODO: Callbacks to Observer pattern
        self._before_callback = None
        self._progress_callback = None
        self._after_callback = None
        self._progress = 0
        self._range = 0
        self._inactive = False

    def set_callbacks(self, before, progress, after):
        self._before_callback = before
        self._progress_callback = progress
        self._after_callback = after

    def start(self):
        if not self.is_scanning:
            if self._before_callback is not None:
                self._before_callback()

            if self._progress_callback is not None:
                self._progress_callback(0)

            self._initialize()

            self.is_scanning = True
            self._inactive = False

            threading.Thread(target=self._capture).start()
            threading.Thread(target=self._process).start()

    def stop(self):
        self._inactive = False
        self.is_scanning = False

    def pause(self):
        self._inactive = True

    def resume(self):
        self._inactive = False

    def _initialize(self):
        pass

    def _capture(self):
        pass

    def _process(self):
        pass
