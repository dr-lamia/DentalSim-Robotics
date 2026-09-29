"""Read-only scientific gate for target-dependent rewards."""
from __future__ import annotations
import json
from pathlib import Path

def target_accuracy_rewards_enabled(manifest_path: str | Path | None) -> bool:
    if manifest_path is None:
        return False
    path = Path(manifest_path)
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return (
        data.get("status") == "validated_target"
        and data.get("accuracy_rewards_unlocked") is True
        and bool(data.get("mesh_sha256"))
    )
