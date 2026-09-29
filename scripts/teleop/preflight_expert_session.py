#!/usr/bin/env python3
"""Preflight a dentist teleoperation session."""
from __future__ import annotations
import argparse, json
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--operator-id", required=True)
    p.add_argument("--operator-role", choices=["dentist", "prosthodontist"], required=True)
    p.add_argument("--scene-id", required=True)
    p.add_argument("--tooth-id", required=True)
    p.add_argument("--forced-contact-result", type=Path, required=True)
    args = p.parse_args()

    issues = []
    try:
        safety = json.loads(args.forced_contact_result.read_text(encoding="utf-8"))
    except Exception:
        safety = {}
        issues.append("invalid_or_missing_forced_contact_result")

    if safety.get("pass") is not True:
        issues.append("safety_negative_test_not_passed")
    if safety.get("contact_detected") is not True:
        issues.append("protected_contact_not_verified")
    if safety.get("safety_rollout_accepted") is not False:
        issues.append("unsafe_rollout_rejection_not_verified")

    report = {
        "ready": not issues,
        "operator_id": args.operator_id,
        "operator_role": args.operator_role,
        "scene_id": args.scene_id,
        "tooth_id": args.tooth_id,
        "issues": issues,
        "rule": "Expert teleoperation may start only after the forced-contact safety gate passes."
    }
    print(json.dumps(report, indent=2))
    if issues:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
