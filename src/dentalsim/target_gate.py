"""Validated-target manifest gate for enabling geometric rewards."""
from __future__ import annotations

import json
from pathlib import Path


def load_validated_target_manifest(path: str | Path) -> dict:
    path = Path(path)
    obj = json.loads(path.read_text(encoding="utf-8"))
    required = ["status", "target_file", "sha256", "reviewers", "review_count"]
    missing = [k for k in required if k not in obj]
    if missing:
        raise ValueError(f"Missing manifest fields: {missing}")
    if obj["status"] != "validated_target":
        raise ValueError("Manifest status is not validated_target")
    if obj["review_count"] < 2 or len(set(obj["reviewers"])) < 2:
        raise ValueError("Validated target requires two independent reviewers")
    return obj


def geometric_rewards_enabled(manifest_path: str | Path | None) -> bool:
    if manifest_path is None:
        return False
    try:
        load_validated_target_manifest(manifest_path)
        return True
    except Exception:
        return False
