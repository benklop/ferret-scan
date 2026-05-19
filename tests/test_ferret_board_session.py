"""Tests for Ferret board calibration session."""

from ferret_scan.engine.calibration.ferret_board import (
    FerretBoardCalibration,
    FerretBoardSession,
    PoseCapture,
)


def test_session_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(
        'ferret_scan.engine.calibration.ferret_board.get_base_path',
        lambda: str(tmp_path),
    )
    session = FerretBoardSession(board_sn='TEST-SN-001')
    session.captures = [PoseCapture(pose_id=0, timestamp=1.0, temperature_c=25.0)]
    session.save()

    loaded = FerretBoardSession.load('TEST-SN-001')
    assert loaded.board_sn == 'TEST-SN-001'
    assert len(loaded.captures) == 1
    assert loaded.captures[0].temperature_c == 25.0


def test_reset_session_clears_index(tmp_path, monkeypatch):
    monkeypatch.setattr(
        'ferret_scan.engine.calibration.ferret_board.get_base_path',
        lambda: str(tmp_path),
    )
    engine = FerretBoardCalibration()
    engine.start('SN2')
    engine._pose_index = 3
    engine.reset_session(delete_files=False)
    assert engine.current_pose_index == 0
    assert engine.session.captures == []
