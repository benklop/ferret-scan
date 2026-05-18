import logging
import re

import cv2

import ciclops._config as _config

logger = logging.getLogger(__name__)


def parse_usb_camera_index(camera_id):
    """Extract OpenCV device index from a profile camera_id string."""
    if camera_id is None:
        return None
    text = str(camera_id).strip()
    if not text:
        return None
    match = re.search(r'video(\d+)', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    match = re.search(r'(\d+)\s*$', text)
    if match:
        return int(match.group(1))
    if text[-1].isdigit():
        return int(text[-1])
    return None


class WrongCamera(Exception):
    def __init__(self):
        Exception.__init__(self, 'Wrong Camera')


class CameraNotConnected(Exception):
    def __init__(self):
        Exception.__init__(self, 'Camera Not Connected')


class InvalidVideo(Exception):
    def __init__(self):
        Exception.__init__(self, 'Invalid Video')


class WrongDriver(Exception):
    def __init__(self):
        Exception.__init__(self, 'Wrong Driver')


class InputOutputError(Exception):
    def __init__(self):
        Exception.__init__(self, 'V4L2 Input/Output Error')


class Camera:
    """Camera class. For accessing to the scanner camera"""

    def __init__(self, parent=None, camera_id=0):
        self.parent = parent
        self.camera_id = camera_id
        self.unplug_callback = None

        self.initialize()

    def initialize(self):
        self._brightness = 0
        self._contrast = 0
        self._saturation = 0
        self._exposure = 0
        self._luminosity = 1.0
        self._frame_rate = 0
        self._width = 0  # has to be detected at camera connect
        self._height = 0
        self._rotate = True
        self._hflip = True
        self._vflip = False
        self._focus = 0

    def read_profile(self):
        self.set_frame_rate(int(_config.settings()['frame_rate']))
        self.set_resolution(_config.settings()['camera_width'], _config.settings()['camera_height'])
        self.set_rotate(_config.settings()['camera_rotate'])
        self.set_hflip(_config.settings()['camera_hflip'])
        self.set_vflip(_config.settings()['camera_vflip'])
        self.set_luminosity(_config.settings()['luminosity'])
        if self.focus_supported():
            self.set_focus(_config.settings()['camera_focus'])

    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def set_unplug_callback(self, value):
        self.unplug_callback = value

    def capture_image(self, flush=0):
        # flush buffered frames
        # 0 - no flush
        # -1 - auto flush
        # n - flush exactly n frames
        raise NotImplementedError

    def save_image(self, filename, image):
        if image is not None:
            # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(filename, image)

    def set_rotate(self, value):
        self._rotate = value

    def set_hflip(self, value):
        self._hflip = value

    def set_vflip(self, value):
        self._vflip = value

    def set_brightness(self, value):
        self._brightness = value

    def set_contrast(self, value):
        self._contrast = value

    def set_saturation(self, value):
        self._saturation = value

    def set_exposure(self, value, force=False):
        self._exposure = value

    def set_luminosity(self, value):
        possible_values = {'High': 0.5, 'Medium': 1.0, 'Low': 2.0}
        self._luminosity = possible_values[value]

    def set_frame_rate(self, value):
        self._frame_rate = value

    def set_resolution_supported(self):
        return False

    def set_resolution(self, width, height):
        if width > 0 and height > 0:
            self._width = width
            self._height = height

    def set_light(self, idx, brightness):
        raise NotImplementedError

    def get_brightness(self):
        return self._brightness

    def get_exposure(self):
        return self._exposure

    def get_resolution(self):
        if self._rotate:
            return int(self._height), int(self._width)
        else:
            return int(self._width), int(self._height)

    def get_video_list(self):
        raise NotImplementedError

    def set_focus(self, value):
        self._focus = value

    def get_focus(self):
        return self._focus

    def focus_supported(self):
        return False

    def set_camera_id_from_settings(self, camera_id):
        index = parse_usb_camera_index(camera_id)
        if index is not None:
            self.camera_id = index
