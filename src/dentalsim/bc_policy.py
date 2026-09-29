"""Behavior-cloning policy for DentalSim-Robotics."""
from __future__ import annotations

import torch
from torch import nn


class DentalBCPolicy(nn.Module):
    def __init__(self, state_dim: int = 27, action_dim: int = 6):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
