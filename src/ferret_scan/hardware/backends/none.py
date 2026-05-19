"""No turntable backend."""

from __future__ import annotations

from typing import List

from ferret_scan.hardware.base import TurntableBackend
from ferret_scan.hardware.types import DeviceCapabilities, PreferenceField


class NoneTurntableBackend(TurntableBackend):
    id = 'none'
    label = 'None'

    def is_available(self) -> bool:
        return True

    def preference_fields(self) -> List[PreferenceField]:
        return []

    def turntable_capabilities(self) -> DeviceCapabilities:
        return DeviceCapabilities(scanner_id='', turntable_id=self.id)

    def sync_legacy_settings(self, settings) -> None:
        settings['turntable_backend'] = 'None'

    def create_board(self, parent=None):
        from ferret_scan.engine.driver._noop_board import _NoBoard

        return _NoBoard(parent)
