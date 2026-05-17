"""Import libferret's Python package without clashing with ferret-scan's ``ferret`` package."""

from __future__ import annotations

import os
import sys


def _libferret_root():
    root = os.environ.get("FERRET_LIBFERRET_ROOT", "")
    if root and os.path.isfile(os.path.join(root, "pyproject.toml")):
        return root
    here = os.path.dirname(os.path.abspath(__file__))
    vendored = os.path.normpath(os.path.join(here, "..", "..", "libferret"))
    if os.path.isfile(os.path.join(vendored, "pyproject.toml")):
        return vendored
    return os.path.expanduser("~/repos/ferret")


def _unload_scan_ferret():
    """Remove ferret-scan's ``ferret`` from sys.modules if already imported."""
    mod = sys.modules.get("ferret")
    if mod is None:
        return
    mod_file = getattr(mod, "__file__", "") or ""
    if "ferret-scan" not in mod_file.replace("\\", "/"):
        return
    for key in list(sys.modules):
        if key == "ferret" or key.startswith("ferret."):
            del sys.modules[key]


def get_ferret_device_class():
    """Return the libferret ``FerretDevice`` class."""
    lib = _libferret_root()
    pkg_path = os.path.join(lib, "python")
    if not os.path.isdir(pkg_path):
        raise ImportError("libferret python tree missing: {0}".format(pkg_path))

    _unload_scan_ferret()
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

    from ferret.device import FerretDevice  # noqa: WPS433

    return FerretDevice
