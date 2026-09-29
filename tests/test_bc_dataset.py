from pathlib import Path
import sys

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.bc_dataset import discover_episodes, load_samples, split_by_tooth


def _make(path, episodes):
    with h5py.File(path, "w") as f:
        f.attrs["dataset_version"] = "0.1"
        eps = f.create_group("episodes")
        for eid, tooth, contact in episodes:
            g = eps.create_group(eid)
            g.attrs["tooth_id"] = tooth
            g.attrs["operator_id"] = "op"
            g.attrs["mode"] = "teleop"
            g.attrs["success"] = not contact
            g.create_dataset("timestamps_s", data=np.arange(3))
            og = g.create_group("observations")
            og.create_dataset("bur_pose", data=np.zeros((3, 7)))
            og.create_dataset("bur_twist", data=np.zeros((3, 6)))
            og.create_dataset("target_relative_pose", data=np.zeros((3, 7)))
            og.create_dataset("adjacent_min_distance_mm", data=np.ones(3))
            og.create_dataset("protected_contact", data=np.array([0, int(contact), 0]))
            og.create_dataset("previous_action", data=np.zeros((3, 6)))
            ag = g.create_group("actions")
            ag.create_dataset("delta_pose", data=np.zeros((3, 6)))


def test_contact_episode_is_excluded(tmp_path):
    p = tmp_path / "d.h5"
    _make(p, [("safe", "15", False), ("bad", "16", True)])
    eps = discover_episodes([p])
    assert [e.episode_id for e in eps] == ["safe"]


def test_state_width_is_27(tmp_path):
    p = tmp_path / "d.h5"
    _make(p, [("safe", "15", False)])
    eps = discover_episodes([p])
    x, y = load_samples(eps)
    assert x.shape == (3, 27)
    assert y.shape == (3, 6)


def test_split_does_not_mix_teeth(tmp_path):
    p = tmp_path / "d.h5"
    _make(p, [("a", "11", False), ("b", "12", False), ("c", "13", False)])
    eps = discover_episodes([p])
    train, val = split_by_tooth(eps, 0.34, seed=1)
    assert set(e.tooth_id for e in train).isdisjoint(set(e.tooth_id for e in val))
