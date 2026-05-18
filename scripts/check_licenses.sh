#!/usr/bin/env bash
# Verify license-compliance invariants (repo layout and optional dist/ artifacts).
set -eo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/common.sh
source "${ROOT}/scripts/lib/common.sh"

errors=0

fail() {
  echo "FAIL: $*" >&2
  errors=$((errors + 1))
}

ok() {
  echo "OK: $*"
}

# --- Creality fetch scripts must not exist ---
for f in \
  "${ROOT}/packages/libferret/scripts/fetch_creality_algo.sh" \
  "${ROOT}/packages/libferret/scripts/extract_algo_blobs.py" \
  "${ROOT}/packages/libferret/scripts/creality_scan_download.py"
do
  if [[ -f "${f}" ]]; then
    fail "removed script still present: ${f}"
  fi
done

# --- Documentation ---
if [[ ! -f "${ROOT}/doc/THIRD_PARTY_LICENSES.md" ]]; then
  fail "missing doc/THIRD_PARTY_LICENSES.md"
else
  ok "doc/THIRD_PARTY_LICENSES.md"
fi

if [[ ! -f "${ROOT}/LICENSE" ]]; then
  fail "missing LICENSE"
else
  ok "LICENSE"
fi

sdk="$(ferret_orbbec_sdk_root)"
if [[ ! -f "${sdk}/extensions/license.txt" ]]; then
  fail "missing Orbbec extensions/license.txt in submodule"
else
  ok "Orbbec extensions/license.txt"
fi

# --- Makefile must not reference algo-assets ---
if grep -q 'algo-assets\|fetch_creality' "${ROOT}/packages/libferret/Makefile" 2>/dev/null; then
  fail "packages/libferret/Makefile still references Creality algo fetch"
else
  ok "packages/libferret/Makefile has no algo-assets"
fi

# --- dist/ artifacts (if present) ---
if [[ -d "${ROOT}/dist" ]]; then
  while IFS= read -r -d '' bad; do
    fail "prohibited file in dist/: ${bad}"
  done < <(find "${ROOT}/dist" \( -name 'algo.obconfig' -o -path '*/algo_blobs/*' -o -path '*/lib/ferret/*' \) -print0 2>/dev/null || true)

  while IFS= read -r appdir; do
    doc="${appdir}/usr/share/doc/ferret-scan/orbbec/orbbec-extensions-license.txt"
    if [[ ! -f "${doc}" ]]; then
      fail "AppImage missing ${doc}"
    else
      ok "Orbbec license in $(basename "${appdir}")"
    fi
  done < <(find "${ROOT}/dist" -name '*.AppDir' -type d 2>/dev/null || true)
fi

if [[ "${errors}" -gt 0 ]]; then
  echo "${errors} license check(s) failed" >&2
  exit 1
fi

echo "All license checks passed."
