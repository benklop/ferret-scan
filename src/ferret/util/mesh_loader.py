# This file is part of the Horus Project


__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.\
                 Copyright (C) 2013 David Braam from Cura Project'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import logging
import os

from ferret.util.mesh_loaders import ply, stl

logger = logging.getLogger(__name__)


def load_supported_extensions():
    """return a list of supported file extensions for loading."""
    return ['.ply', '.stl']


def save_supported_extensions():
    """return a list of supported file extensions for saving."""
    return ['.ply']


def _resolve_mesh_path(filename):
    if not filename:
        return None
    if os.path.isfile(filename):
        return filename
    from ferret.util import resources

    for name in (filename, os.path.basename(filename)):
        try:
            path = resources.get_path_for_mesh(name)
        except AssertionError:
            continue
        if os.path.isfile(path):
            return path
    return filename


def load_mesh(filename):
    """
    loadMesh loads one model from a file.
    """
    path = _resolve_mesh_path(filename)
    if path and os.path.isfile(path):
        ext = os.path.splitext(path)[1].lower()
        if ext == '.ply':
            return ply.load_scene(path)
        if ext == '.stl':
            return stl.load_scene(path)
        logger.error('Error: Unknown model extension: %s' % (ext))
    else:
        logger.error('Error: Model file not found: %s' % (filename))
    return None


def save_mesh(filename, _object):
    """
    Save a object into the file given by the filename.
    Use the filename extension to find out the file format.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.ply':
        ply.save_scene(filename, _object)
        return
    logger.error('Error: Unknown model extension: %s' % (ext))
