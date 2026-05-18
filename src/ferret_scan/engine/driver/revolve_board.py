"""Revopoint Dual-Axis Turntable (BLE) via librevolve."""

from __future__ import annotations

import logging
import threading
import time

from ferret_scan.util import profile

logger = logging.getLogger(__name__)


class BoardNotConnected(Exception):
    pass


class WrongFirmware(Exception):
    pass


class OldFirmware(Exception):
    pass


def _ferret_rotation_speed(dat_ui_value: float) -> float:
    """Map ferret scanning speed (º/s, ~1–1000) to DAT TURNSPEED (35–131, higher = slower)."""
    lo, hi = 35.0, 131.0
    clamped = max(1.0, min(1000.0, float(dat_ui_value)))
    # Invert so faster ferret speed → lower DAT value (faster rotation).
    return hi - (clamped - 1.0) * (hi - lo) / 999.0


class RevolveBoard:
    """Board-compatible adapter for librevolve (rotation only; no lasers)."""

    def __init__(self, parent=None):
        self.parent = parent
        self.unplug_callback = None
        self.serial_name = ''
        self.baud_rate = 0
        self._is_connected = False
        self._motor_direction = 1
        self._motor_speed = 0.0
        self._motor_acceleration = 0
        self._motor_enabled = False
        self._tt = None

    @property
    def device_address(self) -> str:
        return self.serial_name

    @device_address.setter
    def device_address(self, value: str) -> None:
        self.serial_name = value or ''

    def get_serial_list(self):
        """BLE addresses of nearby DAT devices (for preferences combo)."""
        from librevolve import discover_turntables_sync

        try:
            devices = discover_turntables_sync(timeout=8.0, dat_only=True)
            return [d.address for d in devices]
        except Exception:
            logger.debug('BLE scan failed', exc_info=True)
            return []

    def set_unplug_callback(self, value):
        self.unplug_callback = value

    def connect(self):
        from librevolve import SyncDialAxisTurntable, TurntableNotFoundError

        address = profile.settings.get('revolve_device_address', '') or None
        logger.info('Connecting Revopoint DAT%s', f' ({address})' if address else ' (auto)')
        self._is_connected = False
        try:
            self._tt = SyncDialAxisTurntable()
            self._tt.connect(address=address, timeout=30.0)
            self.serial_name = self._tt.device_address or ''
            self._is_connected = True
            self.motor_invert(profile.settings.get('invert_motor', False))
            speed = _ferret_rotation_speed(profile.settings.get('motor_speed_scanning', 200.0))
            self.motor_speed(speed)
            self.motor_reset_origin()
            logger.info('Revopoint DAT connected at %s', self.serial_name)
        except TurntableNotFoundError as exc:
            raise BoardNotConnected(str(exc)) from exc
        except Exception as exc:
            self._close_tt()
            raise BoardNotConnected(str(exc)) from exc

    def _close_tt(self):
        if self._tt is not None:
            try:
                self._tt.close()
            except Exception:
                logger.debug('librevolve close failed', exc_info=True)
            self._tt = None

    def disconnect(self):
        if not self._is_connected and self._tt is None:
            return
        logger.info('Disconnecting Revopoint DAT')
        try:
            if self._tt is not None:
                self._tt.disconnect()
        except Exception:
            logger.debug('Revolve disconnect failed', exc_info=True)
        finally:
            self._close_tt()
            self._is_connected = False

    def motor_invert(self, value):
        self._motor_direction = -1 if value else 1

    def motor_speed(self, value):
        if not self._is_connected or self._tt is None:
            return
        from librevolve import protocol as proto

        if value > 131:
            dat_speed = _ferret_rotation_speed(value)
        else:
            dat_speed = max(35.0, min(131.0, float(value)))
        self._motor_speed = dat_speed
        self._tt.send(proto.cmd_turn_speed(dat_speed))

    def motor_acceleration(self, value):
        self._motor_acceleration = value

    def motor_enable(self):
        self._motor_enabled = True

    def motor_disable(self):
        if self._is_connected and self._tt is not None:
            try:
                self._tt.stop()
            except Exception:
                logger.debug('Revolve stop failed', exc_info=True)
        self._motor_enabled = False

    def motor_reset_origin(self):
        if self._is_connected and self._tt is not None:
            self._tt.zero()

    def motor_move(self, step=0, nonblocking=False, callback=None):
        if not self._is_connected or self._tt is None:
            if callback is not None:
                callback('')
            return

        def do_move():
            try:
                degrees = float(step) * self._motor_direction
                if degrees == 0:
                    return
                angle_before = self._tt.get_rotation_angle()
                self._tt.rotate(degrees)
                if angle_before is not None:
                    target = int(round(angle_before + degrees))
                    self._tt.wait_rotation(target, timeout_s=120.0)
                else:
                    time.sleep(max(0.5, abs(degrees) * 0.08))
            except Exception:
                logger.warning('Turntable move failed', exc_info=True)
            finally:
                if callback is not None:
                    callback('')

        if nonblocking:
            threading.Thread(target=do_move, name='revolve-motor-move', daemon=True).start()
        else:
            do_move()

    def laser_on(self, index):
        pass

    def laser_off(self, index):
        pass

    def lasers_on(self):
        pass

    def lasers_off(self):
        pass

    def ldr_sensor(self, pin):
        return 0

    def send_command(self, req, nonblocking=False, callback=None, read_lines=False):
        if callback is not None:
            callback('')
        return ''
