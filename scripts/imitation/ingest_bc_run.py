#!/usr/bin/env python3
"""Archive a completed BC run with hashes and held-out metrics."""
from __future__ import annotations
import argparse, hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--split-manifest", type=Path, required=True)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--torchscript", type=Path, required=True)
    p.add_argument("--evaluation-report", type=Path, required=True)
    p.add_argument("--repo-commit", required=True)
    p.add_argument("--out-dir", type=Path, default=Path("results/bc_runs"))
    args = p.parse_args()

    split = json.loads(args.split_manifest.read_text(encoding="utf-8"))
    if split.get("split_unit") != "tooth_id" or split.get("frame_level_random_split") is not False:
        raise SystemExit("Invalid split: tooth-level split is mandatory")
    if split.get("leakage_check_pass") is not True:
        raise SystemExit("Invalid split: tooth leakage detected")

    evaluation = json.loads(args.evaluation_report.read_text(encoding="utf-8"))
    run_id = datetime.now(timezone.utc).strftime("bc_%Y%m%dT%H%M%SZ")
    dest = args.out_dir / run_id
    dest.mkdir(parents=True, exist_ok=False)

    copied = {}
    for key, src in {
        "split_manifest": args.split_manifest,
        "config": args.config,
        "checkpoint": args.checkpoint,
        "torchscript": args.torchscript,
        "evaluation_report": args.evaluation_report,
    }.items():
        dst = dest / src.name
        shutil.copy2(src, dst)
        copied[key] = {"file": dst.name, "sha256": sha256_file(dst)}

    manifest = {
        "schema_version": 1,
        "run_type": "behavior_cloning_training",
        "run_id": run_id,
        "run_date_utc": datetime.now(timezone.utc).isoformat(),
        "repo_commit": args.repo_commit,
        "split_unit": "tooth_id",
        "train_tooth_ids": split.get("train_tooth_ids", []),
        "test_tooth_ids": split.get("test_tooth_ids", []),
        "artifacts": copied,
        "evaluation": evaluation,
        "scientific_note": "Action imitation error is not preparation accuracy."
    }
    (dest / "bc_run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
