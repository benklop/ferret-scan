#!/usr/bin/env bash
# Run inside the packaging container. Writes artifacts to $1 (default /artifacts).
set -eo pipefail
OUT="${1:-/artifacts}"
ARCH="${FERRET_PACKAGE_ARCH:-amd64}"
ARCH_SUFFIX="$(ferret_appimage_arch_suffix "${ARCH}")"

# shellcheck source=/src/scripts/lib/common.sh
source /src/scripts/lib/common.sh

APPDIR="${OUT}/FerretScan.AppDir"
rm -rf "${APPDIR}"
mkdir -p "${APPDIR}/usr/bin" "${APPDIR}/usr/lib" "${APPDIR}/usr/share/ferret"

echo "==> AppImage: configure native build"
/src/scripts/dev-setup

LIBFERRET="$(ferret_libferret_root)"
SDK_LIB="$(ferret_sdk_lib_dir)"
PYOB_LIB="$(ferret_pyorbbec_root)/install/lib"
VENV="/src/.venv"

echo "==> AppImage: assemble AppDir"
cp -a /src/res "${APPDIR}/usr/share/ferret/"
cp -a /src/src "${APPDIR}/usr/share/ferret/"
cp /src/scripts/ferret_gui.py "${APPDIR}/usr/share/ferret/"
cp -a "${LIBFERRET}/python" "${APPDIR}/usr/libferret/python"
SDK_PLATFORM="$(ferret_sdk_platform_dir)"
mkdir -p "${APPDIR}/usr/libferret/OrbbecSDK_v2/build/${SDK_PLATFORM}"
cp -a "${SDK_LIB}" "${APPDIR}/usr/libferret/OrbbecSDK_v2/build/${SDK_PLATFORM}/lib"
# Do not bundle Creality algo assets; see doc/CREALITY_ALGO_ASSETS.md and license plan.
rm -rf "${APPDIR}/usr/libferret/OrbbecSDK_v2/build/${SDK_PLATFORM}/lib/ferret" 2>/dev/null || true

if [[ -d "${SDK_LIB}" ]]; then
  cp -a "${SDK_LIB}/"*.so* "${APPDIR}/usr/lib/" 2>/dev/null || true
  if [[ -d "${SDK_LIB}/extensions" ]]; then
    cp -a "${SDK_LIB}/extensions" "${APPDIR}/usr/lib/"
  fi
fi
if [[ -d "${PYOB_LIB}" ]]; then
  cp -a "${PYOB_LIB}/"*.so* "${APPDIR}/usr/lib/" 2>/dev/null || true
fi

mkdir -p "${APPDIR}/usr/share/doc/ferret-scan"
install -Dm644 /src/LICENSE "${APPDIR}/usr/share/doc/ferret-scan/gpl-2.0.txt"
install -Dm644 /src/doc/THIRD_PARTY_LICENSES.md "${APPDIR}/usr/share/doc/ferret-scan/THIRD_PARTY_LICENSES.md"
ferret_install_orbbec_licenses "${APPDIR}/usr/share/doc/ferret-scan/orbbec"
if [[ -d "${APPDIR}/usr/lib/extensions" ]]; then
  install -Dm644 "$(ferret_orbbec_sdk_root)/extensions/license.txt" \
    "${APPDIR}/usr/lib/extensions/license.txt" 2>/dev/null || true
fi

cp -a "${VENV}" "${APPDIR}/usr/venv"

cat > "${APPDIR}/AppRun" <<'EOF'
#!/usr/bin/env bash
HERE="$(cd "$(dirname "$0")" && pwd)"
export FERRET_LIBFERRET_ROOT="${HERE}/usr/libferret"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH:-}"
export PYTHONPATH="${HERE}/usr/share/ferret/src:${HERE}/usr/libferret/python"
exec "${HERE}/usr/venv/bin/python" "${HERE}/usr/share/ferret/ferret_gui.py" "$@"
EOF
chmod +x "${APPDIR}/AppRun"

if [[ -x /usr/local/bin/appimagetool ]]; then
  /usr/local/bin/appimagetool "${APPDIR}" "${OUT}/FerretScan-${ARCH_SUFFIX}.AppImage"
  chmod +x "${OUT}/FerretScan-${ARCH_SUFFIX}.AppImage"
else
  echo "appimagetool missing; leaving AppDir at ${APPDIR}" >&2
fi
