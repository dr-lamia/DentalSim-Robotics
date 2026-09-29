"""Load DentalSim teleoperation HDF5 into behavior-cloning samples."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import h5py
import numpy as np
import torch
from torch.utils.data import Dataset


FEATURES = [
    "bur_pose",
    "bur_twist",
    "target_relative_pose",
    "adjacent_min_distance_mm",
    "previous_action",
]


@dataclass(frozen=True)
class EpisodeIndex:
    file_path: Path
    episode_id: str
    tooth_id: str
    operator_id: str
    success: bool
    n: int


def _column(arr: np.ndarray) -> np.ndarray:
    arr = np.asarray(arr, dtype=np.float32)
    return arr[:, None] if arr.ndim == 1 else arr


def discover_episodes(paths: Iterable[str | Path], require_teleop: bool = True):
    out = []
    for path in map(Path, paths):
        with h5py.File(path, "r") as f:
            for eid, g in f["episodes"].items():
                if require_teleop and g.attrs.get("mode", "") != "teleop":
                    continue
                contacts = np.asarray(g["observations"]["protected_contact"])
                if np.any(contacts):
                    continue
                out.append(
                    EpisodeIndex(
                        file_path=path,
                        episode_id=eid,
                        tooth_id=str(g.attrs["tooth_id"]),
                        operator_id=str(g.attrs["operator_id"]),
                        success=bool(g.attrs.get("success", False)),
                        n=len(g["timestamps_s"]),
                    )
                )
    return out


def split_by_tooth(episodes, validation_fraction=0.15, seed=42):
    teeth = sorted({e.tooth_id for e in episodes})
    if len(teeth) < 2:
        # Smoke-test fallback only; real studies require independent teeth.
        return list(episodes), []
    rng = np.random.default_rng(seed)
    rng.shuffle(teeth)
    n_val = max(1, int(round(len(teeth) * validation_fraction)))
    val_teeth = set(teeth[:n_val])
    train = [e for e in episodes if e.tooth_id not in val_teeth]
    val = [e for e in episodes if e.tooth_id in val_teeth]
    return train, val


def load_samples(episodes):
    states, actions = [], []
    for e in episodes:
        with h5py.File(e.file_path, "r") as f:
            g = f["episodes"][e.episode_id]
            og = g["observations"]
            parts = [_column(np.asarray(og[name])) for name in FEATURES]
            s = np.concatenate(parts, axis=1).astype(np.float32)
            a = np.asarray(g["actions"]["delta_pose"], dtype=np.float32)
            if s.shape[1] != 27:
                raise ValueError(f"Expected 27 state features, got {s.shape[1]}")
            if a.shape[1] != 6:
                raise ValueError(f"Expected 6 action features, got {a.shape[1]}")
            states.append(s)
            actions.append(a)
    if not states:
        return np.empty((0, 27), np.float32), np.empty((0, 6), np.float32)
    return np.concatenate(states), np.concatenate(actions)


class BCDataset(Dataset):
    def __init__(self, states: np.ndarray, actions: np.ndarray):
        self.states = torch.as_tensor(states, dtype=torch.float32)
        self.actions = torch.as_tensor(actions, dtype=torch.float32)

    def __len__(self):
        return len(self.states)

    def __getitem__(self, idx):
        return self.states[idx], self.actions[idx]
