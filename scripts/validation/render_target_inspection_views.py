#!/usr/bin/env python3
"""Render standardized orientation-neutral target inspection views.

The renderer labels views by source scan axes rather than guessing anatomical
buccal/palatal orientation from mesh coordinates.
"""
from __future__ import annotations
import argparse, math
from pathlib import Path
import trimesh
import matplotlib.pyplot as plt
from PIL import Image


VIEWS = {
    "01_plus_Z": (90, -90),
    "02_minus_Z": (-90, 90),
    "03_plus_X": (0, 0),
    "04_minus_X": (0, 180),
    "05_plus_Y": (0, 90),
    "06_minus_Y": (0, -90),
    "07_perspective": (28, -48),
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mesh", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    args = p.parse_args()

    mesh = trimesh.load_mesh(args.mesh, process=True)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    center = mesh.bounds.mean(axis=0)
    vertices = mesh.vertices - center
    faces = mesh.faces
    extent = max(mesh.extents) * 0.62

    rendered = []
    for name, (elev, azim) in VIEWS.items():
        fig = plt.figure(figsize=(5, 5))
        ax = fig.add_subplot(111, projection="3d")
        ax.plot_trisurf(
            vertices[:, 0], vertices[:, 1], vertices[:, 2],
            triangles=faces, linewidth=0.15, antialiased=True, shade=True
        )
        ax.set_box_aspect((1, 1, 1))
        ax.set_xlim(-extent, extent)
        ax.set_ylim(-extent, extent)
        ax.set_zlim(-extent, extent)
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()
        ax.set_title(name.replace("_", " "))
        fig.tight_layout()
        out = args.out_dir / f"{name}.png"
        fig.savefig(out, dpi=220, bbox_inches="tight")
        plt.close(fig)
        rendered.append(out)

    images = [Image.open(x).convert("RGB") for x in rendered]
    width = 700
    thumbs = []
    for im in images:
        ratio = width / im.width
        thumbs.append(im.resize((width, int(im.height * ratio))))

    cell_h = max(im.height for im in thumbs)
    cols = 2
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * width, rows * cell_h), "white")

    for i, im in enumerate(thumbs):
        sheet.paste(im, ((i % cols) * width, (i // cols) * cell_h))

    sheet_path = args.out_dir / "multiview_sheet.png"
    sheet.save(sheet_path)
    print(sheet_path)


if __name__ == "__main__":
    main()
