"""Read-only scientific gate for target-dependent rewards.

Supports both the original validated-target manifest contract and the newer
hash-locked approval manifest. The gate remains closed by default.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_validated_target_manifest(manifest_path: str | Path | None) -> dict[str, Any] | None:
    """Load a target manifest safely.

    Returns None for missing, unreadable, malformed, or non-object JSON.
    """
    if manifest_path is None:
        return None
    path = Path(manifest_path)
    if not path.exists() or not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _reviewer_ids(data: dict[str, Any]) -> list[str]:
    reviewers = data.get("reviewers", [])
    ids: list[str] = []
    if not isinstance(reviewers, list):
        return ids
    for r in reviewers:
        if isinstance(r, str):
            rid = r.strip()
        elif isinstance(r, dict):
            rid = str(r.get("reviewer_id", "")).strip()
        else:
            rid = ""
        if rid:
            ids.append(rid)
    return ids


def geometric_rewards_enabled(manifest_path: str | Path | None) -> bool:
    """Return True only for a valid, independently reviewed target manifest.

    Compatible with:
    1) the original contract:
       status, target_file, sha256, reviewers, review_count
    2) the newer approval contract:
       status, mesh_file, mesh_sha256, reviewers, accuracy_rewards_unlocked
    """
    data = load_validated_target_manifest(manifest_path)
    if data is None or data.get("status") != "validated_target":
        return False

    target_file = data.get("target_file") or data.get("mesh_file")
    mesh_hash = data.get("sha256") or data.get("mesh_sha256")
    if not target_file or not mesh_hash:
        return False

    ids = _reviewer_ids(data)
    if len(ids) < 2 or len(ids) != len(set(ids)):
        return False

    review_count = data.get("review_count", len(ids))
    try:
        if int(review_count) < 2:
            return False
    except Exception:
        return False

    # New manifests explicitly carry this lock. Old manifests predate it, so
    # absence is accepted for backward compatibility.
    if "accuracy_rewards_unlocked" in data and data.get("accuracy_rewards_unlocked") is not True:
        return False

    return True


def target_accuracy_rewards_enabled(manifest_path: str | Path | None) -> bool:
    """Alias for the stricter geometric reward gate."""
    return geometric_rewards_enabled(manifest_path)
