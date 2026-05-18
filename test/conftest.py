"""Pytest configuration and shared fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]


def pytest_configure(config):
    """Configure resource paths before profile.py is imported by tests."""
    from ferret_scan.util import resources

    resources.set_base_path(str(_ROOT / 'res'))
    try:
        from ferret_scan.diy import configure_ciclops

        configure_ciclops()
    except Exception:
        pass


def _prepend_wx_runtime_ld_path() -> None:
    import os

    wx_dir = _ROOT / '.venv' / 'lib'
    if not wx_dir.is_dir():
        return
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
        import wx  # noqa: F401
    except Exception:
        return False
    return True


@pytest.fixture(autouse=True)
def _wx_gate(request):
    """Skip tests marked needs_wx when wx is unavailable."""
    if request.node.get_closest_marker('needs_wx') and not _wx_works():
        pytest.skip('wxPython not available or incompatible with system libraries')
