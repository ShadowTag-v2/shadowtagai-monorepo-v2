"""Tests for GRPO (Group Relative Policy Optimization)"""

import numpy as np
import pytest

from shadowtagai.core.grpo import (
    GRPOBatch,
    GRPOConfig,
    GRPOTrainer,
    compare_ppo_grpo,
    generate_synthetic_batch,
)


class TestGRPOConfig:
    """Test GRPO configuration"""

    def test_default_config(self):
        """Test default configuration values"""
        config = GRPOConfig()

        assert config.num_groups == 8
        assert config.responses_per_prompt == 4
        assert config.learning_rate == 1e-4
        assert config.normalize_advantages

    def test_custom_config(self):
        """Test custom configuration"""
        config = GRPOConfig(num_groups=16, responses_per_prompt=8, learning_rate=1e-3)

        assert config.num_groups == 16
        assert config.responses_per_prompt == 8
        assert config.learning_rate == 1e-3


class TestGRPOBatch:
    """Test GRPO batch structure"""

    def test_batch_creation(self):
        """Test creating a GRPO batch"""
        batch = generate_synthetic_batch(num_groups=4, responses_per_prompt=2)

        assert len(batch.prompts) == 8  # 4 groups * 2 responses
        assert len(batch.responses) == 8
        assert batch.rewards.shape == (8,)
        assert batch.log_probs.shape == (8,)
        assert batch.group_ids.shape == (8,)

    def test_batch_rewards_valid(self):
        """Test that synthetic rewards are valid"""
        batch = generate_synthetic_batch()

        # Rewards should be in [0, 1]
        assert np.all(batch.rewards >= 0)
        assert np.all(batch.rewards <= 1)

    def test_batch_group_structure(self):
        """Test that batch has correct group structure"""
        num_groups = 4
        responses_per_prompt = 3
        batch = generate_synthetic_batch(num_groups, responses_per_prompt)

        # Check group IDs are correct
        expected_group_ids = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3])
        np.testing.assert_array_equal(batch.group_ids, expected_group_ids)


class TestGRPOTrainer:
    """Test GRPO trainer"""

    def test_trainer_initialization(self):
        """Test trainer initialization"""
        config = GRPOConfig(num_groups=8, responses_per_prompt=4)
        trainer = GRPOTrainer(config)

        assert trainer.config == config
        assert len(trainer.training_history) == 0

    def test_compute_advantages_zero_mean(self):
        """Test that advantages have zero mean per group"""
        config = GRPOConfig(num_groups=4, responses_per_prompt=3)
        trainer = GRPOTrainer(config)

        batch = generate_synthetic_batch(
            num_groups=config.num_groups,
            responses_per_prompt=config.responses_per_prompt,
        )

        advantages = trainer.compute_advantages(batch)

        # Check advantages per group sum to ~0
        for g in range(config.num_groups):
            start_idx = g * config.responses_per_prompt
            end_idx = start_idx + config.responses_per_prompt
            group_advantages = advantages[start_idx:end_idx]

            # Sum should be very close to 0
            assert abs(np.sum(group_advantages)) < 1e-6

    def test_compute_advantages_normalized(self):
        """Test normalized advantages"""
        config = GRPOConfig(num_groups=8, responses_per_prompt=4, normalize_advantages=True)
        trainer = GRPOTrainer(config)

        batch = generate_synthetic_batch(
            num_groups=config.num_groups,
            responses_per_prompt=config.responses_per_prompt,
        )

        advantages = trainer.compute_advantages(batch)

        # Overall mean should be ~0 when normalized
        assert abs(np.mean(advantages)) < 1e-6
        # Overall std should be ~1 when normalized
        assert abs(np.std(advantages) - 1.0) < 0.1

    def test_compute_advantages_not_normalized(self):
        """Test un-normalized advantages"""
        config = GRPOConfig(num_groups=8, responses_per_prompt=4, normalize_advantages=False)
        trainer = GRPOTrainer(config)

        batch = generate_synthetic_batch(
            num_groups=config.num_groups,
            responses_per_prompt=config.responses_per_prompt,
        )

        advantages = trainer.compute_advantages(batch)

        # Each group should still have zero mean
        for g in range(config.num_groups):
            start_idx = g * config.responses_per_prompt
            end_idx = start_idx + config.responses_per_prompt
            group_advantages = advantages[start_idx:end_idx]
            assert abs(np.mean(group_advantages)) < 1e-6

    def test_compute_loss(self):
        """Test loss computation"""
        config = GRPOConfig(num_groups=8, responses_per_prompt=4)
        trainer = GRPOTrainer(config)

        batch = generate_synthetic_batch(
            num_groups=config.num_groups,
            responses_per_prompt=config.responses_per_prompt,
        )

        # Compute advantages
        advantages = trainer.compute_advantages(batch)
        batch.advantages = advantages

        # Simulate new log probs
        new_log_probs = batch.log_probs + np.random.normal(0, 0.01, batch.log_probs.shape)

        # Compute loss
        loss_dict = trainer.compute_loss(batch, new_log_probs)

        # Check all loss components present
        assert "total_loss" in loss_dict
        assert "policy_loss" in loss_dict
        assert "entropy" in loss_dict
        assert "entropy_bonus" in loss_dict
        assert "mean_advantage" in loss_dict
        assert "std_advantage" in loss_dict

    def test_train_step(self):
        """Test full training step"""
        config = GRPOConfig(num_groups=8, responses_per_prompt=4)
        trainer = GRPOTrainer(config)

        batch = generate_synthetic_batch(
            num_groups=config.num_groups,
            responses_per_prompt=config.responses_per_prompt,
        )

        # Execute training step
        metrics = trainer.train_step(batch)

        # Check metrics returned
        assert "total_loss" in metrics
        assert "mean_reward" in metrics
        assert "mean_advantage" in metrics

        # Check training history updated
        assert len(trainer.training_history) == 1
        assert trainer.training_history[0] == metrics

    def test_multiple_train_steps(self):
        """Test multiple training steps"""
        config = GRPOConfig(num_groups=8, responses_per_prompt=4)
        trainer = GRPOTrainer(config)

        # Run 5 training steps
        for _ in range(5):
            batch = generate_synthetic_batch(
                num_groups=config.num_groups,
                responses_per_prompt=config.responses_per_prompt,
            )
            trainer.train_step(batch)

        # Check history has 5 entries
        assert len(trainer.training_history) == 5


class TestGRPOUtilities:
    """Test GRPO utility functions"""

    def test_generate_synthetic_batch(self):
        """Test synthetic batch generation"""
        batch = generate_synthetic_batch(num_groups=8, responses_per_prompt=4)

        # Check correct size
        total_responses = 8 * 4
        assert len(batch.prompts) == total_responses
        assert len(batch.responses) == total_responses
        assert batch.rewards.shape == (total_responses,)
        assert batch.log_probs.shape == (total_responses,)
        assert batch.group_ids.shape == (total_responses,)

        # Check rewards are valid
        assert np.all(batch.rewards >= 0)
        assert np.all(batch.rewards <= 1)

    def test_compare_ppo_grpo(self):
        """Test PPO vs GRPO comparison"""
        comparison = compare_ppo_grpo()

        # Check both methods present
        assert "ppo" in comparison
        assert "grpo" in comparison

        # Check PPO details
        ppo = comparison["ppo"]
        assert "components" in ppo
        assert "baseline" in ppo
        assert "advantages" in ppo
        assert "disadvantages" in ppo

        # Check GRPO details
        grpo = comparison["grpo"]
        assert "components" in grpo
        assert "baseline" in grpo
        assert "advantages" in grpo
        assert "disadvantages" in grpo

        # GRPO should be simpler
        assert len(grpo["components"]) < len(ppo["components"])


class TestGRPOScenarios:
    """Test realistic GRPO scenarios"""

    def test_all_same_rewards(self):
        """Test with all same rewards in a group"""
        config = GRPOConfig(num_groups=1, responses_per_prompt=4, normalize_advantages=False)
        trainer = GRPOTrainer(config)

        # Create batch with same rewards
        batch = GRPOBatch(
            prompts=["p1"] * 4,
            responses=["r1", "r2", "r3", "r4"],
            rewards=np.array([0.5, 0.5, 0.5, 0.5]),
            log_probs=np.array([-1.0, -1.0, -1.0, -1.0]),
            group_ids=np.array([0, 0, 0, 0]),
        )

        advantages = trainer.compute_advantages(batch)

        # All advantages should be 0
        np.testing.assert_array_almost_equal(advantages, np.zeros(4))

    def test_clear_winner_in_group(self):
        """Test with clear winner in group"""
        config = GRPOConfig(num_groups=1, responses_per_prompt=4, normalize_advantages=False)
        trainer = GRPOTrainer(config)

        # Create batch with one clear winner
        batch = GRPOBatch(
            prompts=["p1"] * 4,
            responses=["r1", "r2", "r3", "r4"],
            rewards=np.array([1.0, 0.0, 0.0, 0.0]),
            log_probs=np.array([-1.0, -1.0, -1.0, -1.0]),
            group_ids=np.array([0, 0, 0, 0]),
        )

        advantages = trainer.compute_advantages(batch)

        # Winner should have positive advantage
        assert advantages[0] > 0
        # Losers should have negative advantages
        assert np.all(advantages[1:] < 0)
        # Sum should be 0
        assert abs(np.sum(advantages)) < 1e-6

    def test_multiple_groups_different_difficulties(self):
        """Test groups with different base difficulties"""
        config = GRPOConfig(num_groups=3, responses_per_prompt=2, normalize_advantages=False)
        trainer = GRPOTrainer(config)

        # Easy group (high rewards), medium, hard (low rewards)
        batch = GRPOBatch(
            prompts=["easy"] * 2 + ["medium"] * 2 + ["hard"] * 2,
            responses=["r" + str(i) for i in range(6)],
            rewards=np.array(
                [
                    0.9,
                    0.8,  # Easy group
                    0.5,
                    0.4,  # Medium group
                    0.2,
                    0.1,
                ],
            ),  # Hard group
            log_probs=np.ones(6) * -1.0,
            group_ids=np.array([0, 0, 1, 1, 2, 2]),
        )

        advantages = trainer.compute_advantages(batch)

        # Each group should have zero-sum advantages
        group_0_adv = advantages[0:2]
        group_1_adv = advantages[2:4]
        group_2_adv = advantages[4:6]

        assert abs(np.sum(group_0_adv)) < 1e-6
        assert abs(np.sum(group_1_adv)) < 1e-6
        assert abs(np.sum(group_2_adv)) < 1e-6

        # Better response in each group has positive advantage
        assert group_0_adv[0] > group_0_adv[1]
        assert group_1_adv[0] > group_1_adv[1]
        assert group_2_adv[0] > group_2_adv[1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
