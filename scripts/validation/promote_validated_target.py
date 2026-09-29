#!/usr/bin/env python3
"""Promote a reviewed candidate to validated target only after all gates pass."""
from __future__ import annotations
import argparse, json, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from dentalsim.target_validation import load_review, promotion_report

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--candidate-manifest", type=Path, required=True)
    p.add_argument("--mesh", type=Path, required=True)
    p.add_argument("--reviews", nargs="+", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()

    manifest = json.loads(args.candidate_manifest.read_text(encoding="utf-8"))
    reviews = [load_review(x) for x in args.reviews]
    report = promotion_report(candidate_manifest=manifest, mesh_path=args.mesh, reviews=reviews)
    print(json.dumps(report, indent=2))
    if not report["promotable"]:
        raise SystemExit(3)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    target_name = f"fdi{manifest['fdi']}_validated_target_v{manifest['candidate_version']}.stl"
    target_path = args.output_dir / target_name
    shutil.copy2(args.mesh, target_path)
    validated = {
        "schema_version": 1,
        "status": "validated_target",
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "case_id": manifest["case_id"],
        "fdi": manifest["fdi"],
        "candidate_version": manifest["candidate_version"],
        "mesh_file": target_name,
        "mesh_sha256": manifest["sha256"],
        "faces": manifest["faces"],
        "vertices": manifest["vertices"],
        "reviewers": [
            {"reviewer_id": r.reviewer_id, "reviewer_role": r.reviewer_role, "review_date": r.review_date}
            for r in reviews
        ],
        "accuracy_rewards_unlocked": True
    }
    (args.output_dir / "validated_target_manifest.json").write_text(json.dumps(validated, indent=2), encoding="utf-8")
    print(f"STATUS: VALIDATED TARGET LOCKED -> {target_path}")

if __name__ == "__main__":
    main()
