"""Tests for hardware registry and settings migration."""

from ferret_scan.hardware.migration import (
    migrate_hardware_settings,
    sync_legacy_from_ids,
)
from ferret_scan.hardware.registry import get_registry
from ferret_scan.settings import ferret as ferret_settings
from ferret_scan.settings.schema import Settings


def _fresh_settings():
    s = Settings()
    ferret_settings.register_ferret_settings(s)
    return s


def test_migrate_scanner_mode_to_id():
    s = _fresh_settings()
    s.get_setting('scanner_id').value = None
    s.get_setting('scanner_mode').value = 'Ciclop laser'
    migrate_hardware_settings(s)
    assert s['scanner_id'] == 'ciclop'
    assert s['scanner_mode'] == 'Ciclop laser'


def test_migrate_turntable_backend_to_id():
    s = _fresh_settings()
    s.get_setting('turntable_id').value = None
    s.get_setting('turntable_backend').value = 'Revopoint DAT'
    migrate_hardware_settings(s)
    assert s['turntable_id'] == 'revopoint_dat'


def test_registry_ferret_capabilities():
    s = _fresh_settings()
    s['scanner_id'] = 'ferret'
    s['turntable_id'] = 'none'
    sync_legacy_from_ids(s)
    import ferret_scan.util.profile as profile_mod

    profile_mod.settings = s
    caps = get_registry().capabilities()
    assert caps.has_ferret_board_calibration
    assert not caps.has_pattern_calibration
    assert not caps.toolbar_lasers


def test_migration_conflict_prefers_legacy():
    s = _fresh_settings()
    s['scanner_id'] = 'ferret'
    s.get_setting('scanner_mode').value = 'Ciclop laser'
    s['turntable_id'] = 'none'
    s.get_setting('turntable_backend').value = 'GRBL (Ciclop)'
    migrate_hardware_settings(s)
    assert s['scanner_id'] == 'ciclop'
    assert s['turntable_id'] == 'ciclop_grbl'
    assert s['hardware_ids_migrated'] is True


def test_toolbar_lasers_merge():
    from ferret_scan.hardware.backends.ciclop import CiclopScannerBackend
    from ferret_scan.hardware.backends.ciclop_turntable import CiclopTurntableBackend

    sc = CiclopScannerBackend().scanner_capabilities()
    tc = CiclopTurntableBackend().turntable_capabilities()
    assert sc.has_line_lasers or tc.toolbar_lasers


def test_registry_ciclop_capabilities():
    from ferret_scan.hardware.backends.ciclop import CiclopScannerBackend
    from ferret_scan.hardware.backends.ciclop_turntable import CiclopTurntableBackend

    scanner = CiclopScannerBackend()
    turntable = CiclopTurntableBackend()
    sc = scanner.scanner_capabilities()
    tc = turntable.turntable_capabilities()
    assert sc.has_pattern_calibration
    assert sc.has_line_lasers
    assert tc.toolbar_rotate
