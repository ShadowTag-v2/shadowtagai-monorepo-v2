# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Training systems for kernel/agent evolution."""

from .grpo import (
    GRPOConfig,
    GRPOSimulator,
    GRPOvsPPOComparison,
    TrainingExample,
    compare_grpo_ppo,
)

__all__ = [
    "GRPOConfig",
    "GRPOSimulator",
    "GRPOvsPPOComparison",
    "TrainingExample",
    "compare_grpo_ppo",
]
