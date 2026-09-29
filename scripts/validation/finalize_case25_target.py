#!/usr/bin/env python3
"""One-command Case-25 approval/promotion readiness check."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mesh", type=Path, required=True)
    p.add_argument("--review-a", type=Path, required=True)
    p.add_argument("--review-b", type=Path, required=True)
    args = p.parse_args()

    manifest = ROOT / "configs" / "case25_target_candidate_v2_manifest.json"
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "validation" / "promote_validated_target.py"),
        "--candidate-manifest", str(manifest),
        "--mesh", str(args.mesh),
        "--reviews", str(args.review_a), str(args.review_b),
        "--output-dir", str(ROOT / "assets" / "validated_targets" / "case25"),
    ]

    proc = subprocess.run(cmd, text=True, capture_output=True)
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)

    if proc.returncode != 0:
        print(json.dumps({
            "status": "NOT_PROMOTED",
            "next_action": "Resolve the review or mesh-hash issues shown above and rerun."
        }, indent=2))
        raise SystemExit(proc.returncode)

    print(json.dumps({
        "status": "PROMOTED",
        "next_action": "Run scripts/status/check_readiness.py with the validated target manifest."
    }, indent=2))


if __name__ == "__main__":
    main()
