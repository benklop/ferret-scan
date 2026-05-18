"""Runtime settings bridge (configured by ferret-scan on startup)."""

_settings = None


def configure(settings_mapping):
    """Bind a settings object (e.g. ferret_scan.util.profile.settings)."""
    global _settings
    _settings = settings_mapping


def settings():
    if _settings is None:
        raise RuntimeError('ciclops.configure() must be called before using libciclops')
    return _settings
