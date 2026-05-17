# ferret-scan

Structured-light scanning workbench for the **Creality CR-Scan Ferret**, forked from [gryphon-scan](https://github.com/nightgryphon/gryphon-scan) (Horus lineage).

## Distribution

| Format | Build |
|--------|--------|
| **AppImage** | `./scripts/build appimage` |
| **Flatpak** | `./scripts/build flatpak` |
| **Both** | `./scripts/build all` |

Packaging runs in Docker (host CPU by default). Cross-arch builds:

```bash
./scripts/build all --arch amd64
./scripts/build all --arch arm64
```

Artifacts land in `dist/<arch>/`. CI builds both architectures on tag push (see `.github/workflows/packages.yml`).

## Local development

**Prerequisites:** [uv](https://docs.astral.sh/uv/getting-started/installation/), `cmake`, a C/C++ toolchain, git submodules, and **GTK/wxGTK development packages** (wxPython is always **built from source** into `.venv`, not installed from wheels).

```bash
git clone --recursive https://github.com/benklop/ferret-scan.git
cd ferret-scan
./scripts/dev-setup          # .venv, OrbbecSDK, pyorbbecsdk, libferret
.venv/bin/python -m pytest   # unit tests (or: nox -s test)
uv run ruff check            # lint (or: nox -s lint)
./ferret                     # GUI (binstub sets library paths)
./scripts/dev-check --snap   # optional camera test
```

Python **3.9–3.13** (aligned with [pyorbbecsdk v2-main](https://github.com/orbbec/pyorbbecsdk)); dev default **3.13** via [`.python-version`](.python-version). Dependencies are declared in [`pyproject.toml`](pyproject.toml) with a committed [`uv.lock`](uv.lock).

Development uses **asdf/Python from `.python-version`** and a project **`.venv` only** — nothing is installed into `/usr/local` or system `site-packages`.

**Linux native packages** (install once; `wx-config` must exist before `./scripts/dev-setup`):

```bash
# Fedora
sudo dnf install -y gcc-c++ make pkg-config gtk3-devel wxGTK-devel \
  libjpeg-turbo-devel libpng-devel libtiff-devel libSM-devel libXrender-devel \
  libXinerama-devel libXi-devel webkit2gtk4.1-devel SDL-devel \
  gstreamer1-devel gstreamer1-plugins-base-devel

# Debian / Ubuntu
sudo apt install -y build-essential pkg-config libgtk-3-dev libwxgtk3.2-dev \
  libjpeg-dev libpng-dev libtiff-dev libsm-dev libxrender-dev libxinerama-dev \
  libxi-dev libwebkit2gtk-4.1-dev libsdl2-dev \
  libgstreamer1.0-dev libgstreamer1.0-plugins-base-dev
```

If `uv sync` reinstalls a wxPython wheel, run `./scripts/ensure-wx`. Prefer `.venv/bin/python -m pytest` over `uv run pytest`.

On **Linux Wayland**, `./ferret` runs natively (no X11 shim) and sets `PYOPENGL_PLATFORM=egl` so PyOpenGL uses the same EGL context as wx’s `GLCanvas`. If the 3D view fails on an unusual setup, try the legacy stack: `FERRET_FORCE_X11=1 ./ferret`.

No `source` step: `./ferret` and `./scripts/dev-check` configure `LD_LIBRARY_PATH`, `PYTHONPATH`, and `FERRET_LIBFERRET_ROOT` automatically.

Settings: `$XDG_CONFIG_HOME/ferret-scan/` (default `~/.config/ferret-scan/`). Calibration data: `$XDG_DATA_HOME/ferret-scan/`. Defaults work for a source checkout (`libferret` submodule, `python3` from `.venv`).

### Contributing

- `uv sync --group dev` — refresh the venv after pulling dependency changes
- `nox -s test` / `nox -s lint` — same commands as CI
- Optional: `pre-commit install` (ruff + basic file hooks)

### USB permissions

```bash
cd .deps/pyorbbecsdk/scripts/env_setup
sudo ./install_udev_rules.sh
sudo udevadm control --reload && sudo udevadm trigger
```

## Layout

```
./ferret                 # GUI binstub
./scripts/dev-setup      # native dev environment
./scripts/dev-check      # license checks + hardware validation
./scripts/build          # Docker → AppImage / Flatpak
./libferret/             # submodule (OrbbecSDK + Python ferret package)
./.deps/pyorbbecsdk/     # created by dev-setup
pyproject.toml           # Python dependencies and tool config
```

## License

Ferret Scan application code is **GPLv2** (inherited from Horus / Gryphon Scan). See [LICENSE](LICENSE).

Third-party components (Orbbec SDK, extension libraries, Python dependencies) are documented in [doc/THIRD_PARTY_LICENSES.md](doc/THIRD_PARTY_LICENSES.md). Release builds (AppImage, Flatpak) include **unmodified** Orbbec extension `.so` files and their license text under `share/doc/ferret-scan/orbbec/`.
