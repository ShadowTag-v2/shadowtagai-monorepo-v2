# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Training systems for kernel/agent evolution."""

from .grpo import (
    GRPOConfig,
    TrainingExample,
    GRPOSimulator,
    GRPOvsPPOComparison,
    compare_grpo_ppo,
)

__all__ = [
    "GRPOConfig",
    "TrainingExample",
    "GRPOSimulator",
    "GRPOvsPPOComparison",
    "compare_grpo_ppo",
]
