"""Application context: engine facades and driver."""

from __future__ import annotations

from dataclasses import dataclass

from ferret_scan.engine.algorithms.image_capture import ImageCapture
from ferret_scan.engine.algorithms.image_detection import ImageDetection
from ferret_scan.engine.algorithms.laser_segmentation import LaserSegmentation
from ferret_scan.engine.algorithms.point_cloud_generation import PointCloudGeneration
from ferret_scan.engine.algorithms.point_cloud_roi import PointCloudROI
from ferret_scan.engine.calibration.autocheck import Autocheck
from ferret_scan.engine.calibration.calibration_data import CalibrationData, calibration_data
from ferret_scan.engine.calibration.camera_intrinsics import CameraIntrinsics
from ferret_scan.engine.calibration.cloud_correction import CloudCorrection
from ferret_scan.engine.calibration.combo_calibration import ComboCalibration
from ferret_scan.engine.calibration.laser_triangulation import LaserTriangulation
from ferret_scan.engine.calibration.pattern import Pattern, pattern
from ferret_scan.engine.calibration.platform_extrinsics import PlatformExtrinsics
from ferret_scan.engine.driver.driver import Driver, driver
from ferret_scan.engine.scan.ciclop_scan import CiclopScan
from ferret_scan.engine.scan.current_video import CurrentVideo
from ferret_scan.util import profile


@dataclass
class AppContext:
    driver: Driver
    calibration_data: CalibrationData
    pattern: Pattern
    ciclop_scan: CiclopScan
    current_video: CurrentVideo
    camera_intrinsics: CameraIntrinsics
    scanner_autocheck: Autocheck
    laser_triangulation: LaserTriangulation
    platform_extrinsics: PlatformExtrinsics
    combo_calibration: ComboCalibration
    image_capture: ImageCapture
    image_detection: ImageDetection
    laser_segmentation: LaserSegmentation
    point_cloud_generation: PointCloudGeneration
    point_cloud_roi: PointCloudROI
    cloud_correction: CloudCorrection

    @classmethod
    def create(cls) -> AppContext:
        drv = driver
        cal = calibration_data
        pat = pattern
        image_capture = ImageCapture(driver=drv, calibration_data=cal)
        return cls(
            driver=drv,
            calibration_data=cal,
            pattern=pat,
            image_capture=image_capture,
            image_detection=ImageDetection(),
            laser_segmentation=LaserSegmentation(),
            point_cloud_generation=PointCloudGeneration(),
            current_video=CurrentVideo(),
            ciclop_scan=CiclopScan(driver=drv),
            camera_intrinsics=CameraIntrinsics(),
            scanner_autocheck=Autocheck(),
            laser_triangulation=LaserTriangulation(calibration_data=cal),
            platform_extrinsics=PlatformExtrinsics(),
            combo_calibration=ComboCalibration(),
            point_cloud_roi=PointCloudROI(),
            cloud_correction=CloudCorrection(),
        )

    @property
    def settings(self):
        return profile.settings
