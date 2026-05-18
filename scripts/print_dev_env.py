#!/usr/bin/env python3
"""Print dev runtime environment variables (for IDE launch configs)."""

from __future__ import annotations

import json
import os
import platform
import sys


def _repo_root() -> str:
    return os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))


def _libferret_root(repo: str) -> str:
    env = os.environ.get('FERRET_LIBFERRET_ROOT')
    vendored = os.path.join(repo, 'libferret')
    if env and os.path.isfile(os.path.join(env, 'pyproject.toml')):
        return env
    if os.path.isfile(os.path.join(vendored, 'pyproject.toml')):
        return vendored
    raise RuntimeError('libferret not found; run ./scripts/dev-setup')


def _sdk_lib_dir(libferret: str) -> str:
    machine = platform.machine().lower()
    plat = 'linux_x86_64' if machine in ('x86_64', 'amd64') else 'linux_arm64'
    return os.path.join(libferret, 'OrbbecSDK_v2', 'build', plat, 'lib')


def _pyorbbec_root(repo: str) -> str:
    return os.environ.get('FERRET_PYORBBECSDK_ROOT', os.path.join(repo, '.deps', 'pyorbbecsdk'))


def _python_exe(repo: str) -> str:
    venv_py = os.path.join(repo, '.venv', 'bin', 'python')
    if os.path.isfile(venv_py):
        return venv_py
    return os.environ.get('FERRET_PYTHON', sys.executable)


def dev_env() -> dict[str, str]:
    repo = _repo_root()
    libferret = _libferret_root(repo)
    sdk_lib = _sdk_lib_dir(libferret)
    pyob_install = os.path.join(_pyorbbec_root(repo), 'install', 'lib')

    ld_parts = []
    import glob

    for wx_dir in glob.glob(os.path.join(repo, '.venv', 'lib', 'python*/site-packages/wx')):
        if glob.glob(os.path.join(wx_dir, 'libwx_gtk3u_core*.so*')):
            ld_parts.append(wx_dir)
            break
    if os.path.isdir(sdk_lib):
        ld_parts.append(sdk_lib)
    if os.path.isdir(pyob_install):
        ld_parts.append(pyob_install)
    existing_ld = os.environ.get('LD_LIBRARY_PATH', '')
    if existing_ld:
        ld_parts.append(existing_ld)

    env = {
        'FERRET_REPO_ROOT': repo,
        'FERRET_LIBFERRET_ROOT': libferret,
        'FERRET_PYTHON': _python_exe(repo),
        'PYTHONPATH': os.path.join(repo, 'src'),
    }
    if ld_parts:
        env['LD_LIBRARY_PATH'] = ':'.join(ld_parts)
    if sys.platform.startswith('linux'):
        if os.environ.get('FERRET_FORCE_X11'):
            env['GDK_BACKEND'] = 'x11'
            env['PYOPENGL_PLATFORM'] = 'glx'
        elif os.environ.get('WAYLAND_DISPLAY') or os.environ.get('XDG_SESSION_TYPE', '').lower() == 'wayland':
            env['PYOPENGL_PLATFORM'] = 'egl'
        else:
            env.setdefault('PYOPENGL_PLATFORM', 'glx')
    return env


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == '--json':
        print(json.dumps(dev_env(), indent=2))
        return
    for key, value in sorted(dev_env().items()):
        print(f'{key}={value}')


if __name__ == '__main__':
    main()
