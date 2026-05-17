"""Import smoke tests (no GUI, no camera hardware)."""

from __future__ import annotations

import pytest


def _wx_available() -> bool:
    try:
        import wx  # noqa: F401
    except ImportError:
        return False
    return True


@pytest.mark.skipif(not _wx_available(), reason='wxPython not available or incompatible')
def test_import_profile():
    import ferret.util.profile  # noqa: F401


def test_import_board():
    from ferret.engine.driver.board import Board

    assert Board().baud_rate == 115200
