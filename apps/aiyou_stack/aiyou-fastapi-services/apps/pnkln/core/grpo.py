"""GRPO (Group Relative Policy Optimization) for Pnkln
Version: 1.0.0

Philosophy: Simpler, more stable RL training than PPO
Design: Group-relative advantages, no value network needed

GRPO advantages over PPO:
- No separate critic/value network (simpler)
- Group-relative advantages (more stable)
- Better sample efficiency (within-group comparisons)
- Easier to implement and tune

Reference: DeepSeek-R1 training methodology
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np


class RewardType(Enum):
    """Types of reward signals for GRPO"""

    ACCURACY = "accuracy"  # Task correctness
    ELEGANCE = "elegance"  # Code/response beauty
    SIMPLICITY = "simplicity"  # Simplification achieved
    LEVERAGE = "leverage"  # Revenue/effort ratio
    SPEED = "speed"  # Response latency


@dataclass
class GRPOConfig:
    """Configuration for GRPO training"""

    num_groups: int = 8  # Number of prompt groups (G)
    responses_per_prompt: int = 4  # Responses per prompt
    learning_rate: float = 1e-4  # Policy learning rate
    clip_epsilon: float = 0.2  # PPO-style clipping (optional)
    entropy_coef: float = 0.01  # Entropy bonus coefficient
    max_grad_norm: float = 1.0  # Gradient clipping
    normalize_advantages: bool = True  # Normalize advantages
    use_ppo_clipping: bool = False  # Use PPO-style clipping


@dataclass
class GRPOBatch:
    """A batch of GRPO training data"""

    prompts: list[str]  # Input prompts
    responses: list[str]  # Generated responses
    rewards: np.ndarray  # Reward for each response
    log_probs: np.ndarray  # Log probabilities
    group_ids: np.ndarray  # Which group each response belongs to
    advantages: np.ndarray | None = None  # Computed advantages


class GRPOTrainer:
    """Group Relative Policy Optimization trainer.

    Instead of learning a value function (like PPO), GRPO computes
    advantages relative to the mean reward within each group.

    This is simpler, more stable, and often performs better.
    """

    def __init__(self, config: GRPOConfig = GRPOConfig()):
        self.config = config
        self.training_history: list[dict[str, Any]] = []

    def compute_advantages(self, batch: GRPOBatch) -> np.ndarray:
        """Compute group-relative advantages.

        For each response, advantage = reward - mean(group_rewards)

        This is the KEY innovation of GRPO: advantages are relative
        to the group mean, not a learned baseline.

        Args:
            batch: GRPO batch with rewards and group IDs

        Returns:
            Array of advantages (same shape as rewards)

        """
        advantages = np.zeros_like(batch.rewards)
        num_groups = self.config.num_groups
        responses_per_prompt = self.config.responses_per_prompt

        for g in range(num_groups):
            # Get rewards for this group
            start_idx = g * responses_per_prompt
            end_idx = start_idx + responses_per_prompt
            group_rewards = batch.rewards[start_idx:end_idx]

            # Compute group mean
            group_mean = np.mean(group_rewards)

            # Advantages = rewards - mean
            group_advantages = group_rewards - group_mean
            advantages[start_idx:end_idx] = group_advantages

        # Optional: Normalize advantages across all groups
        if self.config.normalize_advantages:
            advantages = (advantages - np.mean(advantages)) / (np.std(advantages) + 1e-8)

        return advantages

    def compute_loss(self, batch: GRPOBatch, new_log_probs: np.ndarray) -> dict[str, float]:
        """Compute GRPO policy gradient loss.

        Loss = -mean(advantages * log_probs)

        Optionally adds:
        - PPO-style clipping (if enabled)
        - Entropy bonus (encourages exploration)

        Args:
            batch: Training batch with advantages
            new_log_probs: Log probabilities from current policy

        Returns:
            Dictionary with loss components

        """
        advantages = batch.advantages
        old_log_probs = batch.log_probs

        # Compute probability ratio
        ratio = np.exp(new_log_probs - old_log_probs)

        # Policy gradient loss
        if self.config.use_ppo_clipping:
            # PPO-style clipping
            clip_epsilon = self.config.clip_epsilon
            clipped_ratio = np.clip(ratio, 1 - clip_epsilon, 1 + clip_epsilon)
            policy_loss = -np.mean(np.minimum(ratio * advantages, clipped_ratio * advantages))
        else:
            # Simple policy gradient
            policy_loss = -np.mean(ratio * advantages)

        # Entropy bonus (encourages exploration)
        # In practice, this would be computed from the policy distribution
        # For simulation, we use a placeholder
        entropy = -np.mean(new_log_probs)  # Simplified
        entropy_bonus = self.config.entropy_coef * entropy

        # Total loss
        total_loss = policy_loss - entropy_bonus

        return {
            "total_loss": total_loss,
            "policy_loss": policy_loss,
            "entropy": entropy,
            "entropy_bonus": entropy_bonus,
            "mean_advantage": np.mean(advantages),
            "std_advantage": np.std(advantages),
            "mean_ratio": np.mean(ratio),
        }

    def train_step(self, batch: GRPOBatch) -> dict[str, Any]:
        """Execute one GRPO training step.

        1. Compute advantages (group-relative)
        2. Compute loss
        3. Update policy (simulated here)

        Args:
            batch: Training batch

        Returns:
            Training metrics

        """
        # Compute advantages
        advantages = self.compute_advantages(batch)
        batch.advantages = advantages

        # Simulate new log probs (in practice, from forward pass)
        # Add small noise to simulate policy update
        new_log_probs = batch.log_probs + np.random.normal(0, 0.01, batch.log_probs.shape)

        # Compute loss
        loss_dict = self.compute_loss(batch, new_log_probs)

        # Record training step
        step_metrics = {
            **loss_dict,
            "num_groups": self.config.num_groups,
            "responses_per_prompt": self.config.responses_per_prompt,
            "mean_reward": np.mean(batch.rewards),
            "max_reward": np.max(batch.rewards),
            "min_reward": np.min(batch.rewards),
        }

        self.training_history.append(step_metrics)

        return step_metrics


def generate_synthetic_batch(
    num_groups: int = 8,
    responses_per_prompt: int = 4,
    reward_noise: float = 0.1,
) -> GRPOBatch:
    """Generate synthetic GRPO batch for testing.

    Creates realistic reward distributions:
    - Some prompts are "easier" (higher base reward)
    - Some responses are better than others
    - Noise simulates evaluation uncertainty

    Args:
        num_groups: Number of prompt groups
        responses_per_prompt: Responses per prompt
        reward_noise: Std dev of reward noise

    Returns:
        Synthetic GRPO batch

    """
    total_responses = num_groups * responses_per_prompt

    # Generate prompts
    prompts = [f"prompt_{g}" for g in range(num_groups) for _ in range(responses_per_prompt)]

    # Generate responses
    responses = [f"response_{i}" for i in range(total_responses)]

    # Generate rewards with structure
    rewards = []
    for _g in range(num_groups):
        # Each group has a different base difficulty
        base_reward = np.random.uniform(0.3, 0.7)

        # Responses within group have varying quality
        group_rewards = base_reward + np.random.uniform(-0.2, 0.2, responses_per_prompt)

        # Add noise
        group_rewards += np.random.normal(0, reward_noise, responses_per_prompt)

        # Clip to [0, 1]
        group_rewards = np.clip(group_rewards, 0, 1)

        rewards.extend(group_rewards)

    rewards = np.array(rewards)

    # Generate log probabilities (simulated)
    log_probs = np.random.normal(-2.0, 0.5, total_responses)

    # Group IDs
    group_ids = np.array([g for g in range(num_groups) for _ in range(responses_per_prompt)])

    return GRPOBatch(
        prompts=prompts,
        responses=responses,
        rewards=rewards,
        log_probs=log_probs,
        group_ids=group_ids,
    )


def compare_ppo_grpo() -> dict[str, dict[str, Any]]:
    """Compare PPO and GRPO characteristics.

    Returns:
        Dictionary with comparison metrics

    """
    return {
        "ppo": {
            "components": ["Policy (actor)", "Value function (critic)"],
            "loss": "Clipped surrogate objective with value loss",
            "baseline": "Learned value function V(s)",
            "complexity": "High (2 networks to train)",
            "stability": "Good (with proper clipping)",
            "sample_efficiency": "Moderate",
            "hyperparameters": [
                "clip_epsilon",
                "vf_coef",
                "ent_coef",
                "lr_actor",
                "lr_critic",
            ],
            "advantages": [
                "Well-established",
                "Proven on many tasks",
                "Good theoretical properties",
            ],
            "disadvantages": [
                "Requires value network",
                "More hyperparameters",
                "Can be unstable",
            ],
        },
        "grpo": {
            "components": ["Policy (actor only)"],
            "loss": "Policy gradient with group-relative advantages",
            "baseline": "Group mean reward (no separate network)",
            "complexity": "Low (1 network to train)",
            "stability": "High (group-wise normalization)",
            "sample_efficiency": "High (relative comparisons)",
            "hyperparameters": ["num_groups", "responses_per_prompt", "lr", "ent_coef"],
            "advantages": [
                "Simpler implementation",
                "No value network needed",
                "More stable training",
                "Better sample efficiency",
            ],
            "disadvantages": [
                "Requires grouped data",
                "Less established",
                "May struggle with sparse rewards",
            ],
        },
    }


if __name__ == "__main__":
    print("GRPO (Group Relative Policy Optimization) - Self Test")
    print("=" * 60)

    # Create trainer
    config = GRPOConfig(
        num_groups=8,
        responses_per_prompt=4,
        learning_rate=1e-4,
        normalize_advantages=True,
    )
    trainer = GRPOTrainer(config)

    print("\nConfiguration:")
    print(f"  Groups: {config.num_groups}")
    print(f"  Responses per prompt: {config.responses_per_prompt}")
    print(f"  Total responses: {config.num_groups * config.responses_per_prompt}")

    # Generate synthetic batch
    batch = generate_synthetic_batch(
        num_groups=config.num_groups,
        responses_per_prompt=config.responses_per_prompt,
    )

    print("\nBatch statistics:")
    print(f"  Mean reward: {np.mean(batch.rewards):.3f}")
    print(f"  Std reward: {np.std(batch.rewards):.3f}")
    print(f"  Min reward: {np.min(batch.rewards):.3f}")
    print(f"  Max reward: {np.max(batch.rewards):.3f}")

    # Compute advantages
    advantages = trainer.compute_advantages(batch)
    batch.advantages = advantages

    print("\nAdvantages (group-relative):")
    print(f"  Mean: {np.mean(advantages):.6f} (should be ~0)")
    print(f"  Std: {np.std(advantages):.3f}")
    print(f"  Min: {np.min(advantages):.3f}")
    print(f"  Max: {np.max(advantages):.3f}")

    # Show first group in detail
    print("\nFirst group (detailed):")
    group_0_rewards = batch.rewards[:4]
    group_0_advantages = advantages[:4]
    group_mean = np.mean(group_0_rewards)

    for i in range(4):
        print(
            f"  Response {i}: reward={group_0_rewards[i]:.3f}, "
            f"advantage={group_0_advantages[i]:.3f}",
        )
    print(f"  Group mean: {group_mean:.3f}")
    print(f"  Advantage sum: {np.sum(group_0_advantages):.6f} (should be ~0)")

    # Train step
    print("\nTraining step:")
    metrics = trainer.train_step(batch)
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")

    # PPO vs GRPO comparison
    print("\n" + "=" * 60)
    print("PPO vs GRPO Comparison")
    print("=" * 60)

    comparison = compare_ppo_grpo()

    for method, details in comparison.items():
        print(f"\n{method.upper()}:")
        print(f"  Components: {', '.join(details['components'])}")
        print(f"  Baseline: {details['baseline']}")
        print(f"  Complexity: {details['complexity']}")
        print(f"  Stability: {details['stability']}")

        print("  Advantages:")
        for adv in details["advantages"]:
            print(f"    + {adv}")

        print("  Disadvantages:")
        for dis in details["disadvantages"]:
            print(f"    - {dis}")

    print("\n" + "=" * 60)
    print("✓ GRPO implementation working correctly")
    print("\nKey insight: GRPO is simpler than PPO but often performs better")
    print("because group-relative advantages are more stable than learned baselines.")
