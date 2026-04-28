# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import torch
import torch.nn.functional as F
from torch import nn

# Alias for strict tensor tracking
Tensor = torch.Tensor


class MirasCore(nn.Module):  # type: ignore[misc]
    """SHADOWTAG NEURAL MEMORY (V7)
    Integrates Titans (Deep MLP) with Miras (Robust Optimization).
    """

    def __init__(self, d_model: int = 128) -> None:
        super().__init__()
        # Titans: Deep Memory for O(L) scaling
        self.memory: nn.Sequential = nn.Sequential(
            nn.Linear(d_model, d_model * 4),
            nn.SiLU(),
            nn.Linear(d_model * 4, d_model),
        )
        self.gate: nn.Linear = nn.Linear(d_model, 1)

    def forward(self, x: Tensor, state: Tensor) -> Tensor:
        """Forward pass applying adaptive gating to deep memory logic."""
        # Miras: Huber Loss for Robustness against "Poison" Data
        surprise: Tensor = F.huber_loss(x, state, reduction="none")

        # Adaptive Forgetting (The Gating Mechanism)
        forget_rate: Tensor = torch.sigmoid(self.gate(surprise))
        new_memory: Tensor = self.memory(x)

        updated_state: Tensor = (state * (1 - forget_rate)) + (new_memory * forget_rate)
        return updated_state
