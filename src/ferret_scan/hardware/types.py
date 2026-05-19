"""Shared types for hardware backends."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import FrozenSet, Optional, Tuple


class WidgetType(str, Enum):
    TEXT = 'text'
    COMBO = 'combo'
    CHECK = 'check'
    PATH = 'path'
    SPIN_FLOAT = 'spin_float'
    SPIN_INT = 'spin_int'


@dataclass(frozen=True)
class PreferenceField:
    key: str
    label: str
    widget: WidgetType = WidgetType.TEXT
    advanced: bool = False
    tooltip: str = ''
    choices: Optional[Tuple[str, ...]] = None
    choices_fn: Optional[str] = None  # dynamic choices: video_list, serial_list, revolve_address_list
    min_value: Optional[float] = None
    max_value: Optional[float] = None


@dataclass
class DeviceCapabilities:
    """Combined UI/engine flags for the active scanner + turntable pair."""

    scanner_id: str
    turntable_id: str
    has_line_lasers: bool = False
    has_grbl_turntable: bool = False
    has_ble_turntable: bool = False
    has_usb_camera_picker: bool = False
    has_firmware_upload: bool = False
    has_pattern_calibration: bool = False
    has_laser_triangulation: bool = False
    has_ferret_board_calibration: bool = False
    has_laser_segmentation_adjustment: bool = False
    has_control_workbench: bool = False
    toolbar_rotate: bool = False
    toolbar_lasers: bool = False
    calibration_panels: FrozenSet[str] = field(default_factory=frozenset)
    adjustment_panels: FrozenSet[str] = field(default_factory=frozenset)
