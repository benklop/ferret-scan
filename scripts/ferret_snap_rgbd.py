#!/usr/bin/env python3
"""One-shot RGBD grab for ferret-scan (Python 2 UI → Python 3 Orbbec stack).

Usage: ferret_snap_rgbd.py <out_dir>
Writes: color.png, depth.png (uint16 mm), meta.json

Requires: libferret on PYTHONPATH and pyorbbecsdk built against Ferret OrbbecSDK fork.
"""
from __future__ import print_function

import json
import os
import sys

import numpy as np


def main():
    if len(sys.argv) < 2:
        print("usage: ferret_snap_rgbd.py <out_dir>", file=sys.stderr)
        return 2

    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)

    libferret_root = os.environ.get("FERRET_LIBFERRET_ROOT", "")
    if libferret_root:
        sys.path.insert(0, os.path.join(libferret_root, "python"))

    try:
        from ferret.device import FerretDevice
    except ImportError as e:
        print("ferret package not found: {0}".format(e), file=sys.stderr)
        print("Set FERRET_LIBFERRET_ROOT to your libferret clone.", file=sys.stderr)
        return 2

    try:
        import cv2
    except ImportError:
        print("opencv-python required", file=sys.stderr)
        return 2

    dev = FerretDevice.open(laser=True, laser_settle_s=2.0)
    config = dev.make_scan_config(color=True, depth=True, imu=False)
    dev.pipeline.start(config)
    dev.pipeline.enable_frame_sync()

    frames = None
    for _ in range(40):
        fs = dev.pipeline.wait_for_frames(200)
        if fs is None:
            continue
        depth = fs.get_depth_frame()
        color = fs.get_color_frame()
        if depth and color:
            frames = (depth, color)
            break

    dev.pipeline.stop()

    if frames is None:
        print("no synced depth+color frameset", file=sys.stderr)
        return 2

    depth_frame, color_frame = frames
    scale = depth_frame.get_depth_scale()
    w = depth_frame.get_width()
    h = depth_frame.get_height()
    depth = np.frombuffer(depth_frame.get_data(), dtype=np.uint16).reshape(h, w)
    color_data = np.frombuffer(color_frame.get_data(), dtype=np.uint8)
    ch = color_frame.get_height()
    cw = color_frame.get_width()
    color = color_data.reshape(ch, cw, 3)

    cv2.imwrite(os.path.join(out_dir, "color.png"), color)
    cv2.imwrite(os.path.join(out_dir, "depth.png"), depth)

    meta = {
        "depth_scale": float(scale),
        "depth_width": int(w),
        "depth_height": int(h),
        "color_width": int(cw),
        "color_height": int(ch),
    }
    with open(os.path.join(out_dir, "meta.json"), "w") as f:
        json.dump(meta, f)

    return 0


if __name__ == "__main__":
    sys.exit(main())
