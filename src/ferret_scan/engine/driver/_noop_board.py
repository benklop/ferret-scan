"""Placeholder turntable board when libciclops is not used."""


class BoardNotConnected(Exception):
    pass


class WrongFirmware(Exception):
    pass


class OldFirmware(Exception):
    pass


class _NoBoard:
    def __init__(self, parent=None):
        self.parent = parent

    def connect(self):
        return True

    def disconnect(self):
        pass

    def get_serial_list(self):
        return []

    def set_light(self, *args, **kwargs):
        return False

    def lasers_on(self, *args, **kwargs):
        pass

    def lasers_off(self, *args, **kwargs):
        pass

    def motor_step(self, *args, **kwargs):
        pass

    def motor_speed(self, *args, **kwargs):
        pass

    def motor_acceleration(self, *args, **kwargs):
        pass

    def motor_move(self, *args, **kwargs):
        pass

    def motor_enable(self, *args, **kwargs):
        pass

    def motor_disable(self, *args, **kwargs):
        pass

    def reset_origin(self, *args, **kwargs):
        pass

    def send_gcode(self, *args, **kwargs):
        pass
