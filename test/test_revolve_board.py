"""Revopoint turntable board adapter (no hardware)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ferret_scan.engine.driver.revolve_board import RevolveBoard, _ferret_rotation_speed


def test_ferret_rotation_speed_mapping():
    fast = _ferret_rotation_speed(1000.0)
    slow = _ferret_rotation_speed(1.0)
    assert fast < slow
    assert 35.0 <= fast <= 131.0
    assert 35.0 <= slow <= 131.0


@patch('librevolve.SyncDialAxisTurntable')
def test_revolve_board_connect(mock_sync_cls):
    mock_tt = MagicMock()
    mock_tt.device_address = 'DE:B6:85:86:6C:5A'
    mock_sync_cls.return_value = mock_tt

    with patch('ferret_scan.engine.driver.revolve_board.profile') as mock_profile:
        mock_profile.settings.get.side_effect = lambda k, d=None: {
            'revolve_device_address': '',
            'invert_motor': False,
            'motor_speed_scanning': 200.0,
        }.get(k, d)

        board = RevolveBoard()
        board.connect()

    assert board._is_connected
    mock_tt.connect.assert_called_once()
    mock_tt.zero.assert_called_once()


@patch('librevolve.SyncDialAxisTurntable')
def test_revolve_board_motor_move(mock_sync_cls):
    mock_tt = MagicMock()
    mock_tt.get_rotation_angle.return_value = 10
    mock_sync_cls.return_value = mock_tt

    board = RevolveBoard()
    board._is_connected = True
    board._tt = mock_tt
    board._motor_direction = 1

    board.motor_move(0.45, nonblocking=False)

    mock_tt.rotate.assert_called_once_with(0.45)
    mock_tt.wait_rotation.assert_called_once()


@patch('ferret_scan.revolve.revolve_available', return_value=True)
@patch('ferret_scan.diy.diy_available', return_value=False)
def test_create_board_revolve(_diy, _rev):
    from ferret_scan.engine.driver.board import create_board

    with patch('ferret_scan.engine.driver.board.turntable_backend', return_value='Revopoint DAT'):
        board = create_board()
    assert isinstance(board, RevolveBoard)
