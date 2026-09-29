#!/usr/bin/env python3
"""Validate Case-25 visual QA, promote target, then print study state."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

VISUAL = (
    "correct_tooth_identity",
    "complete_prepared_surface",
    "axial_surfaces_complete",
    "occlusal_surface_complete",
    "no_adjacent_tooth_contamination",
    "no_unacceptable_gingival_contamination",
    "suitable_as_reference_geometry",
)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mesh", type=Path, required=True)
    p.add_argument("--qa", type=Path, required=True)
    p.add_argument("--forced-contact-result", type=Path)
    args = p.parse_args()

    qa = json.loads(args.qa.read_text(encoding="utf-8"))
    issues = []

    if qa.get("source_expert_supervised") is not True:
        issues.append("source_expert_supervised_not_confirmed")

    criteria = qa.get("criteria", {})
    for key in VISUAL:
        if criteria.get(key) != "pass":
            issues.append(f"visual_check_not_passed:{key}")

    if criteria.get("scale_verified") != "pass":
        issues.append("scale_check_not_passed")
    if criteria.get("orientation_verified") != "pass":
        issues.append("orientation_check_not_passed")
    if qa.get("overall_decision") != "accept":
        issues.append("overall_decision_not_accept")

    if issues:
        print(json.dumps({"status":"NOT_PROMOTED","issues":issues}, indent=2))
        raise SystemExit(2)

    out_dir = ROOT / "assets" / "validated_targets" / "case25"
    promote_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "validation" / "promote_expert_supervised_target.py"),
        "--candidate-manifest", str(ROOT / "configs" / "case25_target_candidate_v2_manifest.json"),
        "--mesh", str(args.mesh),
        "--qa", str(args.qa),
        "--output-dir", str(out_dir),
    ]
    proc = subprocess.run(promote_cmd, text=True, capture_output=True)
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)

    manifest = out_dir / "validated_target_manifest.json"

    state_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "status" / "study_state.py"),
        "--validated-target-manifest", str(manifest),
    ]
    if args.forced_contact_result:
        state_cmd += ["--forced-contact-result", str(args.forced_contact_result)]

    state = subprocess.run(state_cmd, text=True, capture_output=True)
    print(state.stdout)
    if state.stderr:
        print(state.stderr, file=sys.stderr)

    print(json.dumps({
        "status": "CASE25_TARGET_VALIDATED",
        "validated_target_manifest": str(manifest),
        "next_required_gate": (
            "none_for_accuracy_target"
            if args.forced_contact_result else
            "real_isaac_forced_contact_result"
        )
    }, indent=2))

if __name__ == "__main__":
    main()
