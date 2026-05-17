#!/usr/bin/env bash
# Build pyorbbecsdk against libferret's OrbbecSDK fork and install Python packages.
#
# Usage:
#   ./scripts/setup_ferret_hw.sh [/path/to/libferret] [/path/to/pyorbbecsdk]
#
# Prerequisites:
#   libferret OrbbecSDK built: cd libferret/OrbbecSDK_v2 && cmake -B build && cmake --build build -j

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_LIBFERRET="${ROOT}/libferret"
if [[ ! -f "${DEFAULT_LIBFERRET}/pyproject.toml" ]]; then
  DEFAULT_LIBFERRET="${HOME}/repos/ferret"
fi
FERRET_ROOT="${1:-${FERRET_LIBFERRET_ROOT:-${DEFAULT_LIBFERRET}}}"
PYOB_ROOT="${2:-${PYORBBECSDK_ROOT:-$HOME/repos/pyorbbecsdk}}"

SDK_SRC="${FERRET_ROOT}/OrbbecSDK_v2/build/linux_x86_64/lib"
SDK_DST="${PYOB_ROOT}/sdk/lib/linux_x64"

if [[ ! -f "${SDK_SRC}/libOrbbecSDK.so" ]]; then
  echo "Missing ${SDK_SRC}/libOrbbecSDK.so — build libferret OrbbecSDK first." >&2
  exit 1
fi

if [[ ! -d "${PYOB_ROOT}" ]]; then
  echo "Cloning pyorbbecsdk v2-main into ${PYOB_ROOT}..." >&2
  git clone --depth 1 --branch v2-main https://github.com/orbbec/pyorbbecsdk.git "${PYOB_ROOT}"
fi

echo "Syncing Ferret-enabled OrbbecSDK into pyorbbecsdk..."
rm -rf "${SDK_DST}"
mkdir -p "${SDK_DST}"
cp -a "${SDK_SRC}/"* "${SDK_DST}/"

PYBIND_DIR="$(python3 -m pybind11 --cmakedir)"
cd "${PYOB_ROOT}"
cmake -B build -DCMAKE_BUILD_TYPE=Release -Dpybind11_DIR="${PYBIND_DIR}"
cmake --build build -j"$(nproc)"
cmake --install build

pip install -e "${PYOB_ROOT}"
pip install -e "${FERRET_ROOT}"

echo ""
echo "Done. Verify with:"
echo "  source ${ROOT}/scripts/ferret_env.sh ${FERRET_ROOT}"
echo "  python3 ${ROOT}/scripts/check_ferret.py"
