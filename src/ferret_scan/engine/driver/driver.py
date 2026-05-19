import logging
import threading

from ferret_scan.hardware.registry import get_registry
from ferret_scan.util import profile

logger = logging.getLogger(__name__)


class ConnectState:
    DISCONNECTED = 'disconnected'
    CONNECTING = 'connecting'
    CONNECTED = 'connected'
    ERROR = 'error'


class Driver:
    """Driver class. For managing scanner hardware."""

    def __init__(self):
        self._board = None
        self.camera = self._create_camera()
        self.is_connected = False
        self.unplugged = False
        self._connect_thread = None
        self._state = ConnectState.DISCONNECTED
        self._before_callback = None
        self._after_callback = None

    @property
    def board(self):
        if self._board is None:
            from ferret_scan.engine.driver.board import create_board

            self._board = create_board(self)
        return self._board

    def _turntable_enabled(self):
        return get_registry().turntable_enabled()

    @property
    def connect_state(self):
        return self._state

    def _is_ferret(self):
        return get_registry().is_ferret_scanner()

    def _is_diy_mode(self):
        return get_registry().is_ciclop_scanner()

    def _create_camera(self):
        if self._is_ferret():
            from ferret_scan.engine.driver.camera_ferret import Camera_ferret

            return Camera_ferret(self)
        if self._is_diy_mode():
            from ferret_scan.engine.driver.camera_usb import Camera_usb

            return Camera_usb(self)
        from ferret_scan.engine.driver.camera_ferret import Camera_ferret

        return Camera_ferret(self)

    def reset(self):
        if self._connect_thread is not None and self._connect_thread.is_alive():
            logger.warning('Reset while connect thread still running')
        self._state = ConnectState.DISCONNECTED
        try:
            self.camera.disconnect()
        except Exception:
            logger.debug('Camera disconnect during reset', exc_info=True)
        if self._board is not None:
            try:
                self.board.disconnect()
            except Exception:
                logger.debug('Board disconnect during reset', exc_info=True)
        self.is_connected = False
        self._board = None
        self.camera = self._create_camera()

    def connect(self):
        if self._state == ConnectState.CONNECTING:
            logger.warning('Connect requested while already connecting')
            return
        self.reset()
        self._state = ConnectState.CONNECTING
        if self._before_callback is not None:
            self._before_callback()
        self._connect_thread = threading.Thread(target=self._connect, name='ferret-driver-connect', daemon=True)
        self._connect_thread.start()

    def _connect(self):
        exception = None
        self.is_connected = False
        try:
            self.camera.connect()
            if self._turntable_enabled():
                optional = self._is_ferret() and profile.settings.get('ferret_turntable_optional', True)
                if optional:
                    try:
                        self.board.connect()
                    except Exception as board_err:
                        logger.warning('Turntable not connected: %s', board_err)
                else:
                    self.board.connect()
            elif self._is_diy_mode():
                self.board.connect()
        except Exception as e:
            exception = e
            logger.error('Failed to connect: ' + str(e))
        else:
            self.is_connected = True
            self._state = ConnectState.CONNECTED
        finally:
            if exception is None:
                self.unplugged = False
                response = (True, self.is_connected)
            else:
                self._state = ConnectState.ERROR
                response = (False, exception)
                self.disconnect()
            if self._after_callback is not None:
                self._after_callback(response)

    def disconnect(self):
        self.is_connected = False
        self._state = ConnectState.DISCONNECTED
        try:
            self.camera.disconnect()
        except Exception:
            logger.debug('Camera disconnect failed', exc_info=True)
        if self._board is not None:
            try:
                self.board.disconnect()
            except Exception:
                logger.debug('Board disconnect failed', exc_info=True)

    def shutdown(self, join_timeout: float = 5.0) -> None:
        self.disconnect()
        if self._connect_thread is not None and self._connect_thread.is_alive():
            self._connect_thread.join(timeout=join_timeout)
        self._connect_thread = None

    def set_callbacks(self, before, after):
        self._before_callback = before
        self._after_callback = after


driver = Driver()
