# This file is part of the Gryphon Scan Project


__author__ = 'Mikhail N Klimushin aka Night Gryphon <ngryph@gmail.com>'
__copyright__ = 'Copyright (C) 2018 Night Gryphon'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'


import cv2
import numpy as np

from ferret_scan.engine.calibration.pattern import pattern
from ferret_scan.util import profile
from ferret_scan.util.gryphon_util import line_cross_sphere, plane_cross, pos2nd


def _platform_extrinsics():
    from ferret_scan import runtime_engine

    return runtime_engine.platform_extrinsics


def _image_detection():
    from ferret_scan import runtime_engine

    return runtime_engine.image_detection


# ==========================================================
# Prepare platform shapes cache

platform_points = None
platform_border = None


def init_platform_augmented_draw():
    global platform_points
    global platform_border

    r = profile.settings['platform_markers_diameter'] / 2  # 138
    h = profile.settings['platform_markers_z']
    rr = r * np.sin(np.deg2rad(45))
    platform_points = np.float32(
        [
            (0, 0, 0),
            (r, 0, h),
            (-r, 0, h),
            (0, r, h),
            (0, -r, h),
            (rr, rr, h),
            (rr, -rr, h),
            (-rr, rr, h),
            (-rr, -rr, h),
        ]
    )

    h = profile.settings['platform_border_z']
    polys = profile.get_machine_size_polygons()
    platform_border = []
    for p in polys[0]:
        platform_border.append((p[0], p[1], h))
    platform_border = np.float32(platform_border)


# ==========================================================
# Draw platform


def augmented_draw_platform(image):
    global platform_points
    global platform_border

    if platform_points is None:
        init_platform_augmented_draw()

    pe = _platform_extrinsics()
    if pe.calibration_data.platform_rotation is not None and pe.calibration_data.platform_translation is not None:
        calibration_data = pe.calibration_data
        # platform border
        p, jac = cv2.projectPoints(
            platform_border,
            calibration_data.platform_rotation,
            calibration_data.platform_translation,
            calibration_data.camera_matrix,
            calibration_data.distortion_vector,
        )
        p = np.int32([p])
        cv2.polylines(image, p, True, (0, 255, 0), 2)

        # marker positions
        p, jac = cv2.projectPoints(
            platform_points,
            calibration_data.platform_rotation,
            calibration_data.platform_translation,
            calibration_data.camera_matrix,
            calibration_data.distortion_vector,
        )
        p = np.int32(p).reshape(-1, 2)
        for pp in p:
            cv2.circle(image, tuple(pp), 5, (0, 0, 255), -1)


# ==========================================================
# Create mask - exclude platform


def augmented_platform_mask(image):
    global platform_points
    global platform_border

    mask = np.ones(image.shape[0:2], dtype='uint8')
    if platform_points is None:
        init_platform_augmented_draw()

    pe = _platform_extrinsics()
    if pe.calibration_data.platform_rotation is not None and pe.calibration_data.platform_translation is not None:
        calibration_data = pe.calibration_data
        # platform border
        p, jac = cv2.projectPoints(
            platform_border,
            calibration_data.platform_rotation,
            calibration_data.platform_translation,
            calibration_data.camera_matrix,
            calibration_data.distortion_vector,
        )
        p = np.int32([p])
        cv2.fillPoly(mask, p, 0)
    return mask


# ==========================================================
# Draw pattern


def augmented_draw_pattern(image, corners):
    from ferret_scan.engine.visualization.pattern_overlay import augmented_draw_pattern as _draw

    return _draw(image, corners)


# ==========================================================
# Create mask - belong to pattern area


def augmented_pattern_mask(image, corners):
    mask = np.zeros(image.shape[0:2], dtype='uint8')
    if corners is not None:
        pose = _image_detection().detect_pose_from_corners(corners)
        left = -pattern.square_width
        t = -pattern.square_width
        r = pattern.square_width * pattern.columns
        b = pattern.square_width * pattern.rows
        wl = pattern.border_l
        wr = pattern.border_r
        wt = pattern.border_t
        wb = pattern.border_b

        calibration_data = _platform_extrinsics().calibration_data
        points = np.float32(
            (
                (left - wl, t - wt, 0),
                (r + wr, t - wt, 0),
                (r + wr, b + wb, 0),
                (left - wl, b + wb, 0),
            )
        )
        p, jac = cv2.projectPoints(
            points, pose[0], pose[1].T[0], calibration_data.camera_matrix, calibration_data.distortion_vector
        )
        p = np.int32(p).reshape(-1, 2)

        cv2.fillConvexPoly(mask, np.int32([p]), 255)
    return mask


# ==========================================================
# Draw laser lines on platform


def augmented_draw_lasers_on_platform(image):
    if image is None:
        return
    calibration = _platform_extrinsics().calibration_data
    if calibration.platform_rotation is not None and calibration.platform_translation is not None:
        p_norm, p_dist = pos2nd(calibration.platform_rotation, calibration.platform_translation)
        for laser in calibration.laser_planes:
            if not laser.is_empty():
                line_vec, line_p = plane_cross(p_norm, p_dist, laser.normal, laser.distance)
                p1, p2 = line_cross_sphere(
                    line_vec, line_p, calibration.platform_translation, profile.settings['machine_diameter'] / 2
                )

                points = np.float32([p1, p2])
                p, jac = cv2.projectPoints(
                    points, np.identity(3), np.zeros(3), calibration.camera_matrix, calibration.distortion_vector
                )
                p = np.int32(p).reshape(-1, 2)
                cv2.line(image, tuple(p[0]), tuple(p[1]), (255, 0, 0), 2)


# ==========================================================
# Draw laser lines on pattern


def augmented_draw_lasers_on_pattern(image, pose):
    if image is None or pose is None:
        return

    calibration = _platform_extrinsics().calibration_data
    if calibration.laser_planes is None:
        return

    p = pattern
    #    pl = -p.square_width - p.border_l
    pt = -p.square_width - p.border_t
    #    pr = p.square_width * p.columns + p.border_r
    pb = p.square_width * p.rows + p.border_b

    r_inv = np.linalg.inv(pose[0])

    for laser in calibration.laser_planes:
        if laser.normal is None or laser.distance is None:
            continue

        l_n = r_inv.dot(laser.normal)
        pp = laser.distance * laser.normal[:] - pose[1].T[0]
        l_d = pp.dot(laser.normal.T)

        if l_n[0] != 0:
            xt = (l_d - pt * l_n[1]) / l_n[0]
            xb = (l_d - pb * l_n[1]) / l_n[0]
            points = np.float32([(xt, pt, 0), (xb, pb, 0)])
            p, jac = cv2.projectPoints(
                points, pose[0], pose[1].T[0], calibration.camera_matrix, calibration.distortion_vector
            )
            p = np.int32(p).reshape(-1, 2)
            cv2.line(image, tuple(p[0]), tuple(p[1]), (255, 0, 0), 2)


def draw_2d_points(image, points, color):
    if image is not None and points is not None:
        (u, v) = points
        u = np.around(u).astype(int)
        image[v, u] = color
        try:
            image[v, u - 1] = color
            image[v, u + 1] = color
        except IndexError:
            pass

    return image
