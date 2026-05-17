#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Ferret Scan GUI entry (invoked by the ./ferret binstub).

import os
import sys

os.environ.setdefault('WXSUPPRESS_SIZER_FLAGS_CHECK', '1')

_REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(_REPO, 'src'))

from ferret.util import compat  # noqa: F401, E402

try:
    import wx  # noqa: F401
    import cv2  # noqa: F401
    import OpenGL  # noqa: F401
    import serial  # noqa: F401
    import numpy  # noqa: F401
    import scipy  # noqa: F401
    import matplotlib  # noqa: F401
except ImportError as exc:
    print(exc, file=sys.stderr)
    print('Run: ./scripts/dev-setup', file=sys.stderr)
    sys.exit(1)

from ferret.util import resources

_resdir = os.path.join(_REPO, 'res')
if not os.path.isdir(_resdir):
    _resdir = '/usr/share/ferret'
resources.set_base_path(_resdir)


def main():
    if getattr(sys, 'frozen', False):
        appdir = sys._MEIPASS
    else:
        appdir = _REPO
    os.chdir(appdir)
    from ferret.gui import app
    app.FerretApp().MainLoop()


if __name__ == '__main__':
    main()
