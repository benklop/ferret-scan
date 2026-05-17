# Creality algo assets (research notes)

**Status:** ferret-scan and libferret do **not** fetch, ship, or load Creality `algo.obconfig` / `algo_blobs`. Depth uses Orbbec SDK v2 with firmware calibration and unmodified extension libraries.

A speculative `FerretAlgoLoader` was removed: it called `FrameProcessor::setConfigData()`, which is a no-op in Orbbec SDK v2.

## What the assets are

Creality Scan ships a SQLite database `algo.obconfig` (`user_version` 241212) with a `files` table holding four binary payloads (`.bat` names are Creality convention, not shell scripts):

| Blob | Typical size | Header tag @ +4 |
|------|--------------|-------------------|
| `left_ir.bat` | ~544 KB | `0x08a00f00` |
| `right_ir.bat` | ~531 KB | `0x08a00f00` |
| `laser_left_ir.bat` | ~1.12 MB | `0x08282300` |
| `laser_right_ir.bat` | ~1.09 MB | `0x08282300` |

This is **not** Orbbec’s `DPAH` depth-post-filter format (`OB_RAW_DATA_DEPTH_POST_FILTER_PARAMS`).

## Reverse-engineering summary

**Creality Scan (Windows)** loads blobs via `lib_orbbec_scan.dll` and **`mx6600_depth_engine.dll`** (`load_input_configs_path`, `load_input_configs_content`, etc.). Blob filenames do not appear in `OrbbecSDK.dll`.

**Orbbec SDK v2 (Linux path)** does not consume these blobs via frame processors (`setConfigData()` is a no-op) or `libdepthengine.so` (Femto Bolt / K4A, not G2/Ferret). G2 calibration comes from **device firmware** via `G2AlgParamManager`.

Likely mapping: `left_ir` / `right_ir` for structured light; `laser_*` for line-laser modes; tied to depth work mode checksums (exact hash unconfirmed).

## If revisiting later

1. Prove a quality gap vs Creality Scan on real hardware (firmware-only baseline first).
2. Prefer Orbbec-native upload paths (`OB_RAW_DATA_DEPTH_ALG_MODE_LIST`, vendor raw) over shipping Creality binaries.
3. Any Windows DLL / winelib path needs a separate license review; do not bundle in default ferret-scan releases.

See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for what ferret-scan actually distributes today.
