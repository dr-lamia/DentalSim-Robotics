#!/usr/bin/env python3
"""Create a small valid mock teleoperation HDF5 dataset for smoke testing."""
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.teleop_hdf5 import EpisodeMeta, write_episode

out = ROOT / "results" / "mock_teleop.hdf5"
n = 20
t = np.linspace(0, 0.19, n)
obs = {
    "bur_pose": np.c_[np.zeros((n, 3)), np.zeros((n, 3)), np.ones(n)],
    "bur_twist": np.zeros((n, 6)),
    "target_relative_pose": np.c_[np.zeros((n, 3)), np.zeros((n, 3)), np.ones(n)],
    "adjacent_min_distance_mm": np.full(n, 1.0),
    "protected_contact": np.zeros(n),
    "previous_action": np.zeros((n, 6)),
}
act = {"delta_pose": np.zeros((n, 6))}
write_episode(out, EpisodeMeta("mock_ep_001", "15", "mock_operator", success=True), t, obs, act)
print(out)
