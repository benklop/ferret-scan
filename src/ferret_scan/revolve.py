"""Optional Revopoint DAT integration via librevolve."""

from __future__ import annotations

import importlib.util


def revolve_available() -> bool:
    return importlib.util.find_spec('librevolve') is not None
