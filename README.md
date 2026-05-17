# ferret-scan

Structured-light scanning workbench for the **Creality CR-Scan Ferret**, forked from [gryphon-scan](https://github.com/nightgryphon/gryphon-scan) (Horus lineage).

| Mode | Hardware | Capture |
|------|----------|---------|
| **Ferret structured light** (default) | Orbbec Ferret RGB-D + optional GRBL turntable | Depth + color per turntable step |
| **Ciclop laser** (legacy) | Webcam + line lasers + Ciclop board | Laser triangulation (original Gryphon path) |

## Dependencies

- **Python 2.7** — Horus wx GUI (unchanged from Gryphon)
- **Python 3** — Ferret device access via [libferret](https://github.com/benklop/libferret) + pyorbbecsdk
- OpenCV, wxPython, NumPy, PyOpenGL, pyserial, … (same as Gryphon)

The Ferret path uses `scripts/ferret_snap_rgbd.py` (Python 3) from the Horus process. Configure in **Preferences**:

| Setting | Typical value |
|---------|----------------|
| Scanner mode | `Ferret structured light` |
| libferret path | `~/repos/ferret` |
| Python 3 for Ferret | `python3` |
| Turntable optional | `true` if you rotate manually |

Build [libferret](https://github.com/benklop/libferret) first (`OrbbecSDK_v2` submodule + pyorbbecsdk against that fork).

## Run

```bash
cd ferret-scan
./horus
```

Connect → Control (turntable) → Calibration (camera intrinsics + platform; laser cal not used in Ferret mode) → Scanning.

## Architecture

```
Python 2 (Horus UI)
  └─ camera_ferret → subprocess → Python 3 ferret_snap_rgbd.py
                                    └─ libferret / pyorbbecsdk
  └─ ciclop_scan → depth_to_point_cloud (replaces laser segmentation)
  └─ board.py (GRBL turntable, optional)
```

## Related repos

- [benklop/libferret](https://github.com/benklop/libferret) — SDK fork submodule, CLI tools, `ferret` Python package
- [benklop/OrbbecSDK_v2](https://github.com/benklop/OrbbecSDK_v2) — Ferret device support (not intended for upstream Orbbec merge)

## License

GPLv2 (inherited from Horus / Gryphon Scan).
