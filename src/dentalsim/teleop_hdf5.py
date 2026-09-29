"""HDF5 trajectory writer for DentalSim-Robotics teleoperation.

This module is simulator-independent. It can be called from an Isaac teleop
loop or from test utilities.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

import h5py
import numpy as np


@dataclass
class EpisodeMeta:
    episode_id: str
    tooth_id: str
    operator_id: str
    mode: str = "teleop"
    success: bool = False
    termination_reason: str = ""


def _as_array(x, dtype=np.float32):
    arr = np.asarray(x, dtype=dtype)
    if arr.ndim == 0:
        arr = arr.reshape(1)
    return arr


def write_episode(
    path: str | Path,
    meta: EpisodeMeta,
    timestamps_s: Sequence[float],
    observations: Mapping[str, np.ndarray],
    actions: Mapping[str, np.ndarray],
    *,
    dataset_version: str = "0.1.0",
    scene_id: str = "case15_engineering_validation",
    source_case_status: str = "engineering_case",
    clinical_ground_truth_status: str = "not_validated",
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    ts = _as_array(timestamps_s, np.float64)
    n = len(ts)
    if n == 0:
        raise ValueError("Episode must contain at least one timestep")

    with h5py.File(path, "a") as f:
        f.attrs.setdefault("dataset_version", dataset_version)
        f.attrs.setdefault("created_utc", datetime.now(timezone.utc).isoformat())
        f.attrs.setdefault("project", "DentalSim-Robotics")
        f.attrs.setdefault("scene_id", scene_id)
        f.attrs.setdefault("source_case_status", source_case_status)
        f.attrs.setdefault("clinical_ground_truth_status", clinical_ground_truth_status)

        root = f.require_group("episodes")
        if meta.episode_id in root:
            raise ValueError(f"Episode already exists: {meta.episode_id}")
        g = root.create_group(meta.episode_id)
        g.attrs["tooth_id"] = meta.tooth_id
        g.attrs["operator_id"] = meta.operator_id
        g.attrs["mode"] = meta.mode
        g.attrs["success"] = bool(meta.success)
        g.attrs["termination_reason"] = meta.termination_reason

        g.create_dataset("timestamps_s", data=ts, compression="gzip")

        og = g.create_group("observations")
        for name, values in observations.items():
            arr = _as_array(values)
            if len(arr) != n:
                raise ValueError(f"Observation {name} has {len(arr)} rows, expected {n}")
            og.create_dataset(name, data=arr, compression="gzip")

        ag = g.create_group("actions")
        for name, values in actions.items():
            arr = _as_array(values)
            if len(arr) != n:
                raise ValueError(f"Action {name} has {len(arr)} rows, expected {n}")
            ag.create_dataset(name, data=arr, compression="gzip")
