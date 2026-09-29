from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.scoring import PrepMetrics, reward, safety_pass, task_success


def good_metrics():
    return PrepMetrics(
        mean_surface_deviation_mm=0.2,
        p95_surface_deviation_mm=0.4,
        finish_line_mean_deviation_mm=0.2,
        taper_error_deg=2.0,
        over_reduction_mm=0.1,
        adjacent_collision_count=0,
        pulp_min_distance_mm=0.8,
        smoothness_score=0.9,
        undercut_count=0,
    )


def test_good_preparation_passes():
    m = good_metrics()
    assert safety_pass(m)
    assert task_success(m)


def test_collision_forces_failure():
    m = good_metrics()
    m.adjacent_collision_count = 1
    assert not safety_pass(m)
    assert not task_success(m)


def test_better_geometry_gets_better_reward():
    good = good_metrics()
    bad = good_metrics()
    bad.mean_surface_deviation_mm = 1.2
    bad.finish_line_mean_deviation_mm = 0.9
    bad.taper_error_deg = 10.0
    assert reward(good) > reward(bad)
