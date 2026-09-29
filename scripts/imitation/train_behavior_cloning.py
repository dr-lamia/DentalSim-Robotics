#!/usr/bin/env python3
"""Train and export a lightweight DentalSim behavior-cloning policy."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from dentalsim.bc_dataset import BCDataset, discover_episodes, load_samples, split_by_tooth
from dentalsim.bc_policy import DentalBCPolicy


def metrics(pred, target):
    err = pred - target
    return {
        "mae": float(torch.mean(torch.abs(err)).item()),
        "rmse": float(torch.sqrt(torch.mean(err**2)).item()),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("hdf5", nargs="+", type=Path)
    p.add_argument("--output-dir", type=Path, default=ROOT / "runs" / "bc")
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--batch-size", type=int, default=128)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    episodes = discover_episodes(args.hdf5)
    if not episodes:
        raise SystemExit("No safe teleoperation episodes found")

    train_eps, val_eps = split_by_tooth(episodes, validation_fraction=0.15, seed=args.seed)
    train_x, train_y = load_samples(train_eps)
    val_x, val_y = load_samples(val_eps)

    mean = train_x.mean(axis=0)
    std = train_x.std(axis=0)
    std[std < 1e-8] = 1.0
    train_x = (train_x - mean) / std
    if len(val_x):
        val_x = (val_x - mean) / std

    train_loader = DataLoader(BCDataset(train_x, train_y), batch_size=args.batch_size, shuffle=True)

    model = DentalBCPolicy()
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-6)
    loss_fn = nn.SmoothL1Loss()

    best_state = None
    best_val = float("inf")
    patience = 12
    bad = 0
    history = []

    for epoch in range(1, args.epochs + 1):
        model.train()
        losses = []
        for x, y in train_loader:
            opt.zero_grad(set_to_none=True)
            pred = model(x)
            loss = loss_fn(pred, y)
            loss.backward()
            opt.step()
            losses.append(float(loss.item()))

        model.eval()
        with torch.no_grad():
            train_pred = model(torch.as_tensor(train_x, dtype=torch.float32))
            train_metrics = metrics(train_pred, torch.as_tensor(train_y, dtype=torch.float32))
            if len(val_x):
                val_pred = model(torch.as_tensor(val_x, dtype=torch.float32))
                val_metrics = metrics(val_pred, torch.as_tensor(val_y, dtype=torch.float32))
                monitor = val_metrics["rmse"]
            else:
                val_metrics = None
                monitor = train_metrics["rmse"]

        history.append({
            "epoch": epoch,
            "train_loss": float(np.mean(losses)),
            "train": train_metrics,
            "val": val_metrics,
        })

        if monitor < best_val:
            best_val = monitor
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            bad = 0
        else:
            bad += 1
            if bad >= patience:
                break

    model.load_state_dict(best_state)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    norm = {
        "mean": mean.tolist(),
        "std": std.tolist(),
        "state_order": [
            "bur_pose[7]",
            "bur_twist[6]",
            "target_relative_pose[7]",
            "adjacent_min_distance_mm[1]",
            "previous_action[6]",
        ],
        "action_order": ["dx_m", "dy_m", "dz_m", "droll_rad", "dpitch_rad", "dyaw_rad"],
    }
    (args.output_dir / "normalization.json").write_text(json.dumps(norm, indent=2), encoding="utf-8")
    (args.output_dir / "training_history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")

    model.eval()
    example = torch.zeros(1, 27)
    scripted = torch.jit.trace(model, example)
    scripted.save(str(args.output_dir / "dental_bc_v1.pt"))

    report = {
        "safe_episodes": len(episodes),
        "train_episodes": len(train_eps),
        "validation_episodes": len(val_eps),
        "train_teeth": sorted({e.tooth_id for e in train_eps}),
        "validation_teeth": sorted({e.tooth_id for e in val_eps}),
        "train_samples": int(len(train_x)),
        "validation_samples": int(len(val_x)),
        "best_monitor_rmse": best_val,
        "export": str(args.output_dir / "dental_bc_v1.pt"),
        "scientific_note": (
            "Case 15 may support motion/safety pretraining only until its target-preparation "
            "ground truth is validated."
        ),
    }
    (args.output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
