# -*- coding: utf-8 -*-
# Ferret structured-light camera bridge (Python 2 Horus UI → Python 3 libferret snap).

from horus.util import profile

import json
import os
import subprocess
import tempfile
import shutil

import cv2
import numpy as np

from horus.engine.driver.camera import Camera, CameraNotConnected

import logging
logger = logging.getLogger(__name__)


class FerretNotAvailable(Exception):
    pass


class Camera_ferret(Camera):
    """CR-Scan Ferret via libferret snap script (pyorbbecsdk on Python 3)."""

    def __init__(self, parent=None, camera_id=0):
        Camera.__init__(self)
        self._is_connected = False
        self._last_image = None
        self._snap_script = self._find_snap_script()
        self._python3 = profile.settings.get('ferret_python3', 'python3')
        self._libferret_root = profile.settings.get('ferret_libferret_root', '')
        self.initialize()
        self._width = 1280
        self._height = 720

    def _find_snap_script(self):
        here = os.path.dirname(os.path.abspath(__file__))
        root = os.path.abspath(os.path.join(here, '..', '..', '..', '..'))
        script = os.path.join(root, 'scripts', 'ferret_snap_rgbd.py')
        if os.path.isfile(script):
            return script
        script2 = os.path.join(os.getcwd(), 'scripts', 'ferret_snap_rgbd.py')
        if os.path.isfile(script2):
            return script2
        return script

    def connect(self):
        if not os.path.isfile(self._snap_script):
            raise FerretNotAvailable(
                "Missing scripts/ferret_snap_rgbd.py — clone libferret paths or set ferret_libferret_root")
        try:
            self._test_snap()
        except subprocess.CalledProcessError as e:
            raise FerretNotAvailable("Ferret snap failed: {0}".format(e))
        self._is_connected = True
        logger.info("Ferret camera connected (snap bridge)")

    def _test_snap(self):
        tmp = tempfile.mkdtemp(prefix='ferret_test_')
        try:
            self._run_snap(tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def _run_snap(self, out_dir):
        env = os.environ.copy()
        if self._libferret_root:
            env['FERRET_LIBFERRET_ROOT'] = self._libferret_root
        sdk_root = os.path.join(self._libferret_root, 'OrbbecSDK_v2') if self._libferret_root else ''
        if sdk_root and os.path.isdir(sdk_root):
            env['LD_LIBRARY_PATH'] = os.path.join(
                sdk_root, 'build', 'linux_x86_64', 'lib') + ':' + env.get('LD_LIBRARY_PATH', '')
        cmd = [self._python3, self._snap_script, out_dir]
        subprocess.check_call(cmd, env=env)

    def disconnect(self):
        self._is_connected = False

    def capture_image(self, flush=0):
        if not self._is_connected:
            raise CameraNotConnected()
        color, depth, meta = self.capture_rgbd()
        self._last_image = color
        return color

    def capture_rgbd(self):
        if not self._is_connected:
            raise CameraNotConnected()
        tmp = tempfile.mkdtemp(prefix='ferret_scan_')
        try:
            self._run_snap(tmp)
            color = cv2.imread(os.path.join(tmp, 'color.png'))
            depth = cv2.imread(os.path.join(tmp, 'depth.png'), cv2.IMREAD_UNCHANGED)
            with open(os.path.join(tmp, 'meta.json'), 'r') as f:
                meta = json.load(f)
            return color, depth, meta
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def set_light(self, idx, brightness):
        pass

    def get_video_list(self):
        return ['CR-Scan Ferret']

    def set_resolution_supported(self):
        return False

    def focus_supported(self):
        return False
