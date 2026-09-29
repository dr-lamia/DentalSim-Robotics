"""Gate millimetre-based metrics for unitless direct STL sources."""
from __future__ import annotations
import json
from pathlib import Path


def physical_scale_available(path: str | Path | None, expected_mesh_sha256: str | None = None) -> bool:
    if path is None:
        return False
    p=Path(path)
    if not p.exists():
        return False
    try:
        d=json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return False
    if d.get("status")!="physical_scale_calibrated":
        return False
    try:
        if float(d.get("scale_mm_per_native_unit",0)) <= 0:
            return False
    except Exception:
        return False
    if expected_mesh_sha256 and d.get("mesh_sha256") != expected_mesh_sha256:
        return False
    return bool(d.get("mesh_sha256"))
