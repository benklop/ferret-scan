"""Backward-compatible settings facade."""

import logging
import math
import os

import numpy as np

from ferret_scan.settings.paths import get_config_dir
from ferret_scan.settings.schema import Settings

logger = logging.getLogger(__name__)

settings = Settings()
settings._initialize_settings()

laser_bg_scanning = [None, None]
laser_bg_scanning_enable = False

laser_bg_calibration = [None, None]
laser_bg_calibration_enable = False


def default_libferret_root():
    from ferret_scan.settings.persistence import default_libferret_root as _root

    try:
        return _root()
    except RuntimeError:
        return ''


def _migrate_libferret_root():
    from ferret_scan.settings.persistence import default_libferret_root

    if not settings.setting_exists('ferret_libferret_root'):
        return
    current = settings['ferret_libferret_root']
    if current and os.path.isfile(os.path.join(str(current), 'pyproject.toml')):
        return
    try:
        settings['ferret_libferret_root'] = default_libferret_root()
    except RuntimeError:
        settings['ferret_libferret_root'] = ''


def load_settings():
    if os.path.exists(os.path.join(get_config_dir(), 'settings.json')):
        settings.load_settings()
    _migrate_libferret_root()
    from ferret_scan.hardware.migration import migrate_hardware_settings

    migrate_hardware_settings(settings)


def get_machine_size_polygons():
    machine_shape = settings['machine_shape']
    if machine_shape == 'Circular':
        size = np.array(
            [settings['machine_diameter'], settings['machine_diameter'], settings['machine_height']], np.float32
        )
    elif machine_shape == 'Rectangular':
        size = np.array([settings['machine_width'], settings['machine_depth'], settings['machine_height']], np.float32)
    return get_size_polygons(size, machine_shape)


def get_roi_size_polygons():
    machine_shape = settings['machine_shape']
    if machine_shape == 'Circular':
        size = np.array([settings['roi_diameter'], settings['roi_diameter'], settings['roi_height']], np.float32)
    elif machine_shape == 'Rectangular':
        size = np.array([settings['roi_width'], settings['roi_depth'], settings['roi_height']], np.float32)
    return get_size_polygons(size, machine_shape)


def get_size_polygons(size, machine_shape):
    ret = []
    if machine_shape == 'Circular':
        circle = []
        steps = 32
        for n in range(0, steps):
            circle.append(
                [
                    math.cos(float(n) / steps * 2 * math.pi) * size[0] / 2,
                    math.sin(float(n) / steps * 2 * math.pi) * size[1] / 2,
                ]
            )
        ret.append(np.array(circle, np.float32))

    elif machine_shape == 'Rectangular':
        rectangle = []
        rectangle.append([-size[0] / 2, size[1] / 2])
        rectangle.append([size[0] / 2, size[1] / 2])
        rectangle.append([size[0] / 2, -size[1] / 2])
        rectangle.append([-size[0] / 2, -size[1] / 2])
        ret.append(np.array(rectangle, np.float32))

    w = 20
    h = 20
    ret.append(
        np.array(
            [
                [-size[0] / 2, -size[1] / 2],
                [-size[0] / 2 + w + 2, -size[1] / 2],
                [-size[0] / 2 + w, -size[1] / 2 + h],
                [-size[0] / 2, -size[1] / 2 + h],
            ],
            np.float32,
        )
    )
    ret.append(
        np.array(
            [
                [size[0] / 2 - w - 2, -size[1] / 2],
                [size[0] / 2, -size[1] / 2],
                [size[0] / 2, -size[1] / 2 + h],
                [size[0] / 2 - w, -size[1] / 2 + h],
            ],
            np.float32,
        )
    )
    ret.append(
        np.array(
            [
                [-size[0] / 2 + w + 2, size[1] / 2],
                [-size[0] / 2, size[1] / 2],
                [-size[0] / 2, size[1] / 2 - h],
                [-size[0] / 2 + w, size[1] / 2 - h],
            ],
            np.float32,
        )
    )
    ret.append(
        np.array(
            [
                [size[0] / 2, size[1] / 2],
                [size[0] / 2 - w - 2, size[1] / 2],
                [size[0] / 2 - w, size[1] / 2 - h],
                [size[0] / 2, size[1] / 2 - h],
            ],
            np.float32,
        )
    )

    return ret
