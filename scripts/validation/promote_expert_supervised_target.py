#!/usr/bin/env python3
"""Promote an expert-supervised source case after technical geometry QA."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil


CRITERIA = (
    "correct_tooth_identity",
    "complete_prepared_surface",
    "axial_surfaces_complete",
    "occlusal_surface_complete",
    "no_adjacent_tooth_contamination",
    "no_unacceptable_gingival_contamination",
    "scale_verified",
    "orientation_verified",
    "suitable_as_reference_geometry",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--candidate-manifest", type=Path, required=True)
    p.add_argument("--mesh", type=Path, required=True)
    p.add_argument("--qa", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()

    candidate = json.loads(args.candidate_manifest.read_text(encoding="utf-8"))
    qa = json.loads(args.qa.read_text(encoding="utf-8"))
    issues = []

    actual_sha = sha256_file(args.mesh)
    expected_sha = str(candidate["sha256"]).lower()

    if candidate.get("source_expert_supervised") is not True:
        issues.append("candidate_source_not_marked_expert_supervised")
    if actual_sha != expected_sha:
        issues.append("candidate_mesh_hash_mismatch")
    if qa.get("mesh_sha256", "").lower() != expected_sha:
        issues.append("qa_mesh_hash_mismatch")
    if qa.get("case_id") != candidate.get("case_id"):
        issues.append("qa_case_id_mismatch")
    if int(qa.get("fdi", -1)) != int(candidate.get("fdi")):
        issues.append("qa_fdi_mismatch")
    if int(qa.get("candidate_version", -1)) != int(candidate.get("candidate_version")):
        issues.append("qa_candidate_version_mismatch")
    if qa.get("source_expert_supervised") is not True:
        issues.append("qa_did_not_confirm_expert_supervision")
    if qa.get("overall_decision") != "accept":
        issues.append("qa_decision_not_accept")

    criteria = qa.get("criteria", {})
    for key in CRITERIA:
        if criteria.get(key) != "pass":
            issues.append(f"criterion_failed_or_missing:{key}")

    report = {
        "promotable": not issues,
        "issues": issues,
        "case_id": candidate.get("case_id"),
        "fdi": candidate.get("fdi"),
        "candidate_version": candidate.get("candidate_version"),
        "mesh_sha256": expected_sha,
        "source_expert_supervised": candidate.get("source_expert_supervised") is True,
    }
    print(json.dumps(report, indent=2))
    if issues:
        raise SystemExit(3)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    target_name = f"fdi{candidate['fdi']}_validated_target_v{candidate['candidate_version']}.stl"
    target_path = args.output_dir / target_name
    shutil.copy2(args.mesh, target_path)

    validated = {
        "schema_version": 2,
        "status": "validated_target",
        "validation_route": "expert_supervised_source_plus_technical_geometry_qa",
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "case_id": candidate["case_id"],
        "fdi": candidate["fdi"],
        "candidate_version": candidate["candidate_version"],
        "mesh_file": target_name,
        "mesh_sha256": expected_sha,
        "source_expert_supervised": True,
        "technical_geometry_qa_pass": True,
        "technical_qa_operator_id": qa.get("operator_id"),
        "technical_qa_date": qa.get("review_date"),
        "accuracy_rewards_unlocked": True,
    }
    (args.output_dir / "validated_target_manifest.json").write_text(
        json.dumps(validated, indent=2), encoding="utf-8"
    )
    print(f"STATUS: VALIDATED TARGET -> {target_path}")


if __name__ == "__main__":
    main()
