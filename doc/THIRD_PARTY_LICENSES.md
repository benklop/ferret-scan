# Third-party licenses

Ferret Scan combines open-source components and prebuilt Orbbec extension libraries. This document summarizes what each part is licensed under and what we do to comply.

**Source code for Ferret Scan:** [https://github.com/benklop/ferret-scan](https://github.com/benklop/ferret-scan) (GPLv2 application + MIT libferret submodule).

## Ferret Scan application

| Component | License | Notes |
|-----------|---------|--------|
| `src/ferret_scan/` (Horus / Gryphon Scan lineage) | [GPLv2](../LICENSE) | Copyright headers in source files |
| Packaging scripts, GUI entry | GPLv2 | Same as above |

When you receive a binary build (AppImage, Flatpak), you may obtain corresponding source from the repository above under GPLv2 terms.

## libferret

| Component | License | Location |
|-----------|---------|----------|
| Python package, C tools, integration | MIT | [libferret/pyproject.toml](../packages/libferret/pyproject.toml) |
| Ferret-specific SDK changes (`FerretDevice`, etc.) | MIT (Orbbec SDK fork) | [libferret/OrbbecSDK_v2](../packages/libferret/OrbbecSDK_v2) |

## Orbbec SDK (open-source parts)

| Component | License | Location |
|-----------|---------|----------|
| `libOrbbecSDK.so`, headers, examples | MIT | [libferret/OrbbecSDK_v2/LICENSE.txt](../packages/libferret/OrbbecSDK_v2/LICENSE.txt) |
| Bundled third-party libraries (jsoncpp, libjpeg, spdlog, etc.) | MIT, BSD, LGPL, etc. | Summarized in `LICENSE.txt` |

We modify only the **open-source** SDK sources (e.g. Ferret device support). We do **not** modify prebuilt extension binaries.

## librevolve (optional)

| Component | License | Location |
|-----------|---------|----------|
| Revopoint DAT BLE control | MIT | [librevolve](../packages/librevolve/) (git submodule) |

## Orbbec extension libraries (prebuilt)

Closed libraries loaded at runtime for depth/frame processing (e.g. `libob_frame_processor.so` under `extensions/`).

| Rule | Detail |
|------|--------|
| License text | [extensions/license.txt](../packages/libferret/OrbbecSDK_v2/extensions/license.txt) |
| Distribution | Shipped **unmodified** alongside Ferret Scan packages |
| Prohibited | Modifying, decompiling, or reverse engineering the extension binaries |
| Packaging | Copies of `extensions/license.txt` and `End User License Agreement.txt` are installed under `share/doc/ferret-scan/orbbec/` in AppImage and Flatpak builds |

Interoperability work (e.g. `extensionPid_` for Creality Ferret USB PID) is implemented in MIT-licensed SDK source only, not by patching extension `.so` files.

## Python dependencies (runtime)

Installed into the application virtual environment or bundle. Each package has its own license (typically permissive):

| Package | Typical license |
|---------|-----------------|
| wxPython | wxWindows Library License (LGPL-like, GPL-compatible) |
| NumPy, SciPy | BSD |
| OpenCV (`opencv-python`) | Apache 2.0 |
| Matplotlib | PSF / BSD-style |
| pyorbbecsdk | Apache 2.0 (upstream Orbbec bindings) |
| pybind11 | BSD |

See each package’s metadata on PyPI or in `.venv/lib/python*/site-packages/*.dist-info/` after `dev-setup`.

## Removed third-party code

The Pupil Labs macOS UVC extension (`engine/driver/uvc/mac/`, CC BY-NC-SA 3.0) was **removed** from this tree. DIY webcam capture uses OpenCV on all platforms via optional [`libciclops`](https://github.com/benklop/libciclops) (git submodule at `packages/libciclops/`).

## Creality algo assets (not distributed)

Ferret Scan does **not** ship or download Creality `algo.obconfig` / `algo_blobs`. See [CREALITY_ALGO_ASSETS.md](CREALITY_ALGO_ASSETS.md) for research notes only.

## Compliance summary

1. **GPLv2:** Application source is available; GPLv2 license file is included.
2. **Orbbec extensions:** Unmodified binaries + license texts in release artifacts.
3. **MIT SDK fork:** Source changes remain in the public libferret / OrbbecSDK_v2 fork.
4. **No Creality proprietary blobs** in git, CI artifacts, or default packages.
