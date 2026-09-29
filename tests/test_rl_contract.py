from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.rl_contract import RLStepState, compute_reward, termination_reason
from dentalsim.safety_policy import enforce_action


def test_case15_without_validated_target_ignores_surface_terms():
    a = RLStepState(mean_surface_error_mm=0.1, finish_line_error_mm=0.1)
    b = RLStepState(mean_surface_error_mm=10.0, finish_line_error_mm=10.0)
    assert compute_reward(a, validated_target_available=False) == compute_reward(
        b, validated_target_available=False
    )


def test_protected_contact_penalizes_and_terminates():
    safe = RLStepState(protected_contact=False)
    hit = RLStepState(protected_contact=True)
    assert compute_reward(hit, validated_target_available=False) < compute_reward(
        safe, validated_target_available=False
    )
    assert termination_reason(hit, step=1, max_steps=100) == "protected_contact"


def test_action_safety_clamps_policy_output():
    d = enforce_action(np.array([1, -1, 0, 1, -1, 0], dtype=np.float32))
    assert d.clipped
    assert np.all(np.abs(d.action[:3]) <= 0.00025 + 1e-8)
    assert np.all(np.abs(d.action[3:]) <= np.deg2rad(2.0) + 1e-8)


def test_contact_causes_zero_action_emergency_stop():
    d = enforce_action(np.ones(6), protected_contact=True)
    assert d.emergency_stop
    assert d.reason == "protected_contact"
    assert np.all(d.action == 0)
