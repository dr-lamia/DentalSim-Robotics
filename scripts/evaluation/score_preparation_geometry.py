#!/usr/bin/env python3
"""Score a final preparation against a validated target mesh."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.geometry_metrics import load_mesh, evaluate_surface_deviation
from dentalsim.target_gate import target_accuracy_rewards_enabled


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--final", type=Path, required=True)
    p.add_argument("--target", type=Path, required=True)
    p.add_argument("--target-manifest", type=Path, required=True)
    p.add_argument("--sample-count", type=int, default=50000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    if not target_accuracy_rewards_enabled(args.target_manifest):
        print(json.dumps({
            "status": "BLOCKED",
            "reason": "target_accuracy_rewards_not_enabled"
        }, indent=2))
        raise SystemExit(3)

    final_mesh = load_mesh(args.final)
    target_mesh = load_mesh(args.target)
    metrics = evaluate_surface_deviation(
        final_mesh, target_mesh,
        sample_count=args.sample_count,
        seed=args.seed,
    )

    result = {
        "schema_version": 1,
        "metric_family": "bidirectional_surface_deviation",
        "units": "mm",
        "final_mesh": args.final.name,
        "target_mesh": args.target.name,
        "target_manifest": args.target_manifest.name,
        "sample_count": args.sample_count,
        "seed": args.seed,
        "metrics": metrics.to_dict(),
        "limitations": [
            "Unsigned distances do not distinguish over-reduction from under-reduction.",
            "These are sampled-surface nearest-neighbour metrics, not exact analytic mesh-to-mesh distances.",
            "Finish-line and taper metrics are separate endpoints."
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
