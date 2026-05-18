# Ferret structured-light camera (in-process libferret / pyorbbecsdk).

import logging

from ferret_scan.engine.driver.camera import Camera, CameraNotConnected
from ferret_scan.services.ferret_rgbd import FerretRgbdError, FerretRgbdService
from ferret_scan.util import runtime

logger = logging.getLogger(__name__)


class FerretNotAvailable(Exception):
    pass


class Camera_ferret(Camera):
    """CR-Scan Ferret via libferret FerretRgbdService."""

    def __init__(self, parent=None, camera_id=0):
        Camera.__init__(self)
        self._is_connected = False
        self._last_image = None
        self._service = None
        self.initialize()
        self._width = 1280
        self._height = 720

    def connect(self):
        try:
            self._service = FerretRgbdService(runtime.libferret_root())
            self._service.connect()
        except (FerretRgbdError, FileNotFoundError, OSError) as e:
            raise FerretNotAvailable(str(e)) from e
        except Exception as e:
            raise FerretNotAvailable(f'Ferret connect failed: {e}') from e
        self._is_connected = True
        logger.info('Ferret camera connected')

    def disconnect(self):
        self._is_connected = False
        if self._service is not None:
            try:
                self._service.disconnect()
            except Exception:
                logger.debug('Ferret service disconnect', exc_info=True)
            self._service = None

    def capture_image(self, flush=0):
        if not self._is_connected:
            raise CameraNotConnected()
        color, _depth, _meta = self.capture_rgbd()
        self._last_image = color
        return color

    def capture_rgbd(self):
        if not self._is_connected or self._service is None:
            raise CameraNotConnected()
        try:
            return self._service.capture_rgbd()
        except FerretRgbdError as e:
            raise CameraNotConnected(str(e)) from e

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
