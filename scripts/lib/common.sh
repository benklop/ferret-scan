# Shared paths for ferret-scan (safe to source from binstubs; do not use set -u here).
# shellcheck shell=bash

ferret_repo_root() {
    if [[ -n "${FERRET_REPO_ROOT:-}" ]]; then
        echo "${FERRET_REPO_ROOT}"
        return
    fi
    local here
    here="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    FERRET_REPO_ROOT="${here}"
    export FERRET_REPO_ROOT
    echo "${here}"
}

# Normalized arch label: amd64 | arm64
ferret_native_arch() {
    case "$(uname -m)" in
        x86_64|amd64) echo amd64 ;;
        aarch64|arm64) echo arm64 ;;
        *) echo "$(uname -m)" ;;
    esac
}

# OrbbecSDK_v2 cmake output directory name
ferret_sdk_platform_dir() {
    case "$(uname -m)" in
        x86_64|amd64) echo linux_x86_64 ;;
        aarch64|arm64) echo linux_arm64 ;;
        *) echo "linux_$(uname -m)" ;;
    esac
}

# pyorbbecsdk bundled SDK subdirectory
ferret_pyorbbec_sdk_dirname() {
    case "$(uname -m)" in
        x86_64|amd64) echo linux_x64 ;;
        aarch64|arm64) echo arm64 ;;
        armv7l|armv6l) echo arm32 ;;
        *) echo linux_x64 ;;
    esac
}

ferret_libferret_root() {
    if [[ -n "${FERRET_LIBFERRET_ROOT:-}" ]] && [[ -f "${FERRET_LIBFERRET_ROOT}/pyproject.toml" ]]; then
        echo "${FERRET_LIBFERRET_ROOT}"
        return
    fi
    local root vendored
    root="$(ferret_repo_root)"
    vendored="${root}/libferret"
    if [[ -f "${vendored}/pyproject.toml" ]]; then
        echo "${vendored}"
        return
    fi
    echo "${HOME}/repos/ferret"
}

ferret_sdk_lib_dir() {
    local libferret
    libferret="$(ferret_libferret_root)"
    echo "${libferret}/OrbbecSDK_v2/build/$(ferret_sdk_platform_dir)/lib"
}

# OrbbecSDK_v2 tree (submodule) for license files shipped with packages.
ferret_orbbec_sdk_root() {
    echo "$(ferret_libferret_root)/OrbbecSDK_v2"
}

# Install Orbbec extension license texts into a package doc directory.
ferret_install_orbbec_licenses() {
    local dest="$1"
    local sdk
    sdk="$(ferret_orbbec_sdk_root)"
    mkdir -p "${dest}"
    if [[ -f "${sdk}/extensions/license.txt" ]]; then
        install -Dm644 "${sdk}/extensions/license.txt" "${dest}/orbbec-extensions-license.txt"
    fi
    if [[ -f "${sdk}/End User License Agreement.txt" ]]; then
        install -Dm644 "${sdk}/End User License Agreement.txt" "${dest}/orbbec-eula.txt"
    fi
    if [[ -f "${sdk}/LICENSE.txt" ]]; then
        install -Dm644 "${sdk}/LICENSE.txt" "${dest}/orbbec-sdk-mit-license.txt"
    fi
}

ferret_pyorbbec_root() {
    echo "${FERRET_PYORBBECSDK_ROOT:-$(ferret_repo_root)/.deps/pyorbbecsdk}"
}

ferret_python() {
    local root venv_py
    root="$(ferret_repo_root)"
    venv_py="${root}/.venv/bin/python"
    if [[ -x "${venv_py}" ]]; then
        echo "${venv_py}"
        return
    fi
    echo "${FERRET_PYTHON:-python3}"
}

# Library paths only (checks / snap subprocesses — avoid PYTHONPATH shadowing libferret).
ferret_export_libs() {
    local libferret sdk_lib pyorbbec_install
    libferret="$(ferret_libferret_root)"
    sdk_lib="$(ferret_sdk_lib_dir)"
    pyorbbec_install="$(ferret_pyorbbec_root)/install/lib"

    export FERRET_LIBFERRET_ROOT="${libferret}"
    if [[ -d "${sdk_lib}" ]]; then
        export LD_LIBRARY_PATH="${sdk_lib}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
    fi
    if [[ -d "${pyorbbec_install}" ]]; then
        export LD_LIBRARY_PATH="${pyorbbec_install}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
    fi
}

# Export runtime variables for the GUI and dev tools.
ferret_export_dev_runtime() {
    local root libferret sdk_lib pyorbbec_install
    root="$(ferret_repo_root)"
    libferret="$(ferret_libferret_root)"
    sdk_lib="$(ferret_sdk_lib_dir)"
    pyorbbec_install="$(ferret_pyorbbec_root)/install/lib"

    export FERRET_REPO_ROOT="${root}"
    export FERRET_LIBFERRET_ROOT="${libferret}"
    export FERRET_PYTHON="$(ferret_python)"
    export PYTHONPATH="${root}/src${PYTHONPATH:+:${PYTHONPATH}}"

    if [[ -d "${sdk_lib}" ]]; then
        export LD_LIBRARY_PATH="${sdk_lib}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
    fi
    if [[ -d "${pyorbbec_install}" ]]; then
        export LD_LIBRARY_PATH="${pyorbbec_install}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
    fi
}

ferret_docker_platform() {
    case "$1" in
        amd64|x86_64) echo linux/amd64 ;;
        arm64|aarch64) echo linux/arm64 ;;
        *) echo "linux/$1" ;;
    esac
}

ferret_appimage_arch_suffix() {
    case "$1" in
        amd64) echo x86_64 ;;
        arm64) echo aarch64 ;;
        *) echo "$1" ;;
    esac
}
