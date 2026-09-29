#!/usr/bin/env python3
"""Author the Case-15 engineering USD scene inside NVIDIA Isaac Sim.

The prepared-stump candidate is intentionally non-collidable and is NOT a
scientific ground-truth target. This stage is for scene, camera, motion,
collision and reset engineering only.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from isaacsim import SimulationApp

app = SimulationApp({"headless": True})

import omni.usd  # noqa: E402
from pxr import Gf, PhysxSchema, Sdf, Usd, UsdGeom, UsdPhysics  # noqa: E402


MM_TO_M = 0.001

ASSETS = {
    "AnatomicalStart": ("anatomical_start.usd", True, False),
    "PreparedCandidate": ("prepared_candidate.usd", False, False),
    "ProtectedSideA": ("protected_side_A.usd", True, True),
    "ProtectedSideB": ("protected_side_B.usd", True, True),
    "CrownDesign": ("crown_design.usd", False, False),
}


def _set_transform(xform: UsdGeom.Xform, translate=(0.0, 0.0, 0.0), scale=1.0):
    ops = xform.GetOrderedXformOps()
    if ops:
        xform.ClearXformOpOrder()
    xform.AddTranslateOp().Set(Gf.Vec3d(*translate))
    xform.AddScaleOp().Set(Gf.Vec3f(scale, scale, scale))


def _apply_collision_to_mesh_descendants(root_prim: Usd.Prim) -> int:
    count = 0
    for prim in Usd.PrimRange(root_prim):
        if prim.IsA(UsdGeom.Mesh):
            UsdPhysics.CollisionAPI.Apply(prim)
            count += 1
    return count


def _add_reference(stage: Usd.Stage, name: str, usd_path: Path, collision: bool):
    path = f"/World/Dental/{name}"
    xf = UsdGeom.Xform.Define(stage, path)
    xf.GetPrim().GetReferences().AddReference(str(usd_path.resolve()))
    _set_transform(xf, scale=MM_TO_M)
    stage.GetRootLayer().Save()
    # Reload so descendants of the reference are available for traversal.
    stage.Reload()
    prim = stage.GetPrimAtPath(path)
    n_colliders = _apply_collision_to_mesh_descendants(prim) if collision else 0
    return path, n_colliders


def _create_procedural_bur(stage: Usd.Stage):
    bur = UsdGeom.Xform.Define(stage, "/World/Dental/Bur")
    _set_transform(bur, translate=(0.0, 0.0, 0.03), scale=1.0)

    rigid = UsdPhysics.RigidBodyAPI.Apply(bur.GetPrim())
    rigid.CreateKinematicEnabledAttr(True)
    PhysxSchema.PhysxContactReportAPI.Apply(bur.GetPrim()).CreateThresholdAttr(0.0)

    geom = UsdGeom.Cylinder.Define(stage, "/World/Dental/Bur/ActiveCylinder")
    geom.CreateAxisAttr("Z")
    geom.CreateRadiusAttr(0.0008)
    geom.CreateHeightAttr(0.008)
    UsdPhysics.CollisionAPI.Apply(geom.GetPrim())

    return "/World/Dental/Bur"


def _create_camera(stage, path, position, target):
    camera = UsdGeom.Camera.Define(stage, path)
    xf = UsdGeom.Xformable(camera)
    matrix = Gf.Matrix4d().SetLookAt(
        Gf.Vec3d(*position), Gf.Vec3d(*target), Gf.Vec3d(0, 0, 1)
    ).GetInverse()
    xf.AddTransformOp().Set(matrix)
    camera.CreateFocalLengthAttr(35.0)


def build_stage(asset_dir: Path, output: Path):
    stage = Usd.Stage.CreateNew(str(output))
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)

    UsdGeom.Xform.Define(stage, "/World")
    UsdGeom.Xform.Define(stage, "/World/Dental")

    physics = UsdPhysics.Scene.Define(stage, "/World/PhysicsScene")
    physics.CreateGravityDirectionAttr(Gf.Vec3f(0, 0, -1))
    physics.CreateGravityMagnitudeAttr(9.81)

    collider_counts = {}
    for name, (file_name, collision, protected) in ASSETS.items():
        usd_path = asset_dir / file_name
        if not usd_path.exists():
            raise FileNotFoundError(usd_path)
        prim_path, n = _add_reference(stage, name, usd_path, collision)
        collider_counts[name] = n
        prim = stage.GetPrimAtPath(prim_path)
        prim.SetCustomDataByKey("dentalsim:protected", bool(protected))
        prim.SetCustomDataByKey(
            "dentalsim:scientificGroundTruth",
            False if name == "PreparedCandidate" else None,
        )

    _create_procedural_bur(stage)

    # Camera locations are in metres.
    _create_camera(stage, "/World/Cameras/Overview", (0.06, -0.08, 0.06), (0, 0, 0.01))
    _create_camera(stage, "/World/Cameras/Occlusal", (0, 0, 0.08), (0, 0, 0.0))
    _create_camera(stage, "/World/Cameras/Buccal", (0, -0.08, 0.02), (0, 0, 0.01))

    stage.SetDefaultPrim(stage.GetPrimAtPath("/World"))
    stage.GetRootLayer().Save()
    return collider_counts


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--asset-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        counts = build_stage(args.asset_dir, args.output)
        print("Collider counts:", counts)
        if counts["ProtectedSideA"] == 0 or counts["ProtectedSideB"] == 0:
            raise RuntimeError("Protected anatomy imported without mesh colliders")
        print(f"STATUS: ISAAC STAGE AUTHORED -> {args.output}")
    finally:
        app.close()


if __name__ == "__main__":
    main()
