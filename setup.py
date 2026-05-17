# coding=utf-8

import os
import sys

from setuptools import find_packages, setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from ferret import __version__

# Empty until release tooling sets ferret.__version__; must be valid for setuptools/uv.
_PACKAGE_VERSION = __version__ or '0.0.0.dev0'


def package_data_dirs(source, basedir='/usr/share/ferret'):
    dirs = []

    for dirname, _, files in os.walk(source):
        dirname = os.path.relpath(dirname, source)
        for f in files:
            dirs.append((os.path.join(basedir, dirname), [os.path.join(source, dirname, f)]))

    dirs.append(('/usr/share/applications', ['pkg/linux/ferret.desktop']))

    return dirs


setup(
    name='ferret-scan',
    version=_PACKAGE_VERSION,
    author='Jesús Arroyo Torrens, Mikhail Nikolaevich Klimushin, Benjamin Klop',
    author_email='jesus.arroyo@bq.com, gryphon@night-gryphon.ru',
    description='Structured-light 3D scanning for CR-Scan Ferret (fork of Gryphon Scan)',
    license='GPLv2',
    keywords='ferret scan gryphon structured light 3d scanning',
    url='https://github.com/benklop/ferret-scan',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    scripts=['ferret'],
    data_files=package_data_dirs('res'),
)
