"""Migrate legacy scanner_mode / turntable_backend to stable IDs."""

from __future__ import annotations

SCANNER_MODE_TO_ID = {
    'Ferret structured light': 'ferret',
    'Ciclop laser': 'ciclop',
}

TURNTABLE_BACKEND_TO_ID = {
    'None': 'none',
    'Revopoint DAT': 'revopoint_dat',
    'GRBL (Ciclop)': 'ciclop_grbl',
}

SCANNER_ID_TO_MODE = {v: k for k, v in SCANNER_MODE_TO_ID.items()}
TURNTABLE_ID_TO_BACKEND = {v: k for k, v in TURNTABLE_BACKEND_TO_ID.items()}


def _raw_setting_value(settings, key: str, default: str) -> str:
    if not settings.setting_exists(key):
        return default
    st = settings.get_setting(key)
    if st.value is not None:
        return str(st.value)
    return str(st.default) if st.default is not None else default


def _had_loaded_value(settings, key: str) -> bool:
    return settings.setting_exists(key) and settings.get_setting(key).value is not None


def migrate_hardware_settings(settings) -> None:
    """Map legacy string settings to scanner_id / turntable_id if needed."""
    migrated = False
    if settings.setting_exists('hardware_ids_migrated') and settings.get('hardware_ids_migrated', False):
        sync_legacy_from_ids(settings)
        return

    if settings.setting_exists('scanner_id') and not _had_loaded_value(settings, 'scanner_id'):
        mode = _raw_setting_value(settings, 'scanner_mode', 'Ferret structured light')
        settings['scanner_id'] = SCANNER_MODE_TO_ID.get(mode, 'ferret')
        migrated = True
    elif _had_loaded_value(settings, 'scanner_id') and _had_loaded_value(settings, 'scanner_mode'):
        sid = str(settings.get('scanner_id', 'ferret'))
        mode = _raw_setting_value(settings, 'scanner_mode', 'Ferret structured light')
        expected = SCANNER_MODE_TO_ID.get(mode, 'ferret')
        if sid != expected:
            settings['scanner_id'] = expected
            migrated = True

    if settings.setting_exists('turntable_id') and not _had_loaded_value(settings, 'turntable_id'):
        backend = _raw_setting_value(settings, 'turntable_backend', 'None') or 'None'
        settings['turntable_id'] = TURNTABLE_BACKEND_TO_ID.get(backend, 'none')
        migrated = True
    elif _had_loaded_value(settings, 'turntable_id') and _had_loaded_value(settings, 'turntable_backend'):
        tid = str(settings.get('turntable_id', 'none'))
        backend = _raw_setting_value(settings, 'turntable_backend', 'None') or 'None'
        expected = TURNTABLE_BACKEND_TO_ID.get(backend, 'none')
        if tid != expected:
            settings['turntable_id'] = expected
            migrated = True

    if migrated and settings.setting_exists('hardware_ids_migrated'):
        settings['hardware_ids_migrated'] = True

    sync_legacy_from_ids(settings)


def sync_legacy_from_ids(settings) -> None:
    """Keep scanner_mode / turntable_backend in sync for code not yet migrated."""
    sid = settings.get('scanner_id', 'ferret')
    tid = settings.get('turntable_id', 'none')
    if settings.setting_exists('scanner_mode'):
        settings['scanner_mode'] = SCANNER_ID_TO_MODE.get(sid, 'Ferret structured light')
    if settings.setting_exists('turntable_backend'):
        settings['turntable_backend'] = TURNTABLE_ID_TO_BACKEND.get(tid, 'None')
