"""Import smoke tests (no GUI, no camera hardware)."""

from __future__ import annotations

import pytest


@pytest.mark.needs_wx
def test_import_profile():
    import ferret_scan.util.profile  # noqa: F401


def test_import_board():
    from ferret_scan.engine.driver.board import Board

    assert Board().baud_rate == 115200
