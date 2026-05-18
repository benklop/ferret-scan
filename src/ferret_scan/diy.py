"""Optional Ciclop / libciclops integration."""

import importlib.util


def diy_available() -> bool:
    return importlib.util.find_spec('ciclops') is not None


def configure_ciclops() -> None:
    if not diy_available():
        return
    import ciclops

    from ferret_scan.util import profile

    ciclops.configure(profile.settings)
