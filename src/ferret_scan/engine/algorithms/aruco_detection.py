# This file is part of the Gryphon Scan Project

__author__ = 'Mikhail N Klimushkin aka Night Gryphon <ngryph@gmail.com>'
__copyright__ = 'Copyright (C) 2019 Night Gryphon'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'


import cv2

try:
    import cv2.aruco as aruco

    aruco_present = True
except ImportError:
    aruco_present = False


import numpy as np

from ferret_scan.engine.calibration.calibration_data import calibration_data
from ferret_scan.engine.calibration.pattern import pattern


def _aruco_modern_api():
    return aruco_present and hasattr(aruco, 'ArucoDetector')


def _marker_object_points(marker_length):
    half = marker_length / 2.0
    return np.array(
        [
            [-half, half, 0],
            [half, half, 0],
            [half, -half, 0],
            [-half, -half, 0],
        ],
        dtype=np.float32,
    )


class ArucoDetection:
    def __init__(self):
        if not aruco_present:
            return None

        if _aruco_modern_api():
            self._modern = True
            self.aruco_dict = aruco.getPredefinedDictionary(pattern.aruco_dict)
            self.aruco_parameters = aruco.DetectorParameters()
            refine = getattr(aruco, 'CORNER_REFINE_APRILTAG', None)
            if refine is not None:
                self.aruco_parameters.cornerRefinementMethod = refine
            self._detector = aruco.ArucoDetector(self.aruco_dict, self.aruco_parameters)
        else:
            self._modern = False
            self.aruco_dict = aruco.Dictionary_get(pattern.aruco_dict)
            self.aruco_parameters = aruco.DetectorParameters_create()
            self.aruco_parameters.cornerRefinementMethod = aruco.CORNER_REFINE_APRILTAG

    def aruco_detect(self, image):
        if not aruco_present:
            return (None, None)

        if image is None:
            return (None, None)

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        if self._modern:
            corners, ids, _rejected = self._detector.detectMarkers(gray)
        else:
            corners, ids, _rejected = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.aruco_parameters)

        return (corners, ids)

    def aruco_pose_from_corners(self, corners):
        if not aruco_present:
            return (None, None)

        cam = calibration_data.camera_matrix
        dist = calibration_data.distortion_vector
        marker_length = pattern.aruco_size

        if self._modern:
            obj_points = _marker_object_points(marker_length)
            rvecs = []
            tvecs = []
            for corner in corners:
                ok, rvec, tvec = cv2.solvePnP(
                    obj_points, corner.reshape(-1, 2), cam, dist, flags=cv2.SOLVEPNP_IPPE_SQUARE
                )
                if not ok:
                    continue
                rvecs.append(rvec)
                tvecs.append(tvec)
            if not rvecs:
                return (None, None)
            return (np.array(rvecs), np.array(tvecs))

        return aruco.estimatePoseSingleMarkers(corners, marker_length, cam, dist)

    def aruco_draw_markers(self, image, corners, ids):
        rvecs = None
        tvecs = None
        if aruco_present and image is not None and ids is not None and len(ids) > 0:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            image = aruco.drawDetectedMarkers(image, corners, ids)

            rvecs, tvecs = self.aruco_pose_from_corners(corners)
            if rvecs is not None and tvecs is not None:
                axis_len = pattern.aruco_size / 2
                for idx in range(len(ids)):
                    rvec = rvecs[idx]
                    tvec = tvecs[idx]
                    if self._modern:
                        cv2.drawFrameAxes(
                            image,
                            calibration_data.camera_matrix,
                            calibration_data.distortion_vector,
                            rvec,
                            tvec,
                            axis_len,
                        )
                    else:
                        image = aruco.drawAxis(
                            image,
                            calibration_data.camera_matrix,
                            calibration_data.distortion_vector,
                            rvec,
                            tvec,
                            axis_len,
                        )

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return (image, rvecs, tvecs)


aruco_detection = ArucoDetection()
