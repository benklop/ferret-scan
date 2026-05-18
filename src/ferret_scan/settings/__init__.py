"""Application settings."""

from ferret_scan.settings.paths import get_base_path, get_config_dir, get_data_dir
from ferret_scan.settings.persistence import default_libferret_root, repo_root, settings_dir
from ferret_scan.settings.registry import register, run_registered
from ferret_scan.settings.schema import Setting, Settings

__all__ = [
    'Setting',
    'Settings',
    'default_libferret_root',
    'get_base_path',
    'get_config_dir',
    'get_data_dir',
    'register',
    'repo_root',
    'run_registered',
    'settings_dir',
]
