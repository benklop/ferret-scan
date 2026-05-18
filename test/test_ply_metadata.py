"""PLY metadata JSON sidecar."""

from __future__ import annotations

import os
import tempfile

from ferret_scan.util.mesh_loaders import ply_metadata


def test_sidecar_round_trip():
    with tempfile.TemporaryDirectory() as tmp:
        ply_path = os.path.join(tmp, 'mesh.ply')
        meta = {'scanner': 'ferret', 'frames': [1, 2, 3]}
        with open(ply_path, 'w') as f:
            f.write('placeholder')
        ply_metadata.save_metadata(ply_path, meta)
        loaded = ply_metadata.load_metadata(ply_path)
        assert loaded == meta


def test_missing_sidecar_returns_none():
    with tempfile.TemporaryDirectory() as tmp:
        ply_path = os.path.join(tmp, 'mesh.ply')
        with open(ply_path, 'w') as f:
            f.write('placeholder')
        assert ply_metadata.load_metadata(ply_path) is None
