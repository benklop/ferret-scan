"""Pytest configuration and shared fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from ferret.util import resources

_ROOT = Path(__file__).resolve().parents[1]

# profile.py loads at import time and expects res/ to be configured (see ferret_gui.py).
resources.set_base_path(str(_ROOT / 'res'))


def _prepend_wx_runtime_ld_path() -> None:
    import os

    wx_dir = _ROOT / '.venv' / 'lib'
    if not wx_dir.is_dir():
        return
    # platlib/wx with bundled libwx_*.so from a Phoenix source build
    matches = list(wx_dir.glob('python*/site-packages/wx/libwx_gtk3u_core*.so*'))
    if not matches:
        return
    wx_pkg = matches[0].parent
    prev = os.environ.get('LD_LIBRARY_PATH', '')
    wx = str(wx_pkg)
    if not prev.startswith(wx):
        os.environ['LD_LIBRARY_PATH'] = f'{wx}:{prev}' if prev else wx


def _wx_works() -> bool:
    _prepend_wx_runtime_ld_path()
    try:
        import wx._core  # noqa: F401
    except Exception:
        return False
    return True


@pytest.fixture(autouse=True)
def require_wx():
    """Skip ferret imports when wxPython is missing or incompatible (e.g. Fedora pip wheel)."""
    if not _wx_works():
        pytest.skip('wxPython not available or incompatible with system libraries')
