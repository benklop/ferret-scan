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

```bash
git clone --recursive https://github.com/benklop/ferret-scan.git
cd ferret-scan
./scripts/dev-setup          # .venv, OrbbecSDK, pyorbbecsdk, libferret
./scripts/dev-check --snap   # optional camera test
./ferret                     # GUI (binstub sets library paths)
```

On **Fedora**, `dev-setup` uses `/usr/bin/python3` with system `python3-wxpython4` (pip’s wxPython wheel does not match the distro wxGTK). Install `sudo dnf install python3-wxpython4` if needed, then recreate the venv: `rm -rf .venv && ./scripts/dev-setup`.

No `source` step: `./ferret` and `./scripts/dev-check` configure `LD_LIBRARY_PATH`, `PYTHONPATH`, and `FERRET_LIBFERRET_ROOT` automatically.

Settings: `~/.ferret/`. Defaults work for a source checkout (`libferret` submodule, `python3` from `.venv`).

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
```

## License

Ferret Scan application code is **GPLv2** (inherited from Horus / Gryphon Scan). See [LICENSE](LICENSE).

Third-party components (Orbbec SDK, extension libraries, Python dependencies) are documented in [doc/THIRD_PARTY_LICENSES.md](doc/THIRD_PARTY_LICENSES.md). Release builds (AppImage, Flatpak) include **unmodified** Orbbec extension `.so` files and their license text under `share/doc/ferret-scan/orbbec/`.
