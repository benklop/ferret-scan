"""Camera service protocol for RGB-D backends."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class RgbdCameraService(Protocol):
    """Structured-light RGB-D capture (Ferret / Orbbec)."""

    def connect(self) -> None: ...

    def disconnect(self) -> None: ...

    def capture_rgbd(self) -> tuple[Any, Any, dict]:
        """Return (color_rgb, depth_uint16_mm, meta dict)."""
        ...
