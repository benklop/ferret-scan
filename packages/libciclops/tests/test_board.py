import unittest

import ciclops._config as _config


class _StubSettings(dict):
    def get(self, key, default=None):
        return super().get(key, default)


class BoardTest(unittest.TestCase):
    def setUp(self):
        _config._settings_provider = lambda: _StubSettings({'serial_name': '/dev/ttyUSB0', 'baud_rate': 115200})
        from ciclops.board import Board

        self.board = Board()

    def test_serial_name(self):
        self.assertEqual(self.board.serial_name, '/dev/ttyUSB0')

    def test_baud_rate(self):
        self.assertEqual(self.board.baud_rate, 115200)


if __name__ == '__main__':
    unittest.main()
