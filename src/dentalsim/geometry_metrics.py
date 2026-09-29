"""Geometry metrics for DentalSim-Robotics preparation evaluation.

All functions operate in millimetres and must only be used after the target
manifest has passed the physical-scale and target-validation gates.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree


@dataclass(frozen=True)
class SurfaceDeviationMetrics:
    sample_count_final: int
    sample_count_target: int
    final_to_target_mean_mm: float
    final_to_target_median_mm: float
    final_to_target_p95_mm: float
    final_to_target_max_mm: float
    target_to_final_mean_mm: float
    target_to_final_median_mm: float
    target_to_final_p95_mm: float
    target_to_final_max_mm: float
    symmetric_mean_mm: float
    symmetric_p95_mm: float
    within_0_25_mm_fraction: float
    within_0_50_mm_fraction: float
    within_1_00_mm_fraction: float

    def to_dict(self):
        return asdict(self)


def _sample_surface(mesh: trimesh.Trimesh, n: int, seed: int) -> np.ndarray:
    if n <= 0:
        raise ValueError("sample count must be positive")
    # trimesh surface sampling uses NumPy's global RNG. Save/restore state so
    # the function is deterministic without contaminating caller randomness.
    state = np.random.get_state()
    try:
        np.random.seed(seed)
        pts, _ = trimesh.sample.sample_surface(mesh, n)
    finally:
        np.random.set_state(state)
    return np.asarray(pts, dtype=float)


def evaluate_surface_deviation(
    final_mesh: trimesh.Trimesh,
    target_mesh: trimesh.Trimesh,
    *,
    sample_count: int = 50000,
    seed: int = 42,
) -> SurfaceDeviationMetrics:
    """Compute deterministic bidirectional nearest-surface proxy metrics.

    Distances are computed between independently sampled surface point clouds.
    This is robust for open scan surfaces and does not require watertight meshes.
    It is intentionally unsigned; over- vs under-reduction requires a separate
    signed geometry method and should not be inferred from these values.
    """
    if len(final_mesh.faces) == 0 or len(target_mesh.faces) == 0:
        raise ValueError("both meshes must contain faces")

    final_pts = _sample_surface(final_mesh, sample_count, seed)
    target_pts = _sample_surface(target_mesh, sample_count, seed + 1)

    target_tree = cKDTree(target_pts)
    final_tree = cKDTree(final_pts)

    d_ft, _ = target_tree.query(final_pts, k=1)
    d_tf, _ = final_tree.query(target_pts, k=1)

    all_d = np.concatenate([d_ft, d_tf])

    return SurfaceDeviationMetrics(
        sample_count_final=int(len(final_pts)),
        sample_count_target=int(len(target_pts)),
        final_to_target_mean_mm=float(np.mean(d_ft)),
        final_to_target_median_mm=float(np.median(d_ft)),
        final_to_target_p95_mm=float(np.percentile(d_ft, 95)),
        final_to_target_max_mm=float(np.max(d_ft)),
        target_to_final_mean_mm=float(np.mean(d_tf)),
        target_to_final_median_mm=float(np.median(d_tf)),
        target_to_final_p95_mm=float(np.percentile(d_tf, 95)),
        target_to_final_max_mm=float(np.max(d_tf)),
        symmetric_mean_mm=float(np.mean(all_d)),
        symmetric_p95_mm=float(np.percentile(all_d, 95)),
        within_0_25_mm_fraction=float(np.mean(d_ft <= 0.25)),
        within_0_50_mm_fraction=float(np.mean(d_ft <= 0.50)),
        within_1_00_mm_fraction=float(np.mean(d_ft <= 1.00)),
    )


def load_mesh(path: str | Path) -> trimesh.Trimesh:
    mesh = trimesh.load_mesh(Path(path), process=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"Expected Trimesh, got {type(mesh).__name__}")
    return mesh
