#!/usr/bin/env python3
"""Render standardized, orientation-neutral target inspection views.

Views are labelled by source-coordinate axes to avoid inventing anatomical
buccal/lingual labels when those are not encoded explicitly in the source.

For large STL scans, deterministic face sampling keeps rendering practical
without altering the source mesh or scientific evidence.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import json
import math

import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import trimesh


VIEWS = {
    "01_plus_Z": (90, -90),
    "02_minus_Z": (-90, 90),
    "03_plus_X": (0, 0),
    "04_minus_X": (0, 180),
    "05_plus_Y": (0, 90),
    "06_minus_Y": (0, -90),
    "07_perspective": (28, -48),
}


def render(mesh_path: Path, out_dir: Path, dpi: int = 160, max_faces: int = 12000) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    mesh = trimesh.load_mesh(mesh_path, process=True)
    center = mesh.bounds.mean(axis=0)
    vertices = mesh.vertices - center

    if max_faces and len(mesh.faces) > max_faces:
        idx = np.linspace(0, len(mesh.faces) - 1, max_faces, dtype=int)
        faces = mesh.faces[idx]
    else:
        faces = mesh.faces

    extent = float(max(mesh.extents) * 0.62)

    rendered = []
    for name, (elev, azim) in VIEWS.items():
        fig = plt.figure(figsize=(4.2, 4.2))
        ax = fig.add_subplot(111, projection="3d")
        ax.plot_trisurf(
            vertices[:, 0], vertices[:, 1], vertices[:, 2],
            triangles=faces, linewidth=0.0, antialiased=False, shade=True
        )
        ax.set_box_aspect((1, 1, 1))
        ax.set_xlim(-extent, extent)
        ax.set_ylim(-extent, extent)
        ax.set_zlim(-extent, extent)
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()
        ax.set_title(name.replace("_", " "))
        fig.tight_layout()
        path = out_dir / f"{name}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        rendered.append(path)

    images = [Image.open(p).convert("RGB") for p in rendered]
    thumb_w = 520
    thumbs = []
    for im in images:
        ratio = thumb_w / im.width
        thumbs.append(im.resize((thumb_w, int(im.height * ratio))))

    cell_h = max(im.height for im in thumbs)
    cols = 2
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * cell_h), "white")
    for i, im in enumerate(thumbs):
        sheet.paste(im, ((i % cols) * thumb_w, (i // cols) * cell_h))

    sheet_path = out_dir / "candidate_multiview_sheet.png"
    sheet.save(sheet_path, quality=95)

    summary = {
        "mesh_file": mesh_path.name,
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "rendered_faces": int(len(faces)),
        "face_sampling_applied": bool(len(faces) < len(mesh.faces)),
        "bounds_mm": mesh.bounds.tolist(),
        "extents_mm": mesh.extents.tolist(),
        "views": [p.name for p in rendered],
        "sheet": sheet_path.name,
        "orientation_note": (
            "Views are labelled by source-coordinate axes; anatomical "
            "buccal/lingual/mesial/distal names are not inferred."
        ),
        "rendering_note": (
            "Face sampling affects visualization only; source geometry and "
            "QA measurements remain computed from the full mesh."
        ),
    }
    (out_dir / "inspection_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mesh", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--dpi", type=int, default=160)
    p.add_argument("--max-faces", type=int, default=12000)
    args = p.parse_args()
    print(json.dumps(render(args.mesh, args.out_dir, args.dpi, args.max_faces), indent=2))


if __name__ == "__main__":
    main()
