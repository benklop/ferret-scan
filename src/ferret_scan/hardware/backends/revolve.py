"""Revopoint Dual-Axis Turntable backend (librevolve)."""

from __future__ import annotations

from typing import List

from ferret_scan.hardware.base import TurntableBackend
from ferret_scan.hardware.types import DeviceCapabilities, PreferenceField, WidgetType
from ferret_scan.revolve import revolve_available


def _(s):
    return s


class RevolveTurntableBackend(TurntableBackend):
    id = 'revopoint_dat'
    label = 'Revopoint DAT'

    def is_available(self) -> bool:
        return revolve_available()

    def preference_fields(self) -> List[PreferenceField]:
        return [
            PreferenceField(
                'revolve_device_address',
                _('Revopoint BLE address'),
                WidgetType.COMBO,
                choices_fn='revolve_address_list',
                tooltip=_('MAC address from BLE scan, or empty for auto-select.'),
            ),
            PreferenceField(
                'invert_motor',
                _('Invert motor direction'),
                WidgetType.CHECK,
            ),
        ]

    def turntable_capabilities(self) -> DeviceCapabilities:
        return DeviceCapabilities(
            scanner_id='',
            turntable_id=self.id,
            has_ble_turntable=True,
            toolbar_rotate=True,
        )

    def sync_legacy_settings(self, settings) -> None:
        settings['turntable_backend'] = 'Revopoint DAT'

    def create_board(self, parent=None):
        from ferret_scan.engine.driver.revolve_board import RevolveBoard

        return RevolveBoard(parent)
