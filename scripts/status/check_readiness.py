#!/usr/bin/env python3
"""Print DentalSim-Robotics readiness and blocked next actions."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.readiness import evaluate_readiness


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--validated-target-manifest", type=Path)
    p.add_argument("--forced-contact-result", type=Path)
    p.add_argument("--teleop-hdf5", type=Path)
    p.add_argument("--bc-policy", type=Path)
    p.add_argument("--json-out", type=Path)
    args = p.parse_args()

    r = evaluate_readiness(
        repo_root=ROOT,
        validated_target_manifest=args.validated_target_manifest,
        forced_contact_result=args.forced_contact_result,
        teleop_hdf5=args.teleop_hdf5,
        bc_policy=args.bc_policy,
    )
    d = r.to_dict()

    blocked = []
    if not r.forced_contact_verified:
        blocked.append("Run the Isaac forced-contact negative test on an Isaac-capable machine.")
    if not r.teleop_dataset_available:
        blocked.append("Record at least one real dentist teleoperation HDF5 episode.")
    if not r.validated_target_available:
        blocked.append("Complete two independent expert reviews and promote the Case-25 target.")
    if not r.bc_policy_available:
        blocked.append("Train/export the behavior-cloning policy after real teleoperation data exist.")

    result = {
        "readiness": d,
        "blocked_next_actions": blocked,
        "scientific_state": (
            "PREPARATION_ACCURACY_UNLOCKED"
            if r.manuscript_accuracy_outcomes_allowed
            else "ENGINEERING_ONLY"
        ),
    }

    text = json.dumps(result, indent=2)
    print(text)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
