"""Process-wide application context (set once by FerretApp)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ferret_scan.core.context import AppContext

_context: AppContext | None = None


def set_app_context(ctx: AppContext) -> None:
    global _context
    _context = ctx
    from ferret_scan import runtime_engine

    runtime_engine.bind(ctx)


def get_app_context() -> AppContext:
    if _context is None:
        raise RuntimeError('AppContext not initialized; FerretApp must call set_app_context() first')
    return _context


def try_get_app_context() -> AppContext | None:
    return _context
