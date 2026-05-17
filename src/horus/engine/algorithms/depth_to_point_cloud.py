# -*- coding: utf-8 -*-
# Depth map → 3D points for structured-light (Ferret / RGB-D) scanning.

import numpy as np

from horus import Singleton
from horus.engine.calibration.calibration_data import CalibrationData


@Singleton
class DepthToPointCloud(object):

    def __init__(self):
        self.calibration_data = CalibrationData()
        self.stride = 2

    def compute_point_cloud(self, theta, depth_mm, color_bgr=None, depth_scale=1.0):
        """Return (3xN model-frame points, 3xN uint8 texture) or (None, None)."""
        if depth_mm is None:
            return None, None

        points_cam = self._unproject_depth(depth_mm, depth_scale)
        if points_cam is None or points_cam.shape[1] == 0:
            return None, None

        Xwo = self._camera_to_platform(points_cam)
        c, s = np.cos(-theta), np.sin(-theta)
        Rz = np.matrix([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        Xw = Rz * Xwo

        texture = self._sample_texture(color_bgr, depth_mm, points_cam)
        return np.array(Xw), texture

    def _unproject_depth(self, depth_mm, depth_scale):
        K = self.calibration_data.camera_matrix
        if K is None or len(K) < 3:
            return None

        fx = K[0][0]
        fy = K[1][1]
        cx = K[0][2]
        cy = K[1][2]

        h, w = depth_mm.shape[:2]
        step = max(1, int(self.stride))
        us = np.arange(0, w, step)
        vs = np.arange(0, h, step)
        uu, vv = np.meshgrid(us, vs)
        z = depth_mm[vv, uu].astype(np.float32) * float(depth_scale)
        mask = z > 0
        if not np.any(mask):
            return None

        u = uu[mask].astype(np.float32)
        v = vv[mask].astype(np.float32)
        z = z[mask]

        x = (u - cx) * z / fx
        y = (v - cy) * z / fy
        return np.vstack((x, y, z))

    def _camera_to_platform(self, Xc):
        R = np.matrix(self.calibration_data.platform_rotation)
        t = np.matrix(self.calibration_data.platform_translation).T
        return R.T * Xc - R.T * t

    def _sample_texture(self, color_bgr, depth_mm, points_cam):
        n = points_cam.shape[1]
        if color_bgr is None:
            return None

        K = self.calibration_data.camera_matrix
        fx, fy = K[0][0], K[1][1]
        cx, cy = K[0][2], K[1][2]
        x, y, z = points_cam[0, :], points_cam[1, :], points_cam[2, :]
        u = np.round((x * fx / z) + cx).astype(np.int32)
        v = np.round((y * fy / z) + cy).astype(np.int32)
        h, w = color_bgr.shape[:2]
        valid = (u >= 0) & (u < w) & (v >= 0) & (v < h)
        tex = np.zeros((3, n), np.uint8)
        tex[0, valid] = color_bgr[v[valid], u[valid], 2]
        tex[1, valid] = color_bgr[v[valid], u[valid], 1]
        tex[2, valid] = color_bgr[v[valid], u[valid], 0]
        return tex
