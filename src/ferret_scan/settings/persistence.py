"""XDG paths and libferret root resolution."""

from __future__ import annotations

import os

_APP_DIRNAME = 'ferret-scan'


def repo_root() -> str:
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))


def default_libferret_root() -> str:
    """Prefer vendored libferret submodule in a source checkout."""
    vendored = os.path.join(repo_root(), 'libferret')
    if os.path.isfile(os.path.join(vendored, 'pyproject.toml')):
        return vendored
    env = os.environ.get('FERRET_LIBFERRET_ROOT', '')
    if env and os.path.isfile(os.path.join(env, 'pyproject.toml')):
        return env
    raise RuntimeError('libferret not found: run ./scripts/dev-setup or set FERRET_LIBFERRET_ROOT')


def settings_dir() -> str:
    base = os.environ.get('XDG_CONFIG_HOME') or os.path.join(os.path.expanduser('~'), '.config')
    return os.path.join(base, _APP_DIRNAME)
