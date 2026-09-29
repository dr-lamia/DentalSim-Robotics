"""NVIDIA Isaac for Healthcare adapter boundary.

The module is import-safe without Isaac Sim. It provides a concrete scene plan
now and activates actual Isaac APIs only inside an NVIDIA Isaac environment.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .scene_contract import Pose6D, SafetyEnvelope, vec_mm_to_m


@dataclass(frozen=True)
class SceneAsset:
    name: str
    prim_path: str
    mesh_path: str
    pose: Pose6D
    collision_enabled: bool = True
    protected: bool = False


@dataclass(frozen=True)
class IsaacScenePlan:
    assets: tuple[SceneAsset, ...]
    bur_prim_path: str
    safety: SafetyEnvelope
    cameras: tuple[str, ...] = ("overview", "occlusal", "labial")


def phase1_scene_plan(project_root: str | Path) -> IsaacScenePlan:
    root = Path(project_root)
    assets_dir = root / "assets"
    return IsaacScenePlan(
        assets=(
            SceneAsset("target_tooth", "/World/Dental/Tooth11", str(assets_dir / "tooth_11_unprepared.stl"), Pose6D(0, 0, 0)),
            SceneAsset("ideal_preparation", "/World/Dental/TargetPrep", str(assets_dir / "tooth_11_target_prep.stl"), Pose6D(0, 0, 0), collision_enabled=False),
            SceneAsset("adjacent_12", "/World/Dental/Tooth12", str(assets_dir / "tooth_12.stl"), Pose6D(-8.5, 0, 0), protected=True),
            SceneAsset("adjacent_21", "/World/Dental/Tooth21", str(assets_dir / "tooth_21.stl"), Pose6D(8.5, 0, 0), protected=True),
            SceneAsset("bur", "/World/Dental/Bur", str(assets_dir / "diamond_bur.stl"), Pose6D(0, -12, 12)),
        ),
        bur_prim_path="/World/Dental/Bur",
        safety=SafetyEnvelope(),
    )


def validate_asset_files(plan: IsaacScenePlan) -> list[str]:
    """Return missing required meshes. TargetPrep is required for scoring."""
    return [a.mesh_path for a in plan.assets if not Path(a.mesh_path).exists()]


def as_isaac_translation(pose: Pose6D) -> tuple[float, float, float]:
    """Convert the clinically readable millimetre pose to Isaac SI metres."""
    return vec_mm_to_m(pose.position_mm)


def isaac_available() -> bool:
    try:
        import isaacsim  # type: ignore  # noqa: F401
    except ImportError:
        return False
    return True


def build_scene(project_root: str | Path) -> IsaacScenePlan:
    """Preflight the scene and return its plan.

    Actual USD live-authoring belongs in an i4h-workflows checkout following
    NVIDIA's i4h-workflow-scene-edit contract. This function intentionally
    refuses to claim simulator construction if Isaac is absent or meshes are
    missing.
    """
    plan = phase1_scene_plan(project_root)
    missing = validate_asset_files(plan)
    if missing:
        raise FileNotFoundError("Missing dental meshes: " + ", ".join(missing))
    if not isaac_available():
        raise RuntimeError(
            "Isaac Sim is not available in this Python environment. Copy the validated "
            "assets/ into an i4h-workflows checkout and run the scene authoring stage there."
        )
    return plan
