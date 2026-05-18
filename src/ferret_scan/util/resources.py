import gettext
import os

from ferret_scan.util import system

resource_base_path = ''


def set_base_path(path):
    global resource_base_path
    resource_base_path = path


def get_path_for_resource(directory, resource_name):
    assert os.path.isdir(resource_base_path), f'{resource_base_path} is not a directory'
    path = os.path.normpath(os.path.join(resource_base_path, directory, resource_name))
    return path


def get_path_for_image(name):
    return get_path_for_resource('images', name)


def get_path_for_firmware(name):
    return get_path_for_resource('firmware', name)


def get_path_for_logger(name):
    return get_path_for_resource('logger', name)


def get_path_for_tools(name):
    if system.is_windows():
        path = get_path_for_resource('tools/windows', name)
    elif system.is_darwin():
        path = get_path_for_resource('tools/darwin', name)
    else:
        path = get_path_for_resource('tools/linux', name)
    return path


def get_path_for_mesh(name):
    return get_path_for_resource('meshes', name)


def setup_localization(selected_language=None):
    # Default to english
    languages = ['en']

    if selected_language is not None:
        for item in get_language_options():
            if item[1] == selected_language and item[0] is not None:
                languages = [item[0]]

    locale_path = os.path.normpath(os.path.join(resource_base_path, 'locale'))
    translation = gettext.translation('ferret', locale_path, languages, fallback=True)
    translation.install()


def get_language_options():
    return [
        ['en', 'English'],
        ['es', 'Español'],
        ['fr', 'Français'],
        ['de', 'Deutsch'],
        ['it', 'Italiano'],
        ['pt', 'Português'],
    ]
