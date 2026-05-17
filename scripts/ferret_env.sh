#!/usr/bin/env bash
# Source before running Ferret snap/check tools:
#   source scripts/ferret_env.sh [/path/to/libferret]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEFAULT_LIBFERRET="${REPO_ROOT}/libferret"
if [[ ! -f "${DEFAULT_LIBFERRET}/pyproject.toml" ]]; then
  DEFAULT_LIBFERRET="${HOME}/repos/ferret"
fi
FERRET_LIBFERRET_ROOT="${1:-${FERRET_LIBFERRET_ROOT:-${DEFAULT_LIBFERRET}}}"
export FERRET_LIBFERRET_ROOT

SDK_LIB="${FERRET_LIBFERRET_ROOT}/OrbbecSDK_v2/build/linux_x86_64/lib"
if [[ -d "$SDK_LIB" ]]; then
  export LD_LIBRARY_PATH="${SDK_LIB}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi
