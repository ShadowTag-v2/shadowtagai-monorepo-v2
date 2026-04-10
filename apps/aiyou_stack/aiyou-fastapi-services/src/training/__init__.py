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
    "TrainingExample",
    "GRPOSimulator",
    "GRPOvsPPOComparison",
    "compare_grpo_ppo",
]
