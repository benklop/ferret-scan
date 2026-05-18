"""Engine facades bound at application startup (see core.app_state.set_app_context).

Use ``from ferret_scan.runtime_engine import driver`` — proxies resolve after ``bind()``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ferret_scan.core.context import AppContext


class _EngineRef:
    """Lazy reference filled by :func:`bind` (safe for ``from runtime_engine import x``)."""

    __slots__ = ('_name', '_target')

    def __init__(self, name: str) -> None:
        self._name = name
        self._target: Any = None

    def _set(self, target: Any) -> None:
        self._target = target

    def _get(self) -> Any:
        if self._target is None:
            raise RuntimeError(f'runtime_engine.{self._name} is not bound; FerretApp must call set_app_context() first')
        return self._target

    def __getattr__(self, name: str) -> Any:
        return getattr(self._get(), name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ('_name', '_target'):
            object.__setattr__(self, name, value)
        else:
            setattr(self._get(), name, value)

    def __bool__(self) -> bool:
        return self._target is not None

    def __repr__(self) -> str:
        if self._target is None:
            return f'<EngineRef {self._name} (unbound)>'
        return repr(self._target)


driver: _EngineRef = _EngineRef('driver')
ciclop_scan: _EngineRef = _EngineRef('ciclop_scan')
current_video: _EngineRef = _EngineRef('current_video')
camera_intrinsics: _EngineRef = _EngineRef('camera_intrinsics')
scanner_autocheck: _EngineRef = _EngineRef('scanner_autocheck')
laser_triangulation: _EngineRef = _EngineRef('laser_triangulation')
platform_extrinsics: _EngineRef = _EngineRef('platform_extrinsics')
combo_calibration: _EngineRef = _EngineRef('combo_calibration')
image_capture: _EngineRef = _EngineRef('image_capture')
image_detection: _EngineRef = _EngineRef('image_detection')
laser_segmentation: _EngineRef = _EngineRef('laser_segmentation')
point_cloud_generation: _EngineRef = _EngineRef('point_cloud_generation')
point_cloud_roi: _EngineRef = _EngineRef('point_cloud_roi')
cloud_correction: _EngineRef = _EngineRef('cloud_correction')


def bind(ctx: AppContext) -> None:
    driver._set(ctx.driver)
    ciclop_scan._set(ctx.ciclop_scan)
    current_video._set(ctx.current_video)
    camera_intrinsics._set(ctx.camera_intrinsics)
    scanner_autocheck._set(ctx.scanner_autocheck)
    laser_triangulation._set(ctx.laser_triangulation)
    platform_extrinsics._set(ctx.platform_extrinsics)
    combo_calibration._set(ctx.combo_calibration)
    image_capture._set(ctx.image_capture)
    image_detection._set(ctx.image_detection)
    laser_segmentation._set(ctx.laser_segmentation)
    point_cloud_generation._set(ctx.point_cloud_generation)
    point_cloud_roi._set(ctx.point_cloud_roi)
    cloud_correction._set(ctx.cloud_correction)
