"""Hardware registry: available backends and combined capabilities."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from ferret_scan.hardware.backends.ciclop import CiclopScannerBackend
from ferret_scan.hardware.backends.ciclop_turntable import CiclopTurntableBackend
from ferret_scan.hardware.backends.ferret import FerretScannerBackend
from ferret_scan.hardware.backends.none import NoneTurntableBackend
from ferret_scan.hardware.backends.revolve import RevolveTurntableBackend
from ferret_scan.hardware.base import ScannerBackend, TurntableBackend
from ferret_scan.hardware.migration import sync_legacy_from_ids
from ferret_scan.hardware.types import DeviceCapabilities, PreferenceField
from ferret_scan.util import profile

logger = logging.getLogger(__name__)

_registry: Optional['HardwareRegistry'] = None
_fallback_warned: set = set()


class HardwareRegistry:
    def __init__(self):
        self._scanners: Dict[str, ScannerBackend] = {
            FerretScannerBackend.id: FerretScannerBackend(),
            CiclopScannerBackend.id: CiclopScannerBackend(),
        }
        self._turntables: Dict[str, TurntableBackend] = {
            NoneTurntableBackend.id: NoneTurntableBackend(),
            RevolveTurntableBackend.id: RevolveTurntableBackend(),
            CiclopTurntableBackend.id: CiclopTurntableBackend(),
        }

    def available_scanners(self) -> List[ScannerBackend]:
        return [s for s in self._scanners.values() if s.is_available()]

    def available_turntables(self) -> List[TurntableBackend]:
        return [t for t in self._turntables.values() if t.is_available()]

    def _warn_fallback(self, kind: str, requested: str, resolved: str) -> None:
        key = (kind, requested, resolved)
        if key in _fallback_warned or requested == resolved:
            return
        _fallback_warned.add(key)
        logger.warning('%s backend %r unavailable; using %r', kind, requested, resolved)
        if profile.settings.setting_exists(f'{kind}_id'):
            profile.settings[f'{kind}_id'] = resolved
            sync_legacy_from_ids(profile.settings)

    def get_scanner(self, scanner_id: str) -> ScannerBackend:
        requested = scanner_id
        if scanner_id not in self._scanners:
            resolved = FerretScannerBackend.id
            self._warn_fallback('scanner', requested, resolved)
            return self._scanners[resolved]
        backend = self._scanners[scanner_id]
        if not backend.is_available():
            resolved = FerretScannerBackend.id
            self._warn_fallback('scanner', requested, resolved)
            return self._scanners[resolved]
        return backend

    def get_turntable(self, turntable_id: str) -> TurntableBackend:
        requested = turntable_id
        if turntable_id not in self._turntables:
            resolved = NoneTurntableBackend.id
            self._warn_fallback('turntable', requested, resolved)
            return self._turntables[resolved]
        backend = self._turntables[turntable_id]
        if not backend.is_available():
            resolved = NoneTurntableBackend.id
            self._warn_fallback('turntable', requested, resolved)
            return self._turntables[resolved]
        return backend

    def active_scanner_id(self) -> str:
        sid = profile.settings.get('scanner_id', 'ferret')
        return self.get_scanner(sid).id

    def active_turntable_id(self) -> str:
        tid = profile.settings.get('turntable_id', 'none')
        return self.get_turntable(tid).id

    def active_scanner(self) -> ScannerBackend:
        return self.get_scanner(self.active_scanner_id())

    def active_turntable(self) -> TurntableBackend:
        return self.get_turntable(self.active_turntable_id())

    def set_active_scanner(self, scanner_id: str) -> None:
        scanner = self.get_scanner(scanner_id)
        profile.settings['scanner_id'] = scanner.id
        scanner.sync_legacy_settings(profile.settings)

    def set_active_turntable(self, turntable_id: str) -> None:
        turntable = self.get_turntable(turntable_id)
        profile.settings['turntable_id'] = turntable.id
        turntable.sync_legacy_settings(profile.settings)

    def capabilities(self) -> DeviceCapabilities:
        scanner = self.active_scanner()
        turntable = self.active_turntable()
        sc = scanner.scanner_capabilities()
        tc = turntable.turntable_capabilities()

        cal_panels = set(sc.calibration_panels)
        adj_panels = set(sc.adjustment_panels)
        has_control = sc.has_control_workbench or tc.has_control_workbench
        turntable_enabled = turntable.id != NoneTurntableBackend.id

        return DeviceCapabilities(
            scanner_id=scanner.id,
            turntable_id=turntable.id,
            has_line_lasers=sc.has_line_lasers,
            has_grbl_turntable=tc.has_grbl_turntable,
            has_ble_turntable=tc.has_ble_turntable,
            has_usb_camera_picker=sc.has_usb_camera_picker,
            has_firmware_upload=tc.has_firmware_upload,
            has_pattern_calibration=sc.has_pattern_calibration,
            has_laser_triangulation=sc.has_laser_triangulation,
            has_ferret_board_calibration=sc.has_ferret_board_calibration,
            has_laser_segmentation_adjustment=sc.has_laser_segmentation_adjustment,
            has_control_workbench=has_control,
            toolbar_rotate=turntable_enabled,
            toolbar_lasers=sc.has_line_lasers or tc.toolbar_lasers,
            calibration_panels=frozenset(cal_panels),
            adjustment_panels=frozenset(adj_panels),
        )

    def preference_fields(
        self, *, advanced: bool = False, scanner_id: str | None = None, turntable_id: str | None = None
    ) -> List[PreferenceField]:
        scanner = self.get_scanner(scanner_id or self.active_scanner_id())
        turntable = self.get_turntable(turntable_id or self.active_turntable_id())
        fields: List[PreferenceField] = []
        fields.extend(scanner.preference_fields())
        fields.extend(turntable.preference_fields())
        if not advanced:
            return [f for f in fields if not f.advanced]
        return fields

    def create_board(self, parent=None):
        return self.active_turntable().create_board(parent)

    def is_ferret_scanner(self) -> bool:
        return self.active_scanner_id() == FerretScannerBackend.id

    def is_ciclop_scanner(self) -> bool:
        return self.active_scanner_id() == CiclopScannerBackend.id

    def turntable_enabled(self) -> bool:
        return self.active_turntable_id() != NoneTurntableBackend.id


def get_registry() -> HardwareRegistry:
    global _registry
    if _registry is None:
        _registry = HardwareRegistry()
    return _registry
