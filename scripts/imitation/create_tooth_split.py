#!/usr/bin/env python3
"""Create a tooth-level BC split manifest from validated session manifests."""
from __future__ import annotations
import argparse, json
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--session-manifests", nargs="+", type=Path, required=True)
    p.add_argument("--test-tooth", action="append", default=[])
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    sessions = []
    tooth_ids = set()
    for path in args.session_manifests:
        d = json.loads(path.read_text(encoding="utf-8"))
        if d.get("session_type") != "dentist_teleoperation" or d.get("human_expert_demonstration") is not True:
            raise SystemExit(f"Non-expert session forbidden: {path}")
        tooth = str(d["tooth_id"])
        tooth_ids.add(tooth)
        sessions.append({
            "manifest": str(path),
            "session_id": d["session_id"],
            "tooth_id": tooth,
            "hdf5": d["hdf5_file"],
            "hdf5_sha256": d["hdf5_sha256"],
        })

    test_teeth = set(map(str, args.test_tooth))
    if not test_teeth.issubset(tooth_ids):
        missing = sorted(test_teeth - tooth_ids)
        raise SystemExit(f"Requested test teeth absent: {missing}")

    train = [s for s in sessions if s["tooth_id"] not in test_teeth]
    test = [s for s in sessions if s["tooth_id"] in test_teeth]

    if test_teeth and (not train or not test):
        raise SystemExit("Tooth-level split requires non-empty train and test sets")

    out = {
        "schema_version": 1,
        "split_unit": "tooth_id",
        "frame_level_random_split": False,
        "train_tooth_ids": sorted({s["tooth_id"] for s in train}),
        "test_tooth_ids": sorted({s["tooth_id"] for s in test}),
        "train_sessions": train,
        "test_sessions": test,
        "leakage_check_pass": not (
            set(s["tooth_id"] for s in train) & set(s["tooth_id"] for s in test)
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
