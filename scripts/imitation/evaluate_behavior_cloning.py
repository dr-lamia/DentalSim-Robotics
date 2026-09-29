#!/usr/bin/env python3
"""Evaluate an exported BC policy on held-out teleoperation episodes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.bc_dataset import discover_episodes, load_samples
from dentalsim.bc_runtime import BCRuntime


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--normalization", type=Path, required=True)
    p.add_argument("--hdf5", nargs="+", type=Path, required=True)
    p.add_argument("--out", type=Path)
    args = p.parse_args()

    episodes = discover_episodes(args.hdf5)
    if not episodes:
        raise SystemExit("No safe teleoperation episodes found")

    x, y = load_samples(episodes)
    rt = BCRuntime(args.model, args.normalization)
    pred = np.stack([rt.predict(row) for row in x])

    err = pred - y
    trans_err_mm = np.linalg.norm(err[:, :3], axis=1) * 1000.0
    rot_err_deg = np.linalg.norm(err[:, 3:], axis=1) * (180.0 / np.pi)

    translation_bound_violations = int(np.count_nonzero(np.abs(pred[:, :3]) > 0.00025 + 1e-12))
    rotation_bound_violations = int(np.count_nonzero(np.abs(pred[:, 3:]) > np.deg2rad(2.0) + 1e-12))

    report = {
        "episodes": len(episodes),
        "samples": int(len(x)),
        "translation_error_mm": {
            "mean": float(np.mean(trans_err_mm)),
            "median": float(np.median(trans_err_mm)),
            "p95": float(np.percentile(trans_err_mm, 95)),
        },
        "rotation_error_deg": {
            "mean": float(np.mean(rot_err_deg)),
            "median": float(np.median(rot_err_deg)),
            "p95": float(np.percentile(rot_err_deg, 95)),
        },
        "translation_bound_violations": translation_bound_violations,
        "rotation_bound_violations": rotation_bound_violations,
        "safety_bounds_pass": translation_bound_violations == 0 and rotation_bound_violations == 0,
        "scientific_note": (
            "Action imitation error is not equivalent to crown-preparation accuracy. "
            "Clinical/geometric task success requires validated target geometry and Isaac rollout evaluation."
        ),
    }
    print(json.dumps(report, indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if not report["safety_bounds_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
