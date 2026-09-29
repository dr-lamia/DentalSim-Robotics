from pathlib import Path
import sys
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.geometry_metrics import evaluate_surface_deviation


def test_identical_mesh_has_small_sampling_deviation():
    a = trimesh.creation.icosphere(subdivisions=2, radius=5.0)
    m = evaluate_surface_deviation(a, a, sample_count=20000, seed=7)
    assert m.symmetric_mean_mm < 0.15
    assert m.symmetric_p95_mm < 0.30


def test_shifted_mesh_increases_error():
    a = trimesh.creation.icosphere(subdivisions=2, radius=5.0)
    b = a.copy()
    b.apply_translation([1.0, 0.0, 0.0])

    same = evaluate_surface_deviation(a, a, sample_count=12000, seed=3)
    shifted = evaluate_surface_deviation(b, a, sample_count=12000, seed=3)

    assert shifted.symmetric_mean_mm > same.symmetric_mean_mm
    assert shifted.final_to_target_p95_mm > same.final_to_target_p95_mm


def test_metrics_are_deterministic_for_fixed_seed():
    a = trimesh.creation.box(extents=[8.0, 7.0, 5.0])
    b = a.copy()
    b.apply_translation([0.2, 0.0, 0.0])

    x = evaluate_surface_deviation(a, b, sample_count=5000, seed=99)
    y = evaluate_surface_deviation(a, b, sample_count=5000, seed=99)
    assert x.to_dict() == y.to_dict()
