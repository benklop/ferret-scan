"""Color channel order for Ferret RGB-D decode."""

from __future__ import annotations

from unittest.mock import MagicMock

import cv2
import numpy as np


def _frame(fmt, payload: np.ndarray, w: int, h: int):
    frame = MagicMock()
    frame.get_format.return_value = fmt
    frame.get_width.return_value = w
    frame.get_height.return_value = h
    frame.get_data.return_value = payload.tobytes()
    return frame


def test_mjpg_decode_is_rgb():
    from pyorbbecsdk import OBFormat

    from ferret_scan.services.ferret_rgbd import _decode_color_frame

    bgr = np.zeros((4, 4, 3), dtype=np.uint8)
    bgr[:, :] = (0, 0, 255)  # red in BGR
    jpg = cv2.imencode('.jpg', bgr)[1]
    rgb = _decode_color_frame(_frame(OBFormat.MJPG, jpg, 4, 4))
    assert rgb.shape == (4, 4, 3)
    r, g, b = rgb[0, 0]
    assert r > 200 and g < 50 and b < 50


def test_bgr_uncompressed_to_rgb():
    from pyorbbecsdk import OBFormat

    from ferret_scan.services.ferret_rgbd import _decode_color_frame

    bgr = np.zeros((2, 2, 3), dtype=np.uint8)
    bgr[:, :] = (0, 0, 255)
    rgb = _decode_color_frame(_frame(OBFormat.BGR, bgr, 2, 2))
    assert tuple(rgb[0, 0]) == (255, 0, 0)


def test_rgb_uncompressed_unchanged():
    from pyorbbecsdk import OBFormat

    from ferret_scan.services.ferret_rgbd import _decode_color_frame

    raw = np.zeros((2, 2, 3), dtype=np.uint8)
    raw[:, :] = (255, 0, 0)
    rgb = _decode_color_frame(_frame(OBFormat.RGB, raw, 2, 2))
    assert tuple(rgb[0, 0]) == (255, 0, 0)
