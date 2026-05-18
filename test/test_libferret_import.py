"""ferret_scan and libferret ``ferret.device`` can coexist in one process."""

from __future__ import annotations

import os
import sys

import pytest


def test_ferret_scan_and_libferret_device_import():
    repo = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, os.path.join(repo, 'src'))
    import ferret_scan  # noqa: F401

    assert ferret_scan.__name__ == 'ferret_scan'

    scripts_lib = os.path.join(repo, 'scripts', 'lib')
    if scripts_lib not in sys.path:
        sys.path.insert(0, scripts_lib)
    from libferret_import import get_ferret_device_class

    libferret = os.path.join(repo, 'packages', 'libferret')
    if not os.path.isfile(os.path.join(libferret, 'pyproject.toml')):
        pytest.skip('libferret submodule not initialized')

    os.environ.setdefault('FERRET_LIBFERRET_ROOT', libferret)
    try:
        FerretDevice = get_ferret_device_class()
    except ImportError as exc:
        pytest.skip(f'libferret device API not available: {exc}')

    assert FerretDevice.__module__.startswith('ferret.')
    from ferret_scan.util import resources

    resources.set_base_path(os.path.join(repo, 'res'))
    import ferret_scan.util.profile  # noqa: F401 — app package still importable
