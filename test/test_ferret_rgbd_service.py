"""FerretRgbdService with mocked device."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest


@pytest.fixture
def mock_frames():
    depth = MagicMock()
    depth.get_depth_scale.return_value = 1.0
    depth.get_width.return_value = 2
    depth.get_height.return_value = 2
    depth.get_data.return_value = np.zeros(4, dtype=np.uint16).tobytes()

    color = MagicMock()
    color.get_format.return_value = 0
    color.get_width.return_value = 2
    color.get_height.return_value = 2
    color.get_data.return_value = np.zeros(12, dtype=np.uint8).tobytes()

    fs = MagicMock()
    fs.get_depth_frame.return_value = depth
    fs.get_color_frame.return_value = color
    return fs


def test_capture_rgbd_mock(mock_frames):
    from ferret_scan.services.ferret_rgbd import FerretRgbdService

    dev = MagicMock()
    dev.pipeline.wait_for_frames.return_value = mock_frames

    with patch('ferret_scan.services.ferret_rgbd._get_device_class') as gdc:
        gdc.return_value.open.return_value = dev
        svc = FerretRgbdService(libferret_root='/tmp/libferret')
        svc.connect()
        color, depth, meta = svc.capture_rgbd()

    assert color.shape == (2, 2, 3)
    assert depth.shape == (2, 2)
    assert meta['depth_width'] == 2
    svc.disconnect()
    dev.pipeline.stop.assert_called_once()
