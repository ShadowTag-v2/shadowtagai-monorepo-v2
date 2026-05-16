# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
GRPO (Group Relative Policy Optimization) training simulation.

Comparison with PPO (Proximal Policy Optimization):
- GRPO: Uses relative advantages within groups (G responses)
- PPO: Uses clipped loss with absolute advantages
- GRPO better for LLM reasoning tasks (per architecture spec)
"""

import math
import random
from typing import Any

from pydantic import BaseModel, Field


class GRPOConfig(BaseModel):
  """Configuration for GRPO training."""

  group_size: int = Field(8, description="Number of responses per prompt (G)")
  learning_rate: float = Field(1e-5, description="Learning rate")
  beta: float = Field(0.01, description="KL divergence coefficient")
  epsilon: float = Field(
    0.2, description="Clipping parameter (for comparison with PPO)"
  )


class TrainingExample(BaseModel):
  """Single training example with multiple responses."""

  prompt: str
  responses: list[str]
  rewards: list[float]  # Reward for each response
  advantages: list[float] = Field(default_factory=list)  # Computed relative advantages


class GRPOSimulator:
  """
  Simulate GRPO training for kernel/agent optimization.

  Used to evolve kernels via relative performance within groups.
  """

  def __init__(self, config: GRPOConfig):
    self.config = config

  def compute_advantages(self, rewards: list[float]) -> list[float]:
    """
    Compute relative advantages within group.

    GRPO key insight: Advantages are relative to group mean,
    not absolute rewards. This reduces variance.

    Args:
        rewards: List of rewards for G responses

    Returns:
        List of relative advantages (mean-centered)
    """
    mean_reward = sum(rewards) / len(rewards) if rewards else 0.0
    return [r - mean_reward for r in rewards]

  def compute_grpo_loss(
    self,
    log_probs: list[float],
    advantages: list[float],
    old_log_probs: list[float],
  ) -> float:
    """
    Compute GRPO loss.

    Loss = -mean(ratio * advantage) + beta * KL
    where ratio = exp(log_prob - old_log_prob)

    Args:
        log_probs: Current policy log probabilities
        advantages: Relative advantages
        old_log_probs: Old policy log probabilities

    Returns:
        GRPO loss value
    """
    losses = []
    kl_divs = []

    for log_p, adv, old_log_p in zip(log_probs, advantages, old_log_probs):
      ratio = math.exp(log_p - old_log_p)
      policy_loss = -ratio * adv

      # KL divergence (approximation)
      kl = old_log_p - log_p

      losses.append(policy_loss)
      kl_divs.append(kl)

    mean_loss = sum(losses) / len(losses) if losses else 0.0
    mean_kl = sum(kl_divs) / len(kl_divs) if kl_divs else 0.0

    return mean_loss + self.config.beta * mean_kl

  def compute_ppo_loss(
    self,
    log_probs: list[float],
    advantages: list[float],
    old_log_probs: list[float],
  ) -> float:
    """
    Compute PPO loss for comparison.

    Loss = -mean(min(ratio * advantage, clip(ratio) * advantage))

    Args:
        log_probs: Current policy log probabilities
        advantages: Advantages (NOT relative in standard PPO)
        old_log_probs: Old policy log probabilities

    Returns:
        PPO clipped loss value
    """
    epsilon = self.config.epsilon
    losses = []

    for log_p, adv, old_log_p in zip(log_probs, advantages, old_log_probs):
      ratio = math.exp(log_p - old_log_p)
      clip_ratio = max(1 - epsilon, min(1 + epsilon, ratio))

      loss1 = -ratio * adv
      loss2 = -clip_ratio * adv

      losses.append(max(loss1, loss2))  # Take maximum (worse) loss

    return sum(losses) / len(losses) if losses else 0.0

  def simulate_training_step(
    self,
    prompt: str,
    responses: list[str],
    rewards: list[float],
  ) -> dict[str, Any]:
    """
    Simulate one GRPO training step.

    Args:
        prompt: Input prompt
        responses: G generated responses
        rewards: Rewards for each response

    Returns:
        Training step results with GRPO vs PPO comparison
    """
    # Compute relative advantages (GRPO)
    advantages_grpo = self.compute_advantages(rewards)

    # Simulate log probabilities (in real training, these come from model)
    old_log_probs = [random.uniform(-2, -0.5) for _ in responses]
    new_log_probs = [old + random.uniform(-0.1, 0.1) for old in old_log_probs]

    # Compute losses
    grpo_loss = self.compute_grpo_loss(new_log_probs, advantages_grpo, old_log_probs)

    # For PPO comparison, use same advantages (though PPO typically uses GAE)
    ppo_loss = self.compute_ppo_loss(new_log_probs, advantages_grpo, old_log_probs)

    return {
      "prompt": prompt,
      "group_size": len(responses),
      "rewards": rewards,
      "mean_reward": sum(rewards) / len(rewards),
      "advantages_grpo": advantages_grpo,
      "grpo_loss": grpo_loss,
      "ppo_loss": ppo_loss,
      "loss_difference": ppo_loss - grpo_loss,
    }


class GRPOvsPPOComparison(BaseModel):
  """Comparison of GRPO vs PPO training approaches."""

  aspect: str
  grpo: str
  ppo: str
  winner: str  # "GRPO", "PPO", or "Tie"


def compare_grpo_ppo() -> list[GRPOvsPPOComparison]:
  """
  Compare GRPO vs PPO across key dimensions.

  Returns:
      List of comparisons
  """
  return [
    GRPOvsPPOComparison(
      aspect="Advantage Calculation",
      grpo="Relative to group mean (variance reduction)",
      ppo="Absolute or GAE (higher variance)",
      winner="GRPO",
    ),
    GRPOvsPPOComparison(
      aspect="Loss Function",
      grpo="Ratio * advantage + KL penalty",
      ppo="Clipped ratio * advantage",
      winner="Tie",
    ),
    GRPOvsPPOComparison(
      aspect="Sample Efficiency",
      grpo="High (G responses per prompt)",
      ppo="Medium (single response per prompt typically)",
      winner="GRPO",
    ),
    GRPOvsPPOComparison(
      aspect="Reasoning Tasks",
      grpo="Excellent (relative advantages help)",
      ppo="Good (but higher variance)",
      winner="GRPO",
    ),
    GRPOvsPPOComparison(
      aspect="Implementation Complexity",
      grpo="Low (no clipping needed)",
      ppo="Medium (clipping logic)",
      winner="GRPO",
    ),
    GRPOvsPPOComparison(
      aspect="Stability",
      grpo="High (KL penalty prevents drift)",
      ppo="High (clipping prevents drift)",
      winner="Tie",
    ),
  ]
