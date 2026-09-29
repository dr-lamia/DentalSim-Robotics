#!/usr/bin/env python3
"""Compare teleop, BC, RL and hybrid policy rollout CSVs without ranking them.

Each CSV row is one rollout. This script reports the same metrics per method
and paired tooth-level summaries when common tooth IDs exist.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


NUMERIC = [
    "mean_surface_deviation_mm",
    "p95_surface_deviation_mm",
    "finish_line_mean_deviation_mm",
    "taper_error_deg",
    "adjacent_collision_count",
    "pulp_min_distance_mm",
    "episode_steps",
]


def load(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def summarize(rows):
    out = {"n_rollouts": len(rows)}
    if not rows:
        return out

    out["success_rate"] = float(np.mean([int(r["success"]) for r in rows]))
    out["protected_contact_rate"] = float(
        np.mean([int(r.get("adjacent_collision_count", 0)) > 0 for r in rows])
    )
    for col in NUMERIC:
        vals = [float(r[col]) for r in rows if r.get(col, "") not in ("", None)]
        if vals:
            out[col] = {
                "mean": float(np.mean(vals)),
                "median": float(np.median(vals)),
                "p95": float(np.percentile(vals, 95)),
            }
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("files", nargs="+", type=Path, help="CSV files named by method")
    p.add_argument("--out", type=Path)
    args = p.parse_args()

    report = {}
    tooth_methods = defaultdict(set)

    for path in args.files:
        method = path.stem
        rows = load(path)
        report[method] = summarize(rows)
        for r in rows:
            tooth_methods[r.get("tooth_id", "")].add(method)

    common_teeth = sorted(
        t for t, methods in tooth_methods.items()
        if t and len(methods) == len(args.files)
    )
    report["_design"] = {
        "common_tooth_ids_across_all_methods": common_teeth,
        "paired_analysis_possible": bool(common_teeth),
        "note": (
            "This report does not declare a winner. Inferential comparisons should "
            "use tooth-level paired or mixed-effects analysis when repeated rollouts exist."
        ),
    }

    text = json.dumps(report, indent=2)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
