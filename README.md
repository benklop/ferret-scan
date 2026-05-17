# ferret-scan

Structured-light scanning workbench for the **Creality CR-Scan Ferret**, forked from [gryphon-scan](https://github.com/nightgryphon/gryphon-scan) (Horus lineage).

| Mode | Hardware | Capture |
|------|----------|---------|
| **Ferret structured light** (default) | Orbbec Ferret RGB-D + optional GRBL turntable | Depth + color per turntable step |
| **Ciclop laser** (legacy) | Webcam + line lasers + Ciclop board | Laser triangulation (original Gryphon path) |

## Quick start

### 1. Clone with libferret submodule

```bash
git clone --recursive https://github.com/benklop/ferret-scan.git
cd ferret-scan
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

### 2. Build OrbbecSDK (inside submodule)

```bash
cd libferret/OrbbecSDK_v2
cmake -B build && cmake --build build -j$(nproc)
cd ../..
```

### 3. GUI + Python dependencies

With [asdf](https://asdf-vm.com/), from the repo root:

```bash
asdf install    # reads .tool-versions (Python 3.13.7)
pip install -r requirements.txt
```

Or use any Python ≥3.9; **3.13** is recommended for pyorbbecsdk compatibility.

Install **wxPython** before matplotlib if the wx backend is missing.

### 4. Ferret camera stack (pyorbbecsdk)

```bash
chmod +x scripts/setup_ferret_hw.sh scripts/check_ferret.py
./scripts/setup_ferret_hw.sh    # uses ./libferret by default
source scripts/ferret_env.sh
python3 scripts/check_ferret.py --snap
```

### 5. Run the app

```bash
./ferret
```

Settings are stored under `~/.ferret/`. In **Preferences**:

| Setting | Typical value |
|---------|----------------|
| Scanner mode | `Ferret structured light` |
| libferret path | `./libferret` (auto-detected in source checkouts) |
| Python 3 for Ferret | `python3` |
| Turntable optional | `true` if you rotate manually |

Connect → Control (turntable) → Calibration → Scanning.

## Architecture

```
Python 3 (Ferret Scan wx GUI)
  └─ camera_ferret → subprocess → scripts/ferret_snap_rgbd.py
                                    └─ libferret/ (submodule) / pyorbbecsdk
  └─ ciclop_scan → depth_to_point_cloud (Ferret mode)
  └─ board.py (GRBL turntable, optional)
```

## Linux udev (USB permissions)

```bash
cd ~/repos/pyorbbecsdk/scripts/env_setup   # or your pyorbbecsdk clone
sudo ./install_udev_rules.sh
sudo udevadm control --reload && sudo udevadm trigger
```

## Related repos

- [libferret](https://github.com/benklop/libferret) — vendored at `libferret/`; includes OrbbecSDK_v2 fork and Python package
- [OrbbecSDK_v2](https://github.com/benklop/OrbbecSDK_v2) — Ferret device support (submodule of libferret)

## License

GPLv2 (inherited from Horus / Gryphon Scan).
