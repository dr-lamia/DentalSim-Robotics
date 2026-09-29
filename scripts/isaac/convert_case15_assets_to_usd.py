#!/usr/bin/env python3
"""Convert Case-15 dental meshes to USD inside NVIDIA Isaac Sim.

Run with Isaac Sim's Python environment, for example:
    ./python.sh scripts/isaac/convert_case15_assets_to_usd.py \
      --input-dir assets/case15 --output-dir assets/case15_usd
"""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from isaacsim import SimulationApp

app = SimulationApp({"headless": True})

import carb  # noqa: E402
import omni.kit.asset_converter  # noqa: E402


ASSETS = {
    "fdi15_anatomical_start_aligned.stl": "anatomical_start.usd",
    "prepared_stump_candidate_NOT_GROUND_TRUTH.stl": "prepared_candidate.usd",
    "protected_side_A_roi.ply": "protected_side_A.usd",
    "protected_side_B_roi.ply": "protected_side_B.usd",
    "fdi15_design_scan_frame.stl": "crown_design.usd",
}


async def convert_one(src: Path, dst: Path) -> None:
    def progress(current_step: int, total_steps: int):
        if total_steps:
            print(f"[{src.name}] {current_step}/{total_steps}")

    ctx = omni.kit.asset_converter.AssetConverterContext()
    ctx.ignore_materials = False
    ctx.ignore_animations = True
    ctx.ignore_camera = True
    ctx.ignore_light = True
    ctx.single_mesh = True
    ctx.smooth_normals = True
    ctx.export_preview_surface = True
    # Dental coordinates are numerically in millimetres. Keep vertex numbers
    # unchanged here; build_case15_stage.py applies an explicit 0.001 scale.
    ctx.use_meter_as_world_unit = False

    converter = omni.kit.asset_converter.get_instance()
    task = converter.create_converter_task(str(src), str(dst), progress, ctx)
    ok = await task.wait_until_finished()
    if not ok:
        raise RuntimeError(
            f"USD conversion failed for {src}: "
            f"{task.get_status()} {task.get_error_message()}"
        )


async def main_async(args) -> None:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for source_name, usd_name in ASSETS.items():
        src = args.input_dir / source_name
        dst = args.output_dir / usd_name
        if not src.exists():
            raise FileNotFoundError(src)
        print(f"Converting {src} -> {dst}")
        await convert_one(src, dst)
        if not dst.exists():
            raise RuntimeError(f"Converter returned success but {dst} is missing")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    try:
        asyncio.get_event_loop().run_until_complete(main_async(args))
        print("STATUS: CASE15 USD ASSETS READY")
    finally:
        app.close()


if __name__ == "__main__":
    main()
