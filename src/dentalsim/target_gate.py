"""Scientific gates for target-dependent rewards.

Primary target-validation route:
- source clinical preparation was completed under expert supervision;
- the extracted mesh passes technical geometry QA;
- the exact mesh is hash-locked.

The older independent-review manifest remains supported as an optional
stronger audit route.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_validated_target_manifest(manifest_path: str | Path | None) -> dict[str, Any] | None:
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


def _technical_qa_route(data: dict[str, Any]) -> bool:
    return (
        data.get("status") == "validated_target"
        and data.get("source_expert_supervised") is True
        and data.get("technical_geometry_qa_pass") is True
        and bool(data.get("mesh_sha256") or data.get("sha256"))
        and bool(data.get("mesh_file") or data.get("target_file"))
    )


def _legacy_review_route(data: dict[str, Any]) -> bool:
    if data.get("status") != "validated_target":
        return False
    if not (data.get("target_file") or data.get("mesh_file")):
        return False
    if not (data.get("sha256") or data.get("mesh_sha256")):
        return False
    ids = _reviewer_ids(data)
    if len(ids) < 2 or len(ids) != len(set(ids)):
        return False
    try:
        review_count = int(data.get("review_count", len(ids)))
    except Exception:
        return False
    return review_count >= 2


def geometric_rewards_enabled(manifest_path: str | Path | None) -> bool:
    """Enable geometry rewards through either validated scientific route."""
    data = load_validated_target_manifest(manifest_path)
    if data is None:
        return False
    return _technical_qa_route(data) or _legacy_review_route(data)


def target_accuracy_rewards_enabled(manifest_path: str | Path | None) -> bool:
    """Runtime gate for preparation-accuracy rewards."""
    data = load_validated_target_manifest(manifest_path)
    if data is None or data.get("accuracy_rewards_unlocked") is not True:
        return False
    return _technical_qa_route(data) or _legacy_review_route(data)
