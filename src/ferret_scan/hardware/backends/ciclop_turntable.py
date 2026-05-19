"""Ciclop GRBL turntable backend (libciclops board)."""

from __future__ import annotations

from typing import List

from ferret_scan.diy import diy_available
from ferret_scan.hardware.base import TurntableBackend
from ferret_scan.hardware.types import DeviceCapabilities, PreferenceField, WidgetType


def _(s):
    return s


class CiclopTurntableBackend(TurntableBackend):
    id = 'ciclop_grbl'
    label = 'GRBL (Ciclop)'

    def is_available(self) -> bool:
        return diy_available()

    def preference_fields(self) -> List[PreferenceField]:
        return [
            PreferenceField(
                'serial_name',
                _('Serial name'),
                WidgetType.COMBO,
                choices_fn='serial_list',
            ),
            PreferenceField(
                'baud_rate',
                _('Baud rate'),
                WidgetType.COMBO,
                choices=('9600', '14400', '19200', '38400', '57600', '115200'),
                advanced=True,
            ),
            PreferenceField(
                'invert_motor',
                _('Invert motor direction'),
                WidgetType.CHECK,
            ),
            PreferenceField(
                'board',
                _('AVR board'),
                WidgetType.COMBO,
                choices=('Arduino Uno', 'BT ATmega328'),
                advanced=True,
            ),
        ]

    def turntable_capabilities(self) -> DeviceCapabilities:
        return DeviceCapabilities(
            scanner_id='',
            turntable_id=self.id,
            has_grbl_turntable=True,
            has_firmware_upload=True,
            has_control_workbench=True,
            toolbar_rotate=True,
            toolbar_lasers=True,
        )

    def sync_legacy_settings(self, settings) -> None:
        settings['turntable_backend'] = 'GRBL (Ciclop)'

    def create_board(self, parent=None):
        from ciclops.board import Board

        return Board(parent)
