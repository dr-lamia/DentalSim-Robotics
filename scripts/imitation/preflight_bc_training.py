#!/usr/bin/env python3
"""Preflight a behavior-cloning run using expert teleoperation data only."""
from __future__ import annotations
import argparse, json
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--teleop-session-manifest", type=Path, required=True)
    p.add_argument("--min-episodes", type=int, default=3)
    args = p.parse_args()

    issues = []
    try:
        d = json.loads(args.teleop_session_manifest.read_text(encoding="utf-8"))
    except Exception:
        d = {}
        issues.append("invalid_or_missing_session_manifest")

    if d.get("session_type") != "dentist_teleoperation":
        issues.append("not_dentist_teleoperation")
    if d.get("human_expert_demonstration") is not True:
        issues.append("not_human_expert_demo")
    if d.get("input_mode") != "teleop":
        issues.append("input_mode_not_teleop")
    if d.get("validation_pass") is not True:
        issues.append("teleop_validation_not_passed")
    if int(d.get("episode_count") or 0) < args.min_episodes:
        issues.append("insufficient_episode_count")

    report = {
        "ready": not issues,
        "episode_count": d.get("episode_count"),
        "minimum_required": args.min_episodes,
        "operator_id": d.get("operator_id"),
        "tooth_id": d.get("tooth_id"),
        "issues": issues,
        "rule": "BC may train only on validated human expert teleoperation sessions."
    }
    print(json.dumps(report, indent=2))
    if issues:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
