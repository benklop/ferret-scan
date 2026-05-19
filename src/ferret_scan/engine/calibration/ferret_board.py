"""Ferret calibration-board session (pose capture; compute deferred)."""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from ferret_scan.settings.paths import get_base_path
from ferret_scan.util import profile

logger = logging.getLogger(__name__)


def _(s):
    return s


DEFAULT_POSES = [
    {'id': 0, 'hint_xy': _('Center, default height'), 'hint_z': _('Match the guide model')},
    {'id': 1, 'hint_xy': _('Move left'), 'hint_z': _('Keep height')},
    {'id': 2, 'hint_xy': _('Move right'), 'hint_z': _('Keep height')},
    {'id': 3, 'hint_xy': _('Move forward'), 'hint_z': _('Keep height')},
    {'id': 4, 'hint_xy': _('Move back'), 'hint_z': _('Keep height')},
    {'id': 5, 'hint_xy': _('Center'), 'hint_z': _('Raise scanner')},
    {'id': 6, 'hint_xy': _('Center'), 'hint_z': _('Lower scanner')},
    {'id': 7, 'hint_xy': _('Corner pose'), 'hint_z': _('Match the guide model')},
]


@dataclass
class PoseCapture:
    pose_id: int
    timestamp: float
    temperature_c: Optional[float] = None
    color_path: Optional[str] = None
    depth_path: Optional[str] = None


@dataclass
class FerretBoardSession:
    board_sn: str = ''
    captures: List[PoseCapture] = field(default_factory=list)
    complete: bool = False

    def session_path(self) -> str:
        cal_dir = os.path.join(get_base_path(), 'ferret_calibration')
        os.makedirs(cal_dir, exist_ok=True)
        sn = self.board_sn or 'unknown'
        safe = ''.join(c if c.isalnum() or c in '-_' else '_' for c in sn)
        return os.path.join(cal_dir, f'session_{safe}.json')

    def save(self) -> None:
        data = {
            'board_sn': self.board_sn,
            'complete': self.complete,
            'captures': [asdict(c) for c in self.captures],
        }
        with open(self.session_path(), 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, board_sn: str) -> 'FerretBoardSession':
        session = cls(board_sn=board_sn)
        path = session.session_path()
        if not os.path.isfile(path):
            return session
        try:
            with open(path) as f:
                data = json.load(f)
            session.board_sn = data.get('board_sn', board_sn)
            session.complete = bool(data.get('complete', False))
            session.captures = []
            for c in data.get('captures', []):
                session.captures.append(
                    PoseCapture(
                        pose_id=int(c['pose_id']),
                        timestamp=float(c['timestamp']),
                        temperature_c=c.get('temperature_c'),
                        color_path=c.get('color_path'),
                        depth_path=c.get('depth_path'),
                    )
                )
        except (KeyError, TypeError, ValueError):
            logger.warning('Corrupt ferret calibration session %s', path, exc_info=True)
        except OSError:
            logger.debug('Failed to load ferret calibration session', exc_info=True)
        return session


class FerretBoardCalibration:
    """Pose state machine for optional Ferret calibration board workflow."""

    def __init__(self):
        self.session = FerretBoardSession()
        self._pose_index = 0

    @property
    def pose_count(self) -> int:
        return len(DEFAULT_POSES)

    @property
    def current_pose_index(self) -> int:
        return self._pose_index

    @property
    def current_pose(self) -> Dict[str, Any]:
        idx = min(self._pose_index, len(DEFAULT_POSES) - 1)
        return DEFAULT_POSES[idx]

    @property
    def poses_done(self) -> bool:
        return self._pose_index >= len(DEFAULT_POSES)

    def start(self, board_sn: str) -> None:
        profile.settings['ferret_calibration_board_sn'] = board_sn
        self.session = FerretBoardSession.load(board_sn)
        self.session.board_sn = board_sn
        self._pose_index = len(self.session.captures)

    def reset_session(self, *, delete_files: bool = True) -> None:
        if delete_files:
            for cap in self.session.captures:
                for path in (cap.color_path, cap.depth_path):
                    if path and os.path.isfile(path):
                        try:
                            os.remove(path)
                        except OSError:
                            logger.debug('Could not remove %s', path, exc_info=True)
            json_path = self.session.session_path()
            if os.path.isfile(json_path):
                try:
                    os.remove(json_path)
                except OSError:
                    pass
        self.session = FerretBoardSession(board_sn=self.session.board_sn)
        self._pose_index = 0

    def capture_current_pose(self) -> PoseCapture:
        from ferret_scan.runtime_engine import driver

        pose = self.current_pose
        cal_dir = os.path.join(get_base_path(), 'ferret_calibration', 'frames')
        os.makedirs(cal_dir, exist_ok=True)
        stamp = int(time.time() * 1000)
        color_path = os.path.join(cal_dir, f'pose{pose["id"]}_{stamp}_color.npy')
        depth_path = os.path.join(cal_dir, f'pose{pose["id"]}_{stamp}_depth.npy')

        color, depth, meta = driver.camera.capture_rgbd()
        np.save(color_path, color)
        np.save(depth_path, depth)

        temp = None
        if isinstance(meta, dict) and meta.get('temperature') is not None:
            temp = float(meta['temperature'])

        capture = PoseCapture(
            pose_id=pose['id'],
            timestamp=time.time(),
            temperature_c=temp,
            color_path=color_path,
            depth_path=depth_path,
        )
        self.session.captures.append(capture)
        self.session.save()
        self._pose_index += 1
        return capture

    def finish_acquisition(self) -> None:
        self.session.complete = True
        self.session.save()

    def run_compute(self) -> str:
        return _(
            'Pose captures are saved locally. Factory calibration from the board serial number '
            'is not available yet (see doc/FERRET_BOARD_CALIBRATION.md and the cr-scan-reverse project). '
            'Depth accuracy for scanning still uses Orbbec firmware calibration.'
        )


_session: Optional[FerretBoardCalibration] = None


def get_ferret_board_calibration() -> FerretBoardCalibration:
    global _session
    if _session is None:
        _session = FerretBoardCalibration()
    return _session
