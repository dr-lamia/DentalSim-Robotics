"""Read-only scientific gates for target-dependent rewards.

Two manifest contracts are supported:
- geometric_rewards_enabled(): legacy validated-target contract requiring two
  distinct reviewers.
- target_accuracy_rewards_enabled(): newer promotion-manifest contract requiring
  an explicit accuracy unlock and locked mesh hash.

Both gates are closed by default.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_validated_target_manifest(manifest_path: str | Path | None) -> dict[str, Any] | None:
    """Load a target manifest safely."""
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
    """Legacy gate: require a validated target and two distinct reviewers."""
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

    return True


def target_accuracy_rewards_enabled(manifest_path: str | Path | None) -> bool:
    """New promotion-manifest gate.

    The promotion script is responsible for creating this manifest only after
    expert review succeeds. Runtime code therefore checks the immutable
    promotion signals: validated status, explicit unlock, and a locked mesh
    hash. It does not reinterpret the reviews at runtime.
    """
    data = load_validated_target_manifest(manifest_path)
    if data is None:
        return False
    return (
        data.get("status") == "validated_target"
        and data.get("accuracy_rewards_unlocked") is True
        and bool(data.get("mesh_sha256") or data.get("sha256"))
    )
