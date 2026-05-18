"""Import libferret's Python ``ferret`` package (device API) alongside ferret_scan."""

from __future__ import annotations

import os
import sys


def _libferret_root():
    root = os.environ.get('FERRET_LIBFERRET_ROOT', '')
    if root and os.path.isfile(os.path.join(root, 'pyproject.toml')):
        return root
    here = os.path.dirname(os.path.abspath(__file__))
    vendored = os.path.normpath(os.path.join(here, '..', '..', 'libferret'))
    if os.path.isfile(os.path.join(vendored, 'pyproject.toml')):
        return vendored
    raise ImportError('libferret not found; set FERRET_LIBFERRET_ROOT or run ./scripts/dev-setup')


def get_ferret_device_class():
    """Return the libferret ``FerretDevice`` class (``ferret.device``)."""
    lib = _libferret_root()
    pkg_path = os.path.join(lib, 'python')
    if not os.path.isdir(pkg_path):
        raise ImportError('libferret python tree missing: {0}'.format(pkg_path))

    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

    from ferret.device import FerretDevice

    return FerretDevice
