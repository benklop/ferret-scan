# Ferret optional calibration board

The CR-Scan Ferret can use an optional high-precision calibration board (shared with the Otter series). Standard scanning works without it; depth accuracy relies on Orbbec firmware calibration in normal use.

## ferret-scan today

- **Capture-only workflow:** Guided poses and RGB-D frame saves under the user config directory (`ferret_calibration/`).
- **Board serial number:** Stored in preferences for future use; ferret-scan does not load factory board geometry from the SN.
- **Compute step:** Not implemented. Factory calibration from the board SN is expected to depend on reverse-engineering work in the **cr-scan-reverse** project (Creality `algo.obconfig` / cloud lookup). Until that is complete, do not expect CrealityScan-equivalent accuracy improvements from the wizard alone.

## User guide

See the [Creality Ferret calibration wiki](https://wiki.creality.com/en/3d-scanner/cr-scan-ferret-series/ferret-calibration) for physical setup (arrow up, temperature, pose guidance). ferret-scan provides text hints only; visual guide overlays are not implemented yet.
