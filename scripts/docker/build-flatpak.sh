#!/usr/bin/env bash
# Run inside the packaging container. Writes bundle to $1 (default /artifacts).
set -eo pipefail
OUT="${1:-/artifacts}"
ARCH="${FERRET_PACKAGE_ARCH:-amd64}"
case "${ARCH}" in
  amd64) FP_ARCH=x86_64 ;;
  arm64) FP_ARCH=aarch64 ;;
  *) FP_ARCH="${ARCH}" ;;
esac

mkdir -p "${OUT}/repo"
flatpak-builder \
  --force-clean \
  --repo="${OUT}/repo" \
  --arch="${FP_ARCH}" \
  "${OUT}/build-dir" \
  /src/flatpak/org.ferret.FerretScan.yml

flatpak build-bundle \
  "${OUT}/repo" \
  "${OUT}/ferret-scan-${ARCH}.flatpak" \
  org.ferret.FerretScan
