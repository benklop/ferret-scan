# -*- coding: utf-8 -*-
# This file is part of the Horus Project

from __future__ import absolute_import
__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

#from ferret.engine.driver.driver import Driver
from ferret.engine.driver.driver import driver
from ferret.engine.scan.ciclop_scan import CiclopScan
from ferret.engine.scan.current_video import CurrentVideo
from ferret.engine.calibration.pattern import pattern
from ferret.engine.calibration.calibration_data import calibration_data
from ferret.engine.calibration.camera_intrinsics import CameraIntrinsics
from ferret.engine.calibration.autocheck import Autocheck
from ferret.engine.calibration.laser_triangulation import LaserTriangulation
from ferret.engine.calibration.platform_extrinsics import PlatformExtrinsics
from ferret.engine.calibration.combo_calibration import ComboCalibration
#from ferret.engine.calibration.cloud_correction import CloudCorrection

from ferret.engine.algorithms.image_capture import ImageCapture
from ferret.engine.algorithms.image_detection import ImageDetection
from ferret.engine.algorithms.aruco_detection import aruco_detection
from ferret.engine.algorithms.laser_segmentation import LaserSegmentation
from ferret.engine.algorithms.point_cloud_generation import PointCloudGeneration
from ferret.engine.algorithms.point_cloud_roi import PointCloudROI


# Instances of engine modules

#driver = Driver()
ciclop_scan = CiclopScan()
current_video = CurrentVideo() # no params
#pattern = Pattern()
#calibration_data = CalibrationData()
camera_intrinsics = CameraIntrinsics() # no params
scanner_autocheck = Autocheck() # no params
laser_triangulation = LaserTriangulation()
platform_extrinsics = PlatformExtrinsics()
combo_calibration = ComboCalibration()
image_capture = ImageCapture()
image_detection = ImageDetection() # no params
laser_segmentation = LaserSegmentation()
point_cloud_generation = PointCloudGeneration() # no params
point_cloud_roi = PointCloudROI()
#cloud_correction = CloudCorrection()
