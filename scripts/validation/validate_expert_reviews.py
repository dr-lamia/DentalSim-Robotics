#!/usr/bin/env python3
"""Validate expert review JSON files for a locked target candidate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.target_validation import load_review, validate_review


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--candidate-manifest", type=Path, required=True)
    p.add_argument("--reviews", nargs="+", type=Path, required=True)
    p.add_argument("--json-out", type=Path)
    args = p.parse_args()

    manifest = json.loads(args.candidate_manifest.read_text(encoding="utf-8"))
    expected_sha = str(manifest["sha256"]).lower()

    reports = []
    reviewer_ids = []
    all_issues = []

    for path in args.reviews:
        review = load_review(path)
        reviewer_ids.append(review.reviewer_id)
        issues = validate_review(review)

        if review.case_id != manifest["case_id"]:
            issues.append("case_id_mismatch")
        if review.fdi != int(manifest["fdi"]):
            issues.append("fdi_mismatch")
        if review.candidate_version != int(manifest["candidate_version"]):
            issues.append("candidate_version_mismatch")
        if review.mesh_sha256 != expected_sha:
            issues.append("mesh_sha256_mismatch")

        failed_criteria = [
            k for k, v in review.criteria.items() if v != "pass"
        ]

        reports.append({
            "file": str(path),
            "reviewer_id": review.reviewer_id,
            "reviewer_role": review.reviewer_role,
            "review_date": review.review_date,
            "overall_decision": review.overall_decision,
            "failed_criteria": failed_criteria,
            "issues": issues,
        })
        all_issues.extend([f"{review.reviewer_id}:{x}" for x in issues])

    if len(reviewer_ids) != len(set(reviewer_ids)):
        all_issues.append("duplicate_reviewer_ids")

    decisions = {r["overall_decision"] for r in reports}
    disagreement = len(decisions) > 1

    result = {
        "case_id": manifest["case_id"],
        "fdi": manifest["fdi"],
        "candidate_version": manifest["candidate_version"],
        "mesh_sha256": expected_sha,
        "review_count": len(reports),
        "distinct_reviewer_count": len(set(reviewer_ids)),
        "reviews": reports,
        "decision_disagreement": disagreement,
        "all_reviews_accept": all(
            r["overall_decision"] == "accept" and not r["failed_criteria"] and not r["issues"]
            for r in reports
        ),
        "eligible_for_promotion_check": (
            len(reports) >= 2
            and len(set(reviewer_ids)) >= 2
            and not all_issues
            and all(r["overall_decision"] == "accept" for r in reports)
            and all(not r["failed_criteria"] for r in reports)
        ),
        "issues": all_issues,
    }

    text = json.dumps(result, indent=2)
    print(text)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")

    if not result["eligible_for_promotion_check"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
