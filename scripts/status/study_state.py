#!/usr/bin/env python3
"""Print the current DentalSim-Robotics study execution state."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.study_state import evaluate_study_state


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--forced-contact-result", type=Path)
    p.add_argument("--validated-target-manifest", type=Path)
    p.add_argument("--teleop-session-manifest", type=Path)
    p.add_argument("--bc-run-manifest", type=Path)
    p.add_argument("--json-out", type=Path)
    args = p.parse_args()

    state = evaluate_study_state(
        forced_contact_result=args.forced_contact_result,
        validated_target_manifest=args.validated_target_manifest,
        teleop_session_manifest=args.teleop_session_manifest,
        bc_run_manifest=args.bc_run_manifest,
    )
    payload = state.to_dict()
    text = json.dumps(payload, indent=2)
    print(text)

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
