"""CR-Scan Ferret scanner backend (libferret / Orbbec)."""

from __future__ import annotations

from typing import List

from ferret_scan.hardware.base import ScannerBackend
from ferret_scan.hardware.types import DeviceCapabilities, PreferenceField, WidgetType


def _(s):
    return s


class FerretScannerBackend(ScannerBackend):
    id = 'ferret'
    label = 'CR-Scan Ferret'

    def is_available(self) -> bool:
        return True

    def preference_fields(self) -> List[PreferenceField]:
        return [
            PreferenceField(
                'ferret_libferret_root',
                _('libferret path'),
                WidgetType.PATH,
                tooltip=_('Path to libferret (submodule or clone with OrbbecSDK_v2).'),
            ),
            PreferenceField(
                'ferret_low_bandwidth',
                _('Low-bandwidth depth'),
                WidgetType.CHECK,
                tooltip=_('Use 640×400 depth stream instead of 1280×800.'),
            ),
            PreferenceField(
                'ferret_laser_on_connect',
                _('Laser on at connect'),
                WidgetType.CHECK,
            ),
            PreferenceField(
                'ferret_laser_settle_s',
                _('Laser settle time (s)'),
                WidgetType.SPIN_FLOAT,
                min_value=0.0,
                max_value=30.0,
                advanced=True,
            ),
            PreferenceField(
                'ferret_turntable_optional',
                _('Turntable optional'),
                WidgetType.CHECK,
                tooltip=_('Allow Ferret connect when the turntable is absent (manual rotation).'),
            ),
            PreferenceField(
                'ferret_calibration_board_sn',
                _('Calibration board SN'),
                WidgetType.TEXT,
                advanced=True,
                tooltip=_('Serial number on the back of the optional Ferret calibration board.'),
            ),
        ]

    def scanner_capabilities(self) -> DeviceCapabilities:
        return DeviceCapabilities(
            scanner_id=self.id,
            turntable_id='',
            has_ferret_board_calibration=True,
            calibration_panels=frozenset({'ferret_board_calibration'}),
            adjustment_panels=frozenset({'scan_capture'}),
        )

    def sync_legacy_settings(self, settings) -> None:
        settings['scanner_mode'] = 'Ferret structured light'
