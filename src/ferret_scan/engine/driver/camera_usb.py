"""DIY USB camera (libciclops) — OpenCV only, no macOS UVC."""

from ferret_scan.diy import diy_available

if diy_available():
    from ciclops.camera_usb import Camera_usb  # noqa: F401
else:
    raise ImportError('camera_usb requires ferret-scan[diy] (libciclops)')
