#!/usr/bin/env python3
"""Validate two expert target reviews before promoting a preparation mesh."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

REQUIRED = [
    "correct_tooth_identity",
    "complete_visible_boundary",
    "no_adjacent_tooth_contamination",
    "no_gingival_contamination",
    "complete_axial_surfaces",
    "complete_occlusal_surface",
    "suitable_for_geometric_scoring",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_review(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in ["reviewer_id", "decision", "criteria", "mesh_sha256"] if k not in obj]
    if missing:
        raise ValueError(f"{path}: missing fields {missing}")
    return obj


def review_passes(review: dict, expected_sha: str) -> tuple[bool, list[str]]:
    issues = []
    if review["decision"] != "accept":
        issues.append(f"decision={review['decision']}")
    if review["mesh_sha256"] != expected_sha:
        issues.append("mesh_checksum_mismatch")
    criteria = review.get("criteria", {})
    for key in REQUIRED:
        if criteria.get(key) is not True:
            issues.append(f"criterion_failed:{key}")
    return len(issues) == 0, issues


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--review", type=Path, action="append", required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()

    if len(args.review) != 2:
        raise SystemExit("Exactly two independent expert reviews are required")

    mesh_sha = sha256(args.candidate)
    reviews = [load_review(x) for x in args.review]

    reviewer_ids = [r["reviewer_id"] for r in reviews]
    if len(set(reviewer_ids)) != 2:
        raise SystemExit("Reviews must come from two different reviewer IDs")

    checks = []
    all_pass = True
    for path, review in zip(args.review, reviews):
        ok, issues = review_passes(review, mesh_sha)
        all_pass = all_pass and ok
        checks.append({
            "file": str(path),
            "reviewer_id": review["reviewer_id"],
            "pass": ok,
            "issues": issues,
        })

    report = {
        "candidate": str(args.candidate),
        "candidate_sha256": mesh_sha,
        "review_count": len(reviews),
        "review_checks": checks,
        "promotion_pass": all_pass,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "target_promotion_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    if not all_pass:
        print(json.dumps(report, indent=2))
        raise SystemExit(3)

    promoted = args.output_dir / "fdi25_validated_target.stl"
    shutil.copy2(args.candidate, promoted)
    manifest = {
        "status": "validated_target",
        "target_file": promoted.name,
        "sha256": mesh_sha,
        "reviewers": reviewer_ids,
        "review_count": 2,
    }
    (args.output_dir / "validated_target_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
