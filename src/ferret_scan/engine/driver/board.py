"""Turntable board: resolved via hardware registry."""

from __future__ import annotations

from ferret_scan.hardware.registry import get_registry
from ferret_scan.util import profile


def turntable_backend() -> str:
    from ferret_scan.hardware.migration import TURNTABLE_ID_TO_BACKEND
    from ferret_scan.hardware.registry import get_registry

    tid = get_registry().active_turntable_id()
    return TURNTABLE_ID_TO_BACKEND.get(tid, profile.settings.get('turntable_backend', 'None') or 'None')


def create_board(parent=None):
    return get_registry().create_board(parent)


# Re-export exceptions and Board symbol for legacy imports.

try:
    from ferret_scan.diy import diy_available

    if diy_available():
        from ciclops.board import Board, BoardNotConnected, OldFirmware, WrongFirmware  # noqa: F401
    else:
        from ferret_scan.engine.driver._noop_board import (  # noqa: F401
            BoardNotConnected,
            OldFirmware,
            WrongFirmware,
        )
        from ferret_scan.engine.driver._noop_board import _NoBoard as Board  # noqa: F401
except ImportError:
    from ferret_scan.engine.driver._noop_board import (  # noqa: F401
        BoardNotConnected,
        OldFirmware,
        WrongFirmware,
    )
