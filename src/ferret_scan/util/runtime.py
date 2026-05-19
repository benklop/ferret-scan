"""Repo paths and process environment for dev runs and snap subprocesses."""

import os
import platform


def repo_root():
    if os.environ.get('FERRET_REPO_ROOT'):
        return os.environ['FERRET_REPO_ROOT']
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))


def libferret_root():
    env = os.environ.get('FERRET_LIBFERRET_ROOT', '')
    if env and os.path.isfile(os.path.join(env, 'pyproject.toml')):
        return env
    vendored = os.path.join(repo_root(), 'packages', 'libferret')
    if os.path.isfile(os.path.join(vendored, 'pyproject.toml')):
        return vendored
    raise RuntimeError('libferret not found; run ./scripts/dev-setup')


def resolve_libferret_root():
    """Prefer a valid settings path, then env / packages/libferret."""
    try:
        from ferret_scan.util import profile

        if profile.settings.setting_exists('ferret_libferret_root'):
            configured = profile.settings['ferret_libferret_root'] or ''
            if configured and os.path.isfile(os.path.join(configured, 'pyproject.toml')):
                return configured
    except Exception:
        pass
    return libferret_root()


def _sdk_platform_dir():
    machine = platform.machine().lower()
    if machine in ('x86_64', 'amd64'):
        return 'linux_x86_64'
    if machine in ('aarch64', 'arm64'):
        return 'linux_arm64'
    return f'linux_{machine}'


def sdk_lib_dir():
    return os.path.join(libferret_root(), 'OrbbecSDK_v2', 'build', _sdk_platform_dir(), 'lib')


def pyorbbec_install_lib():
    root = os.environ.get('FERRET_PYORBBECSDK_ROOT', os.path.join(repo_root(), '.deps', 'pyorbbecsdk'))
    return os.path.join(root, 'install', 'lib')


def augmented_environ(base=None):
    env = dict(base or os.environ)
    lib = libferret_root()
    env['FERRET_REPO_ROOT'] = repo_root()
    env['FERRET_LIBFERRET_ROOT'] = lib
    root = repo_root()
    # Only ferret-scan on PYTHONPATH; libferret is loaded via scripts/lib/libferret_import.py
    py_path = [os.path.join(root, 'src')]
    existing = env.get('PYTHONPATH', '')
    if existing:
        py_path.append(existing)
    env['PYTHONPATH'] = os.pathsep.join(py_path)

    ld_parts = []
    for path in (sdk_lib_dir(), pyorbbec_install_lib()):
        if os.path.isdir(path):
            ld_parts.append(path)
    if env.get('LD_LIBRARY_PATH'):
        ld_parts.append(env['LD_LIBRARY_PATH'])
    if ld_parts:
        env['LD_LIBRARY_PATH'] = os.pathsep.join(ld_parts)
    return env
