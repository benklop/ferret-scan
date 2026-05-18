"""AppContext builds a shared driver / calibration_data graph."""

from __future__ import annotations

from ferret_scan.core.context import AppContext
from ferret_scan.engine.calibration.calibration_data import calibration_data


def test_image_capture_shares_module_singletons():
    ctx = AppContext.create()
    assert ctx.image_capture.driver is ctx.driver
    assert ctx.image_capture.calibration_data is ctx.calibration_data
    assert ctx.calibration_data is calibration_data
    assert ctx.laser_triangulation.calibration_data is calibration_data
