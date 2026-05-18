"""Settings path helpers."""

from __future__ import annotations

import os

from ferret_scan.settings.persistence import default_libferret_root, repo_root, settings_dir


def test_repo_root_exists():
    root = repo_root()
    assert os.path.isdir(root)
    assert os.path.isfile(os.path.join(root, 'pyproject.toml'))


def test_settings_dir_under_xdg():
    path = settings_dir()
    assert path.endswith('ferret-scan')
    assert 'config' in path or '.config' in path


def test_default_libferret_root_vendored():
    root = default_libferret_root()
    assert os.path.isfile(os.path.join(root, 'pyproject.toml'))
