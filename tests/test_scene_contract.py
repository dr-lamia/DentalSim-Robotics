from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.baseline_controller import finish_line_ring
from dentalsim.isaac_adapter import as_isaac_translation, phase1_scene_plan
from dentalsim.scene_contract import Pose6D, SafetyEnvelope, SafetyState, bounded_delta, path_length_mm


def test_mm_to_isaac_metres():
    assert as_isaac_translation(Pose6D(1.0, -2.0, 10.0)) == (0.001, -0.002, 0.01)


def test_safety_gate_rejects_adjacent_clearance():
    env = SafetyEnvelope(adjacent_clearance_mm=0.30, pulp_clearance_mm=0.50)
    s = SafetyState(adjacent_min_distance_mm=0.20, pulp_min_distance_mm=1.2)
    assert not s.allowed(env)
    assert "adjacent_clearance_violation" in s.reasons


def test_safety_gate_rejects_pulp_clearance():
    env = SafetyEnvelope()
    s = SafetyState(adjacent_min_distance_mm=2.0, pulp_min_distance_mm=0.49)
    assert not s.allowed(env)
    assert "pulp_clearance_violation" in s.reasons


def test_action_is_bounded():
    env = SafetyEnvelope(max_translation_mm_per_step=0.25, max_rotation_deg_per_step=2.0)
    p = bounded_delta(Pose6D(0, 0, 0), Pose6D(1, -1, 0.1, 5, -5, 1), env)
    assert p == Pose6D(0.25, -0.25, 0.1, 2.0, -2.0, 1.0)


def test_baseline_path_is_closed_and_nontrivial():
    path = finish_line_ring(points=72)
    assert len(path) == 75
    assert path_length_mm(path) > 20.0
    assert abs(path[1].x_mm - path[-2].x_mm) < 1e-9
    assert abs(path[1].y_mm - path[-2].y_mm) < 1e-9


def test_scene_marks_adjacent_teeth_protected(tmp_path):
    plan = phase1_scene_plan(tmp_path)
    protected = {a.name for a in plan.assets if a.protected}
    assert protected == {"adjacent_12", "adjacent_21"}
    assert plan.bur_prim_path == "/World/Dental/Bur"
