#!/usr/bin/env python3
"""Validate DentalSim-Robotics teleoperation HDF5 datasets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py
import numpy as np

MAX_TRANSLATION_M = 0.00025
MAX_ROTATION_RAD = np.deg2rad(2.0)

REQ_OBS = {
    "bur_pose": 7,
    "bur_twist": 6,
    "target_relative_pose": 7,
    "adjacent_min_distance_mm": None,
    "protected_contact": None,
    "previous_action": 6,
}
REQ_ACT = {"delta_pose": 6}


def validate(path: Path) -> dict:
    issues = []
    episode_reports = []

    with h5py.File(path, "r") as f:
        for attr in [
            "dataset_version",
            "project",
            "scene_id",
            "source_case_status",
            "clinical_ground_truth_status",
        ]:
            if attr not in f.attrs:
                issues.append(f"missing_file_attr:{attr}")

        if "episodes" not in f:
            issues.append("missing_group:episodes")
            return {"pass": False, "issues": issues, "episodes": []}

        for episode_id, g in f["episodes"].items():
            epi_issues = []
            if "timestamps_s" not in g:
                epi_issues.append("missing:timestamps_s")
                episode_reports.append({"episode_id": episode_id, "issues": epi_issues})
                continue

            ts = np.asarray(g["timestamps_s"])
            n = len(ts)
            if n == 0:
                epi_issues.append("empty_episode")
            if np.any(np.diff(ts) < 0):
                epi_issues.append("timestamps_not_monotonic")

            if "observations" not in g:
                epi_issues.append("missing_group:observations")
            else:
                og = g["observations"]
                for name, width in REQ_OBS.items():
                    if name not in og:
                        epi_issues.append(f"missing_observation:{name}")
                        continue
                    arr = np.asarray(og[name])
                    if len(arr) != n:
                        epi_issues.append(f"row_mismatch:{name}")
                    if width is not None and (arr.ndim != 2 or arr.shape[1] != width):
                        epi_issues.append(f"shape_mismatch:{name}")

            if "actions" not in g:
                epi_issues.append("missing_group:actions")
            else:
                ag = g["actions"]
                for name, width in REQ_ACT.items():
                    if name not in ag:
                        epi_issues.append(f"missing_action:{name}")
                        continue
                    arr = np.asarray(ag[name])
                    if arr.ndim != 2 or arr.shape[1] != width:
                        epi_issues.append(f"shape_mismatch:{name}")
                    elif len(arr) != n:
                        epi_issues.append(f"row_mismatch:{name}")
                    else:
                        if np.any(np.abs(arr[:, :3]) > MAX_TRANSLATION_M + 1e-12):
                            epi_issues.append("translation_action_limit_exceeded")
                        if np.any(np.abs(arr[:, 3:]) > MAX_ROTATION_RAD + 1e-12):
                            epi_issues.append("rotation_action_limit_exceeded")

            protected_contacts = 0
            if "observations" in g and "protected_contact" in g["observations"]:
                protected_contacts = int(np.count_nonzero(np.asarray(g["observations"]["protected_contact"])))

            success = bool(g.attrs.get("success", False))
            if success and protected_contacts > 0:
                epi_issues.append("success_with_protected_contact")

            episode_reports.append({
                "episode_id": episode_id,
                "timesteps": n,
                "success": success,
                "protected_contact_events": protected_contacts,
                "issues": epi_issues,
            })
            issues.extend([f"{episode_id}:{x}" for x in epi_issues])

    return {
        "pass": len(issues) == 0,
        "issues": issues,
        "episodes": episode_reports,
        "episode_count": len(episode_reports),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("hdf5_file", type=Path)
    p.add_argument("--json-out", type=Path)
    args = p.parse_args()
    report = validate(args.hdf5_file)
    print(json.dumps(report, indent=2))
    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
