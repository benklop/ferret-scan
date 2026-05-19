"""In-process Ferret RGB-D capture via libferret (pyorbbecsdk)."""

from __future__ import annotations

import logging
import os
import sys

import numpy as np

from ferret_scan.util import runtime

logger = logging.getLogger(__name__)


class FerretRgbdError(RuntimeError):
    pass


def _get_device_class():
    scripts_lib = os.path.join(runtime.repo_root(), 'scripts', 'lib')
    if scripts_lib not in sys.path:
        sys.path.insert(0, scripts_lib)
    from libferret_import import get_ferret_device_class

    return get_ferret_device_class()


def _decode_color_frame(color_frame):
    """Return HxWx3 uint8 RGB (ferret-scan convention for wx and calibration)."""
    import cv2

    color_fmt = color_frame.get_format()
    cw = color_frame.get_width()
    ch = color_frame.get_height()
    color_data = np.frombuffer(color_frame.get_data(), dtype=np.uint8)

    try:
        from pyorbbecsdk import OBFormat
    except ImportError:
        OBFormat = None

    if OBFormat is not None and color_fmt == OBFormat.MJPG:
        bgr = cv2.imdecode(color_data, cv2.IMREAD_COLOR)
        if bgr is None:
            raise FerretRgbdError('failed to decode MJPG color frame')
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    if OBFormat is not None and color_fmt == OBFormat.BGR:
        bgr = color_data.reshape(ch, cw, 3)
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    if OBFormat is not None and color_fmt == OBFormat.RGB:
        return color_data.reshape(ch, cw, 3).copy()

    if color_data.size >= 2 and color_data[0] == 0xFF and color_data[1] == 0xD8:
        bgr = cv2.imdecode(color_data, cv2.IMREAD_COLOR)
        if bgr is not None:
            return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    # Uncompressed 3-channel (Orbbec default for non-MJPG scan profiles).
    return color_data.reshape(ch, cw, 3).copy()


def _read_device_temperature_c(device) -> float | None:
    """Best-effort device temperature in Celsius from Orbbec properties."""
    try:
        ob = __import__('pyorbbecsdk', fromlist=['OBPropertyID', 'OBPermissionType'])
        prop = ob.OBPropertyID
        perm = ob.OBPermissionType
        for prop_id in (
            getattr(prop, 'OB_PROP_DEVICE_TEMPERATURE_FLOAT', None),
            getattr(prop, 'OB_PROP_TEMPERATURE_FLOAT', None),
            getattr(prop, 'OB_PROP_CHIP_TEMPERATURE_FLOAT', None),
        ):
            if prop_id is None:
                continue
            if device.is_property_supported(prop_id, perm.PERMISSION_READ):
                return float(device.get_float_property(prop_id))
    except Exception:
        logger.debug('Device temperature property unavailable', exc_info=True)
    return None


class FerretRgbdService:
    """Keeps an open FerretDevice pipeline for repeated captures."""

    def __init__(self, libferret_root: str | None = None):
        self._libferret_root = libferret_root or runtime.resolve_libferret_root()
        self._device = None
        self._last_temperature_c: float | None = None

    def connect(self) -> None:
        if self._device is not None:
            return
        if self._libferret_root:
            os.environ['FERRET_LIBFERRET_ROOT'] = self._libferret_root
        from ferret_scan.util import profile

        laser_on = bool(profile.settings.get('ferret_laser_on_connect', True))
        laser_settle = float(profile.settings.get('ferret_laser_settle_s', 2.0))
        low_bw = bool(profile.settings.get('ferret_low_bandwidth', False))
        FerretDevice = _get_device_class()
        dev = FerretDevice.open(laser=laser_on, laser_settle_s=laser_settle if laser_on else 0.0)
        config = dev.make_scan_config(color=True, depth=True, imu=False, low_bandwidth=low_bw)
        dev.pipeline.start(config)
        dev.pipeline.enable_frame_sync()
        self._device = dev
        self._last_temperature_c = _read_device_temperature_c(dev.device)
        logger.info('Ferret RGB-D service connected (in-process)')

    def disconnect(self) -> None:
        if self._device is None:
            return
        try:
            self._device.pipeline.stop()
        except Exception:
            logger.debug('Pipeline stop failed', exc_info=True)
        self._device = None

    def capture_rgbd(self):
        if self._device is None:
            raise FerretRgbdError('not connected')
        frames = None
        for _ in range(40):
            fs = self._device.pipeline.wait_for_frames(200)
            if fs is None:
                continue
            depth = fs.get_depth_frame()
            color = fs.get_color_frame()
            if depth and color:
                frames = (depth, color)
                break
        if frames is None:
            raise FerretRgbdError('no synced depth+color frameset')

        depth_frame, color_frame = frames
        scale = depth_frame.get_depth_scale()
        w = depth_frame.get_width()
        h = depth_frame.get_height()
        depth = np.frombuffer(depth_frame.get_data(), dtype=np.uint16).reshape(h, w)
        color = _decode_color_frame(color_frame)
        if self._device is not None:
            self._last_temperature_c = _read_device_temperature_c(self._device.device)
        meta = {
            'depth_scale': float(scale),
            'depth_width': int(w),
            'depth_height': int(h),
            'color_width': int(color.shape[1]),
            'color_height': int(color.shape[0]),
        }
        if self._last_temperature_c is not None:
            meta['temperature'] = self._last_temperature_c
        return color, depth, meta
