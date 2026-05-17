# coding=utf-8

import os
import sys
from setuptools import setup, find_packages

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from horus import __version__


def package_data_dirs(source, basedir='/usr/share/horus'):
    dirs = []

    for dirname, _, files in os.walk(source):
        dirname = os.path.relpath(dirname, source)
        for f in files:
            dirs.append((os.path.join(basedir, dirname),
                         [os.path.join(source, dirname, f)]))

    dirs.append(('/usr/share/applications', ['pkg/linux/horus.desktop']))

    return dirs


setup(
    name='ferret-scan',
    version=__version__,
    author='Jesús Arroyo Torrens, Mikhail Nikolaevich Klimushin, Benjamin Klop',
    author_email='jesus.arroyo@bq.com, gryphon@night-gryphon.ru',
    description='Structured-light 3D scanning for CR-Scan Ferret (fork of Gryphon Scan / Horus)',

    license='GPLv2',
    keywords="ferret scan horus gryphon structured light 3d scanning",
    url='https://github.com/benklop/ferret-scan',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    scripts=['horus'],
    data_files=package_data_dirs('res'),
)
