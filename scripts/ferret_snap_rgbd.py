#!/usr/bin/env python3
"""One-shot RGBD grab for ferret-scan (CLI / dev-check).

Usage: ferret_snap_rgbd.py <out_dir>
Writes: color.png, depth.png (uint16 mm), meta.json
"""

import json
import os
import sys

_REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(_REPO, 'src'))


def main():
    if len(sys.argv) < 2:
        print('usage: ferret_snap_rgbd.py <out_dir>', file=sys.stderr)
        return 2

    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)

    try:
        import cv2
    except ImportError:
        print('opencv-python required', file=sys.stderr)
        return 2

    from ferret_scan.services.ferret_rgbd import FerretRgbdService
    from ferret_scan.util import runtime

    svc = FerretRgbdService(runtime.libferret_root())
    try:
        svc.connect()
        color, depth, meta = svc.capture_rgbd()
    except Exception as e:
        print(f'Ferret snap failed: {e}', file=sys.stderr)
        return 2
    finally:
        svc.disconnect()

    cv2.imwrite(os.path.join(out_dir, 'color.png'), color)
    cv2.imwrite(os.path.join(out_dir, 'depth.png'), depth)
    with open(os.path.join(out_dir, 'meta.json'), 'w') as f:
        json.dump(meta, f, indent=2)
    return 0


if __name__ == '__main__':
    sys.exit(main())
