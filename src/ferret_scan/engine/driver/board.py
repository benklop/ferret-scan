"""Turntable board: GRBL (libciclops), Revopoint DAT (librevolve), or no-op."""

from __future__ import annotations

from ferret_scan.util import profile


def turntable_backend() -> str:
    return profile.settings.get('turntable_backend', 'None') or 'None'


def create_board(parent=None):
    backend = turntable_backend()
    if backend == 'Revopoint DAT':
        from ferret_scan.revolve import revolve_available

        if revolve_available():
            from ferret_scan.engine.driver.revolve_board import RevolveBoard

            return RevolveBoard(parent)
        raise RuntimeError('turntable_backend is Revopoint DAT but librevolve is not installed')

    if backend == 'GRBL (Ciclop)':
        from ferret_scan.diy import diy_available

        if diy_available():
            from ciclops.board import Board

            return Board(parent)
        raise RuntimeError('turntable_backend is GRBL (Ciclop) but libciclops is not installed')

    from ferret_scan.engine.driver._noop_board import _NoBoard

    return _NoBoard(parent)


# Re-export exceptions and Board symbol for legacy imports.

try:
    from ferret_scan.diy import diy_available

    if diy_available():
        from ciclops.board import Board, OldFirmware, WrongFirmware  # noqa: F401
    else:
        from ferret_scan.engine.driver._noop_board import OldFirmware, WrongFirmware  # noqa: F401
        from ferret_scan.engine.driver._noop_board import _NoBoard as Board  # noqa: F401
except ImportError:
    from ferret_scan.engine.driver._noop_board import (  # noqa: F401
        OldFirmware,
        WrongFirmware,
    )
