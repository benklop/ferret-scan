"""XDG and legacy path helpers for settings and user data."""

import logging
import os
import sys

from ferret_scan.util import system

logger = logging.getLogger(__name__)

_APP_DIRNAME = 'ferret-scan'


def _xdg_config_home():
    env = os.environ.get('XDG_CONFIG_HOME')
    if env:
        return os.path.expanduser(env)
    return os.path.expanduser('~/.config')


def _xdg_data_home():
    env = os.environ.get('XDG_DATA_HOME')
    if env:
        return os.path.expanduser(env)
    return os.path.expanduser('~/.local/share')


def _ensure_dir(path):
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except OSError:
            logger.error('Failed to create directory: %s' % path)


def get_config_dir():
    """User settings directory (settings.json, exported profiles)."""
    if system.is_windows():
        base_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
        if hasattr(sys, 'frozen'):
            base_path = os.path.normpath(os.path.join(base_path, '..'))
    elif system.is_darwin():
        base_path = os.path.join(os.path.expanduser('~/Library/Application Support'), _APP_DIRNAME)
    else:
        base_path = os.path.join(_xdg_config_home(), _APP_DIRNAME)
    _ensure_dir(base_path)
    return base_path


def get_data_dir():
    """User data directory (calibration captures, etc.)."""
    if system.is_windows():
        base_path = get_config_dir()
    elif system.is_darwin():
        base_path = os.path.join(os.path.expanduser('~/Library/Application Support'), _APP_DIRNAME)
    else:
        base_path = os.path.join(_xdg_data_home(), _APP_DIRNAME)
    _ensure_dir(base_path)
    return base_path


def get_base_path():
    """Alias for :func:`get_config_dir` (default path for settings and profiles)."""
    return get_config_dir()
