"""Configure PyOpenGL to match the active Linux display stack.

Must run before ``import OpenGL`` (see ``scripts/ferret_gui.py``).
"""

from __future__ import annotations

import os
import sys


def _on_wayland() -> bool:
    return bool(os.environ.get('WAYLAND_DISPLAY')) or os.environ.get('XDG_SESSION_TYPE', '').lower() == 'wayland'


def configure() -> None:
    """Align PyOpenGL (and optionally GDK) with native Wayland/EGL or X11/GLX."""
    if not sys.platform.startswith('linux'):
        return

    if os.environ.get('FERRET_FORCE_X11'):
        os.environ['GDK_BACKEND'] = 'x11'
        os.environ['PYOPENGL_PLATFORM'] = 'glx'
        return

    if _on_wayland():
        # wx GLCanvas on Wayland uses EGL; PyOpenGL must use eglGetCurrentContext.
        os.environ['PYOPENGL_PLATFORM'] = 'egl'
    else:
        os.environ.setdefault('PYOPENGL_PLATFORM', 'glx')
