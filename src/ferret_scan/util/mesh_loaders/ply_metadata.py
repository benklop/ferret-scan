"""PLY mesh metadata as JSON sidecar (.ply.meta.json)."""

from __future__ import annotations

import json
import os

META_SUFFIX = '.meta.json'


def sidecar_path(ply_path: str) -> str:
    return ply_path + META_SUFFIX


def load_metadata(ply_path: str):
    """Load metadata from JSON sidecar, or None if absent."""
    sc = sidecar_path(ply_path)
    if not os.path.isfile(sc):
        return None
    with open(sc, encoding='utf-8') as f:
        return json.load(f)


def save_metadata(ply_path: str, metadata) -> None:
    """Write metadata as JSON sidecar next to the PLY file."""
    if metadata is None:
        sc = sidecar_path(ply_path)
        if os.path.isfile(sc):
            os.remove(sc)
        return
    with open(sidecar_path(ply_path), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
