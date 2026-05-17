#!/usr/bin/env python3
"""Validate Ferret hardware stack for ferret-scan."""

from __future__ import print_function

import os
import subprocess
import sys
import tempfile


def ok(msg):
    print("OK  ", msg)


def fail(msg):
    print("FAIL", msg)
    return 1


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_libferret = os.path.join(root, "libferret")
    if not os.path.isfile(os.path.join(default_libferret, "pyproject.toml")):
        default_libferret = os.path.expanduser("~/repos/ferret")
    libferret = os.environ.get("FERRET_LIBFERRET_ROOT", default_libferret)
    errors = 0

    # libferret before ferret-scan imports (same package name).
    lib_path = os.path.join(os.path.dirname(__file__), "lib")
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)

    if not os.path.isdir(libferret):
        errors += fail("libferret not found: {0}".format(libferret))
    else:
        ok("libferret: {0}".format(libferret))

    try:
        from libferret_import import get_ferret_device_class
        get_ferret_device_class()
        ok("libferret Python package (device)")
    except ImportError as e:
        errors += fail("libferret device import: {0}".format(e))
        print("      Run: ./scripts/dev-setup", file=sys.stderr)
        return errors

    try:
        from ferret.util import runtime
        sdk_lib = runtime.sdk_lib_dir()
    except ImportError:
        import platform
        machine = platform.machine().lower()
        plat = "linux_x86_64" if machine in ("x86_64", "amd64") else "linux_arm64"
        sdk_lib = os.path.join(libferret, "OrbbecSDK_v2", "build", plat, "lib")
    sdk_so = os.path.join(sdk_lib, "libOrbbecSDK.so")
    if os.path.isfile(sdk_so):
        ok("OrbbecSDK: {0}".format(sdk_so))
    else:
        errors += fail("OrbbecSDK not built — run cmake in libferret/OrbbecSDK_v2")

    snap = os.path.join(root, "scripts", "ferret_snap_rgbd.py")
    if os.path.isfile(snap):
        ok("snap script: {0}".format(snap))
    else:
        errors += fail("missing {0}".format(snap))

    env = os.environ.copy()
    env["FERRET_LIBFERRET_ROOT"] = libferret
    if os.path.isdir(sdk_lib):
        env["LD_LIBRARY_PATH"] = sdk_lib + ":" + env.get("LD_LIBRARY_PATH", "")
    pyob_lib = os.path.join(root, ".deps", "pyorbbecsdk", "install", "lib")
    if os.path.isdir(pyob_lib):
        env["LD_LIBRARY_PATH"] = pyob_lib + ":" + env.get("LD_LIBRARY_PATH", "")

    if "--snap" in sys.argv:
        tmp = tempfile.mkdtemp(prefix="ferret_check_")
        print("Running snap test →", tmp)
        rc = subprocess.call(
            [sys.executable, snap, tmp],
            env=env,
        )
        if rc == 0 and os.path.isfile(os.path.join(tmp, "color.png")):
            ok("RGBD snap from device")
        else:
            errors += fail("snap test failed (exit {0})".format(rc))
    else:
        print("(pass --snap to grab one RGBD frame from the camera)")

    return errors


if __name__ == "__main__":
    sys.exit(main())
