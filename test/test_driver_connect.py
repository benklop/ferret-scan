"""Driver connect lifecycle (no hardware)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ferret_scan.engine.driver.driver import ConnectState, Driver


def test_connect_calls_reset_not_init():
    drv = Driver.__new__(Driver)
    drv._before_callback = None
    drv._after_callback = None
    drv._connect_thread = None
    drv._state = ConnectState.DISCONNECTED
    with patch.object(drv, 'reset') as mock_reset:
        with patch('ferret_scan.engine.driver.driver.threading.Thread') as thread_cls:
            thread_cls.return_value = MagicMock()
            Driver.connect(drv)
            mock_reset.assert_called_once()
            thread_cls.assert_called_once()


def test_shutdown_joins_connect_thread():
    drv = Driver.__new__(Driver)
    thread = MagicMock()
    thread.is_alive.return_value = True
    drv._connect_thread = thread
    with patch.object(drv, 'disconnect'):
        Driver.shutdown(drv, join_timeout=0.1)
    thread.join.assert_called_once_with(timeout=0.1)
