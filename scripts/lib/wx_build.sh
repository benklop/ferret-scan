# Build wxPython from source into the project venv (Linux).
# Requires wxGTK/GTK development packages from your distro — no binary wheels.
# shellcheck shell=bash

FERRET_WXPYTHON_VERSION='4.2.5'
FERRET_WXPYTHON_SDIST_URL="https://files.pythonhosted.org/packages/22/43/81657a6b126ffc19163500a8184d683cec08eb4e1d06905cd0c371c702d0/wxpython-${FERRET_WXPYTHON_VERSION}.tar.gz"

ferret_wx_config() {
    if command -v wx-config-3.2 >/dev/null 2>&1; then
        echo wx-config-3.2
    elif command -v wx-config >/dev/null 2>&1; then
        echo wx-config
    else
        return 1
    fi
}

ferret_wx_native_deps_ok() {
    ferret_wx_config >/dev/null
}

ferret_wx_print_native_deps() {
    cat <<'EOF'
wxPython is built from source into .venv (see [tool.uv] no-binary-package in pyproject.toml).
Install GTK/wxGTK development packages for your distro, then re-run dev-setup.

Debian / Ubuntu:
  sudo apt install -y build-essential pkg-config \
    libgtk-3-dev libwxgtk3.2-dev libjpeg-dev libpng-dev libtiff-dev \
    libsm-dev libxrender-dev libxinerama-dev libxi-dev \
    libwebkit2gtk-4.1-dev libsdl2-dev \
    libgstreamer1.0-dev libgstreamer1.0-plugins-base-dev

Fedora / RHEL:
  sudo dnf install -y gcc-c++ make pkg-config \
    gtk3-devel wxGTK-devel libjpeg-turbo-devel libpng-devel libtiff-devel \
    libSM-devel libXrender-devel libXinerama-devel libXi-devel \
    webkit2gtk4.1-devel SDL-devel gstreamer1-devel gstreamer1-plugins-base-devel
EOF
}

# Directory with libwx_*.so bundled by a Phoenix source build (platlib/wx).
ferret_wx_package_lib_dir() {
    local venv_py="$1"
    "${venv_py}" - <<'PY'
import glob
import os
import sysconfig

wx_dir = os.path.join(sysconfig.get_path("purelib"), "wx")
if glob.glob(os.path.join(wx_dir, "libwx_gtk3u_core*.so*")):
    print(wx_dir)
PY
}

# Phoenix gtk3 builds bundle libwx in site-packages/wx, but _core.so may not get $ORIGIN
# in RUNPATH; prepend this dir so the loader does not pick mismatched system libwx.
ferret_prepend_wx_runtime_ld_path() {
    local venv_py="$1"
    local wx_lib
    wx_lib="$(ferret_wx_package_lib_dir "${venv_py}" 2>/dev/null || true)"
    if [[ -n "${wx_lib}" && -d "${wx_lib}" ]]; then
        export LD_LIBRARY_PATH="${wx_lib}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
    fi
}

ferret_verify_wx_import() {
    local venv_py="$1"
    ferret_prepend_wx_runtime_ld_path "${venv_py}"
    "${venv_py}" -c "import wx; print('wxPython OK:', wx.version())"
}

# Build wxPython into venv_py from the PyPI sdist (uv --no-binary often still picks wheels).
ferret_build_wxpython() {
    local venv_py="$1"

    if [[ "$(uname -s)" != Linux ]]; then
        echo "wxPython source build is only automated on Linux; install wxPython for your platform." >&2
        return 1
    fi

    if ! ferret_wx_native_deps_ok; then
        echo "ERROR: wx-config not found — GTK/wxGTK development packages are required." >&2
        echo >&2
        ferret_wx_print_native_deps >&2
        return 1
    fi

    echo "==> Building wxPython ${FERRET_WXPYTHON_VERSION} from source into .venv ($(ferret_wx_config))..."
    echo "    First build may take ~10 minutes."

    uv pip install --python "${venv_py}" 'setuptools>=61,<70' wheel
    uv pip uninstall --python "${venv_py}" wxpython wxPython 2>/dev/null || true

    if ! uv pip install --python "${venv_py}" --no-deps "${FERRET_WXPYTHON_SDIST_URL}"; then
        echo "ERROR: wxPython source build failed." >&2
        ferret_wx_print_native_deps >&2
        return 1
    fi

    if ! ferret_verify_wx_import "${venv_py}"; then
        echo "ERROR: wxPython built but import failed." >&2
        return 1
    fi
}
