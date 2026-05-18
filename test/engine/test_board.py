import unittest


class BoardTest(unittest.TestCase):
    def setUp(self):
        from ferret_scan.engine.driver.board import Board

        self.board = Board()

    def test_serial_name(self):
        self.assertEqual(self.board.serial_name, '/dev/ttyUSB0')

    def test_baud_rate(self):
        self.assertEqual(self.board.baud_rate, 115200)
