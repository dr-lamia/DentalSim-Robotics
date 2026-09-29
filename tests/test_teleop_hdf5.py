from pathlib import Path
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.teleop_hdf5 import EpisodeMeta, write_episode

sys.path.insert(0, str(ROOT / "scripts" / "teleop"))
from validate_teleop_hdf5 import validate


def _payload(n=5):
    obs = {
        "bur_pose": np.zeros((n, 7)),
        "bur_twist": np.zeros((n, 6)),
        "target_relative_pose": np.zeros((n, 7)),
        "adjacent_min_distance_mm": np.ones(n),
        "protected_contact": np.zeros(n),
        "previous_action": np.zeros((n, 6)),
    }
    act = {"delta_pose": np.zeros((n, 6))}
    return obs, act


def test_valid_dataset_passes(tmp_path):
    p = tmp_path / "demo.hdf5"
    obs, act = _payload()
    write_episode(p, EpisodeMeta("e1", "15", "op1", success=True), np.arange(5)*0.01, obs, act)
    r = validate(p)
    assert r["pass"]


def test_success_with_protected_contact_fails(tmp_path):
    p = tmp_path / "demo.hdf5"
    obs, act = _payload()
    obs["protected_contact"][2] = 1
    write_episode(p, EpisodeMeta("e1", "15", "op1", success=True), np.arange(5)*0.01, obs, act)
    r = validate(p)
    assert not r["pass"]
    assert any("success_with_protected_contact" in x for x in r["issues"])
