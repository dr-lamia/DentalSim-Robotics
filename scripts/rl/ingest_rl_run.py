#!/usr/bin/env python3
"""Archive a completed PPO/hybrid run with reproducible provenance."""
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
    p.add_argument("--mode", required=True)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--evaluation-report", type=Path, required=True)
    p.add_argument("--repo-commit", required=True)
    p.add_argument("--forced-contact-result", type=Path, required=True)
    p.add_argument("--validated-target-manifest", type=Path)
    p.add_argument("--bc-run-manifest", type=Path)
    p.add_argument("--out-dir", type=Path, default=Path("results/rl_runs"))
    args = p.parse_args()

    run_id = datetime.now(timezone.utc).strftime("rl_%Y%m%dT%H%M%SZ")
    dest = args.out_dir / run_id
    dest.mkdir(parents=True, exist_ok=False)

    artifacts = {}
    for key, src in {
        "config": args.config,
        "checkpoint": args.checkpoint,
        "evaluation_report": args.evaluation_report,
        "forced_contact_result": args.forced_contact_result,
    }.items():
        dst = dest / src.name
        shutil.copy2(src, dst)
        artifacts[key] = {"file": dst.name, "sha256": sha256_file(dst)}

    if args.validated_target_manifest:
        dst = dest / args.validated_target_manifest.name
        shutil.copy2(args.validated_target_manifest, dst)
        artifacts["validated_target_manifest"] = {"file": dst.name, "sha256": sha256_file(dst)}

    if args.bc_run_manifest:
        dst = dest / args.bc_run_manifest.name
        shutil.copy2(args.bc_run_manifest, dst)
        artifacts["bc_run_manifest"] = {"file": dst.name, "sha256": sha256_file(dst)}

    evaluation = json.loads(args.evaluation_report.read_text(encoding="utf-8"))

    manifest = {
        "schema_version": 1,
        "run_type": "rl_training",
        "run_id": run_id,
        "run_date_utc": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "repo_commit": args.repo_commit,
        "artifacts": artifacts,
        "evaluation": evaluation,
        "scientific_note": (
            "Safety-only modes cannot support preparation-accuracy claims. "
            "Accuracy modes require a validated target manifest."
        ),
    }
    (dest / "rl_run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
