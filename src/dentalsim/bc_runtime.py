"""Runtime wrapper for an exported DentalSim behavior-cloning policy."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch


class BCRuntime:
    def __init__(self, model_path: str | Path, normalization_json: str | Path):
        self.model = torch.jit.load(str(model_path), map_location="cpu")
        self.model.eval()
        norm = json.loads(Path(normalization_json).read_text(encoding="utf-8"))
        self.mean = np.asarray(norm["mean"], dtype=np.float32)
        self.std = np.asarray(norm["std"], dtype=np.float32)

    def predict(self, state_27) -> np.ndarray:
        x = np.asarray(state_27, dtype=np.float32)
        if x.shape != (27,):
            raise ValueError(f"Expected state shape (27,), got {x.shape}")
        x = (x - self.mean) / self.std
        with torch.no_grad():
            y = self.model(torch.as_tensor(x[None, :])).numpy()[0]
        # Final hard safety clamp at the runtime boundary.
        y[:3] = np.clip(y[:3], -0.00025, 0.00025)
        rot = np.deg2rad(2.0)
        y[3:] = np.clip(y[3:], -rot, rot)
        return y.astype(np.float32)
