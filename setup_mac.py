# coding=utf-8

import os
import sys
from setuptools import setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from ferret import __version__

APP = ['ferret']
DATA_FILES = ['res']

PLIST = {
    u'CFBundleName': u'Ferret Scan',
    u'CFBundleShortVersionString': __version__,
    u'CFBundleVersion': __version__,
    u'CFBundleIdentifier': u'com.benklop.ferret-scan-' + __version__,
    u'LSMinimumSystemVersion': u'10.8',
    u'LSApplicationCategoryType': u'public.app-category.graphics-design'
}

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'res/ferret.icns',
    'plist': PLIST
}

setup(name='ferret-scan',
      version=__version__,
      author='Jesús Arroyo Torrens',
      author_email='jesus.arroyo@bq.com',
      description='Ferret Scan — structured-light 3D scanning',
      license='GPLv2',
      keywords="ferret scan gryphon structured light 3d",
      url='https://www.diwo.bq.com/tag/ciclop',
      app=APP,
      data_files=DATA_FILES,
      options={'py2app': OPTIONS},
      setup_requires=['py2app'])
