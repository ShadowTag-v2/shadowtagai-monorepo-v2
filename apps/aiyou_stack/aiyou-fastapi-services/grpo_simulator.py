"""
GRPO (Group Relative Policy Optimization) Simulator

Demonstrates key concepts of GRPO:
1. Generate groups of trajectories (not single trajectories)
2. Rank trajectories by relative performance
3. Optimize policy over the group (not individuals)
4. Maintain entropy (prevent collapse to single solution)

Use cases:
- Preference learning (RLHF-style training)
- Ranking tasks (search results, recommendations)
- Multi-objective optimization
- Avoiding entropy collapse in RL training

References:
- GRPO builds on PPO but optimizes over sets of trajectories
- Prevents mode collapse via entropy regularization
- 2.5× faster convergence than standard PPO (per GAIN-RL research)
"""

import math
import random
import statistics
from dataclasses import dataclass


@dataclass
class Trajectory:
    """Represents a trajectory (sequence of actions)."""

    actions: list[int]  # Sequence of actions taken
    reward: float  # Total reward obtained
    log_prob: float  # Log probability under current policy

    def __repr__(self):
        return f"Trajectory(actions={self.actions}, reward={self.reward:.2f}, log_prob={self.log_prob:.3f})"


class GRPOSimulator:
    """
    Simplified GRPO simulator for educational/demo purposes.

    Simulates training a policy that learns to solve a simple task:
    - Task: Select sequence of numbers that sum to a target
    - Policy: Probability distribution over numbers [0-9]
    - GRPO: Generate groups of trajectories, rank them, optimize distribution
    """

    def __init__(
        self,
        target_sum: int = 15,
        trajectory_length: int = 5,
        group_size: int = 8,
        entropy_weight: float = 0.1,
        learning_rate: float = 0.1,
    ):
        """
        Initialize GRPO simulator.

        Args:
            target_sum: Target sum for the sequence
            trajectory_length: Number of actions per trajectory
            group_size: Number of trajectories to generate per group
            entropy_weight: Weight for entropy regularization (prevents collapse)
            learning_rate: Policy update step size
        """
        self.target_sum = target_sum
        self.trajectory_length = trajectory_length
        self.group_size = group_size
        self.entropy_weight = entropy_weight
        self.learning_rate = learning_rate

        # Policy: probability distribution over actions [0-9]
        # Start with uniform distribution
        self.policy = [1 / 10 for _ in range(10)]

    def _sample_action(self) -> tuple[int, float]:
        """
        Sample action from current policy.

        Returns:
            (action, log_prob): Sampled action and its log probability
        """
        action = random.choices(range(10), weights=self.policy)[0]
        log_prob = math.log(self.policy[action] + 1e-8)  # Add epsilon to avoid log(0)
        return action, log_prob

    def _compute_reward(self, actions: list[int]) -> float:
        """
        Compute reward for a trajectory.

        Reward = -|sum(actions) - target_sum|
        (Closer to target = higher reward)

        Args:
            actions: Sequence of actions

        Returns:
            Reward (higher is better)
        """
        total = sum(actions)
        distance = abs(total - self.target_sum)
        return -distance

    def generate_trajectory(self) -> Trajectory:
        """
        Generate a single trajectory by sampling from current policy.

        Returns:
            Trajectory with actions, reward, and log probability
        """
        actions = []
        log_prob_total = 0

        for _ in range(self.trajectory_length):
            action, log_prob = self._sample_action()
            actions.append(action)
            log_prob_total += log_prob

        reward = self._compute_reward(actions)

        return Trajectory(actions=actions, reward=reward, log_prob=log_prob_total)

    def generate_group(self) -> list[Trajectory]:
        """
        Generate a group of trajectories.

        Returns:
            List of trajectories
        """
        return [self.generate_trajectory() for _ in range(self.group_size)]

    def rank_trajectories(self, trajectories: list[Trajectory]) -> list[tuple[Trajectory, float]]:
        """
        Rank trajectories by reward (relative comparison).

        Assigns relative rewards:
        - Best trajectory: +1
        - Worst trajectory: -1
        - Middle trajectories: Linear interpolation

        Args:
            trajectories: List of trajectories to rank

        Returns:
            List of (trajectory, relative_reward) pairs
        """
        # Sort by reward (descending)
        sorted_traj = sorted(trajectories, key=lambda t: t.reward, reverse=True)

        # Assign relative rewards
        n = len(sorted_traj)
        ranked = []
        for i, traj in enumerate(sorted_traj):
            # Linear interpolation from +1 (best) to -1 (worst)
            relative_reward = 1 - 2 * i / (n - 1) if n > 1 else 0
            ranked.append((traj, relative_reward))

        return ranked

    def _compute_entropy(self) -> float:
        """
        Compute entropy of current policy.

        H(policy) = -Σ p(a) log p(a)

        Higher entropy = more diverse/exploratory
        Lower entropy = more deterministic/exploitative

        Returns:
            Entropy of policy
        """
        return -sum(p * math.log(p + 1e-8) for p in self.policy)

    def update_policy(self, ranked_trajectories: list[tuple[Trajectory, float]]):
        """
        Update policy based on ranked trajectories.

        GRPO key idea:
        1. Increase probability of actions in high-reward trajectories
        2. Decrease probability of actions in low-reward trajectories
        3. Apply entropy regularization to prevent collapse

        Args:
            ranked_trajectories: List of (trajectory, relative_reward) pairs
        """
        # Accumulate policy gradients
        policy_gradients = [0.0 for _ in range(10)]

        for traj, relative_reward in ranked_trajectories:
            # For each action in trajectory
            for action in traj.actions:
                # Gradient = relative_reward (higher reward → increase prob)
                policy_gradients[action] += relative_reward

        # Normalize gradients
        total_grad = sum(abs(g) for g in policy_gradients)
        if total_grad > 0:
            policy_gradients = [g / total_grad for g in policy_gradients]

        # Compute entropy before update
        entropy_before = self._compute_entropy()

        # Update policy (gradient ascent)
        new_policy = []
        for i in range(10):
            # Update: p(a) ← p(a) + lr * gradient
            new_prob = self.policy[i] + self.learning_rate * policy_gradients[i]

            # Add entropy bonus (prevents collapse)
            # If policy getting too peaked, push towards uniform
            entropy_bonus = self.entropy_weight * (1 / 10 - new_prob)
            new_prob += entropy_bonus

            # Clip to valid probability range
            new_prob = max(0.01, min(0.99, new_prob))
            new_policy.append(new_prob)

        # Normalize to ensure valid probability distribution
        total = sum(new_policy)
        self.policy = [p / total for p in new_policy]

        # Compute entropy after update
        entropy_after = self._compute_entropy()

        return {
            "entropy_before": entropy_before,
            "entropy_after": entropy_after,
            "entropy_change": entropy_after - entropy_before,
        }

    def train(self, num_iterations: int = 100, verbose: bool = True) -> dict:
        """
        Train policy using GRPO.

        Args:
            num_iterations: Number of training iterations
            verbose: Print progress

        Returns:
            Training history
        """
        history = {"avg_reward": [], "best_reward": [], "entropy": [], "policy_snapshots": []}

        if verbose:
            print("=== GRPO Training ===")
            print(f"Target sum: {self.target_sum}")
            print(f"Trajectory length: {self.trajectory_length}")
            print(f"Group size: {self.group_size}")
            print(f"Entropy weight: {self.entropy_weight}")
            print(f"Learning rate: {self.learning_rate}\n")

        for iteration in range(num_iterations):
            # 1. Generate group of trajectories
            group = self.generate_group()

            # 2. Rank trajectories
            ranked = self.rank_trajectories(group)

            # 3. Update policy
            entropy_info = self.update_policy(ranked)

            # Track metrics
            avg_reward = statistics.mean([t.reward for t in group])
            best_reward = max([t.reward for t in group])
            entropy = entropy_info["entropy_after"]

            history["avg_reward"].append(avg_reward)
            history["best_reward"].append(best_reward)
            history["entropy"].append(entropy)

            # Snapshot policy every 10 iterations
            if iteration % 10 == 0:
                history["policy_snapshots"].append(self.policy.copy())

            # Print progress
            if verbose and iteration % 20 == 0:
                print(
                    f"Iter {iteration:3d} | "
                    f"Avg Reward: {avg_reward:6.2f} | "
                    f"Best: {best_reward:6.2f} | "
                    f"Entropy: {entropy:.3f}"
                )

                # Show example trajectory
                best_traj = max(group, key=lambda t: t.reward)
                print(
                    f"         Best trajectory: {best_traj.actions} → sum={sum(best_traj.actions)}\n"
                )

        if verbose:
            print("\n=== Training Complete ===")
            print(f"Final avg reward: {history['avg_reward'][-1]:.2f}")
            print(f"Final best reward: {history['best_reward'][-1]:.2f}")
            print(f"Final entropy: {history['entropy'][-1]:.3f}")
            print("\nLearned policy distribution:")
            for i, prob in enumerate(self.policy):
                bar = "#" * int(prob * 50)
                print(f"Action {i}: {prob:5.3f} {bar}")

        return history

    def compare_to_ppo(self, num_iterations: int = 100) -> dict:
        """
        Compare GRPO to PPO-style single-trajectory optimization.

        Returns:
            Comparison metrics
        """
        print("\n=== GRPO vs PPO Comparison ===\n")

        # GRPO training
        print("Training with GRPO (group optimization)...")
        self.policy.copy()
        grpo_history = self.train(num_iterations, verbose=False)

        # Reset policy
        self.policy = [1 / 10 for _ in range(10)]

        # PPO-style training (single trajectory per iteration)
        print("Training with PPO (single trajectory)...")
        ppo_history = {"avg_reward": [], "best_reward": [], "entropy": []}

        for _iteration in range(num_iterations):
            # Generate single trajectory (PPO-style)
            traj = self.generate_trajectory()

            # Rank (trivial for single trajectory)
            ranked = [(traj, 1.0)]  # Single trajectory always gets +1

            # Update policy
            entropy_info = self.update_policy(ranked)

            # Track metrics (average over group for fair comparison)
            test_group = self.generate_group()
            avg_reward = statistics.mean([t.reward for t in test_group])
            best_reward = max([t.reward for t in test_group])

            ppo_history["avg_reward"].append(avg_reward)
            ppo_history["best_reward"].append(best_reward)
            ppo_history["entropy"].append(entropy_info["entropy_after"])

        # Compare final performance
        print("\n=== Results ===\n")
        print(f"GRPO final avg reward: {grpo_history['avg_reward'][-1]:.2f}")
        print(f"PPO  final avg reward: {ppo_history['avg_reward'][-1]:.2f}")
        print(
            f"GRPO advantage: {grpo_history['avg_reward'][-1] - ppo_history['avg_reward'][-1]:.2f}\n"
        )

        print(f"GRPO final entropy: {grpo_history['entropy'][-1]:.3f}")
        print(f"PPO  final entropy: {ppo_history['entropy'][-1]:.3f}")
        print(
            f"GRPO maintains {grpo_history['entropy'][-1] / ppo_history['entropy'][-1]:.2f}× more diversity\n"
        )

        # Compute convergence speed (iterations to reach 90% of final performance)
        def iterations_to_threshold(history, threshold_pct=0.9):
            target = history[-1] * threshold_pct
            for i, reward in enumerate(history):
                if reward >= target:
                    return i
            return len(history)

        grpo_conv = iterations_to_threshold(grpo_history["avg_reward"])
        ppo_conv = iterations_to_threshold(ppo_history["avg_reward"])

        print(f"GRPO converged in: {grpo_conv} iterations")
        print(f"PPO  converged in: {ppo_conv} iterations")
        print(f"GRPO is {ppo_conv / grpo_conv:.2f}× faster to converge\n")

        return {
            "grpo": grpo_history,
            "ppo": ppo_history,
            "grpo_advantage": grpo_history["avg_reward"][-1] - ppo_history["avg_reward"][-1],
            "convergence_speedup": ppo_conv / grpo_conv,
        }


# Example usage and demonstrations
if __name__ == "__main__":
    random.seed(42)  # For reproducibility

    # Demo 1: Basic GRPO training
    print("=== Demo 1: Basic GRPO Training ===\n")
    simulator = GRPOSimulator(
        target_sum=15, trajectory_length=5, group_size=8, entropy_weight=0.1, learning_rate=0.1
    )

    history = simulator.train(num_iterations=100, verbose=True)

    # Demo 2: GRPO vs PPO comparison
    print("\n" + "=" * 60 + "\n")
    simulator2 = GRPOSimulator(
        target_sum=20, trajectory_length=6, group_size=10, entropy_weight=0.15, learning_rate=0.08
    )

    comparison = simulator2.compare_to_ppo(num_iterations=100)

    # Demo 3: Effect of entropy weight
    print("\n" + "=" * 60)
    print("\n=== Demo 3: Effect of Entropy Weight ===\n")

    entropy_weights = [0.0, 0.05, 0.15, 0.3]
    results = {}

    for ew in entropy_weights:
        sim = GRPOSimulator(
            target_sum=15, trajectory_length=5, group_size=8, entropy_weight=ew, learning_rate=0.1
        )
        hist = sim.train(num_iterations=50, verbose=False)
        results[ew] = {"final_reward": hist["avg_reward"][-1], "final_entropy": hist["entropy"][-1]}

    print("Entropy Weight | Final Reward | Final Entropy | Interpretation")
    print("-" * 70)
    for ew in entropy_weights:
        r = results[ew]
        interp = (
            "Collapsed!"
            if r["final_entropy"] < 1.0
            else "Low diversity"
            if r["final_entropy"] < 1.5
            else "Good diversity"
            if r["final_entropy"] < 2.0
            else "High diversity"
        )
        print(f"{ew:14.2f} | {r['final_reward']:12.2f} | {r['final_entropy']:13.3f} | {interp}")

    print("\n✅ Key insight: Higher entropy weight → more diversity → prevents collapse")
    print("✅ GRPO simulator implementation complete\n")
