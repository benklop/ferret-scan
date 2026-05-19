"""Ciclop DIY laser scanner backend (libciclops)."""

from __future__ import annotations

from typing import List

from ferret_scan.diy import diy_available
from ferret_scan.hardware.base import ScannerBackend
from ferret_scan.hardware.types import DeviceCapabilities, PreferenceField, WidgetType


def _(s):
    return s


class CiclopScannerBackend(ScannerBackend):
    id = 'ciclop'
    label = 'Ciclop laser'

    def is_available(self) -> bool:
        return diy_available()

    def preference_fields(self) -> List[PreferenceField]:
        return [
            PreferenceField(
                'camera_id',
                _('Camera ID'),
                WidgetType.COMBO,
                choices_fn='video_list',
            ),
            PreferenceField(
                'luminosity',
                _('Luminosity'),
                WidgetType.COMBO,
                choices=('High', 'Medium', 'Low'),
                tooltip=_('Change luminosity until colored lines appear over the chess pattern.'),
            ),
        ]

    def scanner_capabilities(self) -> DeviceCapabilities:
        return DeviceCapabilities(
            scanner_id=self.id,
            turntable_id='',
            has_line_lasers=True,
            has_usb_camera_picker=True,
            has_pattern_calibration=True,
            has_laser_triangulation=True,
            has_laser_segmentation_adjustment=True,
            has_control_workbench=True,
            toolbar_lasers=True,
            calibration_panels=frozenset(
                {
                    'pattern_settings',
                    'scanner_autocheck',
                    'rotating_platform_settings',
                    'video_settings',
                    'camera_intrinsics',
                    'laser_triangulation',
                    'platform_extrinsics',
                }
            ),
            adjustment_panels=frozenset(
                {
                    'scan_capture',
                    'scan_segmentation',
                    'calibration_capture',
                    'calibration_segmentation',
                }
            ),
        )

    def sync_legacy_settings(self, settings) -> None:
        settings['scanner_mode'] = 'Ciclop laser'
