"""runtime_engine lazy refs resolve after bind."""

from __future__ import annotations

import pytest

from ferret_scan.core.app_state import set_app_context
from ferret_scan.core.context import AppContext
from ferret_scan.runtime_engine import driver


def test_driver_proxy_before_bind():
    with pytest.raises(RuntimeError, match='not bound'):
        _ = driver.board


def test_driver_proxy_after_bind():
    ctx = AppContext.create()
    set_app_context(ctx)
    assert driver.board is ctx.driver.board
