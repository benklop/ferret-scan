# Ferret structured-light camera bridge (Python 2 Horus UI → Python 3 libferret snap).

import json
import logging
import os
import shutil
import subprocess
import tempfile

import cv2

from ferret.engine.driver.camera import Camera, CameraNotConnected
from ferret.util import profile, runtime

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
        self._python3 = os.environ.get('FERRET_PYTHON', profile.settings.get('ferret_python3', 'python3'))
        self._libferret_root = profile.settings.get('ferret_libferret_root', '') or runtime.libferret_root()
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
                'Missing scripts/ferret_snap_rgbd.py — clone libferret paths or set ferret_libferret_root'
            )
        try:
            self._test_snap()
        except FerretNotAvailable:
            raise
        except subprocess.CalledProcessError as e:
            raise FerretNotAvailable(f'Ferret connect test failed: {e}')
        self._is_connected = True
        logger.info('Ferret camera connected (snap bridge)')

    def _test_snap(self):
        tmp = tempfile.mkdtemp(prefix='ferret_test_')
        try:
            self._run_snap(tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def _ferret_env(self):
        env = runtime.augmented_environ()
        if self._libferret_root:
            env['FERRET_LIBFERRET_ROOT'] = self._libferret_root
        return env

    def _run_snap(self, out_dir):
        cmd = [self._python3, self._snap_script, out_dir]
        try:
            subprocess.check_output(cmd, env=self._ferret_env(), stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            detail = (e.output or b'').decode('utf-8', errors='replace').strip()
            raise FerretNotAvailable(f'Ferret snap failed: {e}\n{detail}')

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
            with open(os.path.join(tmp, 'meta.json')) as f:
                meta = json.load(f)
            return color, depth, meta
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def set_light(self, idx, brightness):
        pass

    def get_video_list(self):
        return ['CR-Scan Ferret']

    def set_camera_id_from_settings(self, camera_id):
        pass

    def set_resolution_supported(self):
        return False

    def focus_supported(self):
        return False
