"""Chessboard pattern overlay drawing (OpenCV only; no wx)."""

import cv2
import numpy as np

from ferret_scan.core.app_state import get_app_context
from ferret_scan.engine.calibration.pattern import pattern


def augmented_draw_pattern(image, corners):
    if corners is not None:
        cv2.drawChessboardCorners(image, (pattern.columns, pattern.rows), corners, True)

        ctx = get_app_context()
        pose = ctx.image_detection.detect_pose_from_corners(corners)
        l = -pattern.square_width
        t = -pattern.square_width
        r = pattern.square_width * pattern.columns
        b = pattern.square_width * pattern.rows
        wl = pattern.border_l
        wr = pattern.border_r
        wt = pattern.border_t
        wb = pattern.border_b

        calibration_data = ctx.platform_extrinsics.calibration_data
        points = np.float32(
            (
                (l, t, 0),
                (r, t, 0),
                (r, b, 0),
                (l, b, 0),
                (l - wl, t - wt, 0),
                (r + wr, t - wt, 0),
                (r + wr, b + wb, 0),
                (l - wl, b + wb, 0),
                (l - wl, b - pattern.square_width + pattern.origin_distance, 0),
                (r + wr, b - pattern.square_width + pattern.origin_distance, 0),
                (l, b, 0),
                (l, b, -50),
            )
        )
        p, jac = cv2.projectPoints(
            points, pose[0], pose[1].T[0], calibration_data.camera_matrix, calibration_data.distortion_vector
        )
        p = np.int32(p).reshape(-1, 2)
        cv2.polylines(image, np.int32([p[0:4]]), True, (0, 255, 0), 2)
        cv2.polylines(image, np.int32([p[4:8]]), True, (255, 0, 0), 2)
        cv2.line(image, tuple(p[8]), tuple(p[9]), (255, 0, 0), 2)
        cv2.line(image, tuple(p[10]), tuple(p[11]), (255, 0, 0), 2)

        cv2.putText(
            image, str(pose[1].T[0]), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), lineType=cv2.LINE_AA
        )
    return image
