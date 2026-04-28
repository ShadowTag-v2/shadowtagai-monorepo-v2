#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Ensemble Distillation for Flying n-autoresearch/Kosmos/BioAgents swarm.
Implements CIKD pattern: score → elect best → distill → repeat.
Based on Hong et al., NeurIPS 2019 Deep RL Workshop.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np


@dataclass
class EnsembleMember:
    """A member of the ensemble (squad-level agent)."""

    member_id: int
    name: str

    # Performance metrics
    avg_latency_ms: float = 100.0
    success_rate: float = 0.95
    avg_cost: float = 1.0
    task_throughput: int = 0

    # Learnable state (patterns that can be distilled)
    pheromone_trail: np.ndarray = field(default_factory=lambda: np.ones((25, 25)))
    routing_weights: np.ndarray = field(default_factory=lambda: np.ones(24) / 24)
    exploration_rate: float = 0.1

    # History
    score_history: list[float] = field(default_factory=list)
    was_teacher: int = 0

    def compute_score(self, weights: dict[str, float] = None) -> float:
        """Compute composite performance score."""
        if weights is None:
            weights = {"speed": 0.4, "quality": 0.3, "efficiency": 0.2, "volume": 0.1}

        score = (
            weights["speed"] * (1 / max(self.avg_latency_ms, 1)) * 1000
            + weights["quality"] * self.success_rate
            + weights["efficiency"] * (1 / max(self.avg_cost, 0.01))
            + weights["volume"] * min(self.task_throughput / 100, 1.0)
        )

        self.score_history.append(score)
        return score


class EnsembleDistillation:
    """CIKD-style ensemble learning for 600-agent swarm.

    Core loop:
    1. Score all ensemble members
    2. Elect best as teacher
    3. Distill teacher's patterns to students
    4. Repeat

    Treats 24 squads as ensemble members.
    """

    def __init__(
        self,
        num_members: int = 24,
        distillation_alpha: float = 0.3,
        exploration_boost: float = 1.1,
        score_window: int = 100,
    ):
        """Initialize ensemble distillation.

        Args:
            num_members: Number of ensemble members (squads)
            distillation_alpha: Strength of distillation (0 = no change, 1 = full copy)
            exploration_boost: Multiplier for exploration after distillation
            score_window: Rolling window for score averaging

        """
        self.num_members = num_members
        self.alpha = distillation_alpha
        self.exploration_boost = exploration_boost
        self.score_window = score_window

        # Initialize ensemble
        self.members = self._init_members()
        self.teacher_id: int | None = None
        self.cycle_count = 0
        self.history: list[dict] = []

    def _init_members(self) -> list[EnsembleMember]:
        """Initialize ensemble members with diverse starting points."""
        members = []
        for i in range(self.num_members):
            # Diverse initialization
            members.append(
                EnsembleMember(
                    member_id=i,
                    name=f"Squad-{i:02d}",
                    avg_latency_ms=np.random.uniform(50, 150),
                    success_rate=np.random.uniform(0.85, 0.99),
                    avg_cost=np.random.uniform(0.5, 2.0),
                    task_throughput=np.random.randint(10, 100),
                    pheromone_trail=np.random.uniform(0.5, 1.5, (25, 25)),
                    routing_weights=np.random.dirichlet(np.ones(24)),
                    exploration_rate=np.random.uniform(0.05, 0.15),
                ),
            )
        return members

    def score_all(self, weights: dict[str, float] = None) -> list[tuple[int, float]]:
        """Score all ensemble members.

        Returns:
            List of (member_id, score) tuples, sorted by score descending

        """
        scores = []
        for member in self.members:
            score = member.compute_score(weights)
            scores.append((member.member_id, score))

        return sorted(scores, key=lambda x: x[1], reverse=True)

    def elect_teacher(self, scores: list[tuple[int, float]] = None) -> int:
        """Elect best-performing member as teacher.

        Uses rolling window of scores for stability.
        """
        if scores is None:
            scores = self.score_all()

        # Simple: best current score
        # Advanced: consider stability over window
        if len(self.members[0].score_history) >= 3:
            # Use average of last 3 scores for stability
            avg_scores = []
            for member in self.members:
                recent = member.score_history[-3:]
                avg_scores.append((member.member_id, np.mean(recent)))
            avg_scores.sort(key=lambda x: x[1], reverse=True)
            self.teacher_id = avg_scores[0][0]
        else:
            self.teacher_id = scores[0][0]

        self.members[self.teacher_id].was_teacher += 1
        return self.teacher_id

    def distill(self, teacher_id: int = None):
        """Distill teacher's knowledge to all students.

        Soft alignment: students move toward teacher while retaining exploration.
        """
        if teacher_id is None:
            teacher_id = self.teacher_id

        teacher = self.members[teacher_id]

        for member in self.members:
            if member.member_id == teacher_id:
                continue  # Teacher doesn't distill to itself

            # Distill pheromone trails
            member.pheromone_trail = (
                1 - self.alpha
            ) * member.pheromone_trail + self.alpha * teacher.pheromone_trail

            # Distill routing weights
            member.routing_weights = (
                1 - self.alpha
            ) * member.routing_weights + self.alpha * teacher.routing_weights

            # Boost exploration to maintain diversity
            member.exploration_rate = min(
                member.exploration_rate * self.exploration_boost,
                0.3,  # Cap at 30%
            )

    def run_cycle(self, weights: dict[str, float] = None) -> dict:
        """Run one complete CIKD cycle: score → elect → distill.

        Returns:
            Cycle summary with metrics

        """
        start = time.time()
        self.cycle_count += 1

        # Score all members
        scores = self.score_all(weights)

        # Elect teacher
        teacher_id = self.elect_teacher(scores)

        # Compute ensemble metrics before distillation
        all_scores = [s[1] for s in scores]
        variance_before = np.var(all_scores)

        # Distill
        self.distill(teacher_id)

        # Record cycle
        cycle_summary = {
            "cycle": self.cycle_count,
            "teacher_id": teacher_id,
            "teacher_name": self.members[teacher_id].name,
            "teacher_score": scores[0][1],
            "mean_score": np.mean(all_scores),
            "score_variance": variance_before,
            "score_range": scores[0][1] - scores[-1][1],
            "duration_ms": (time.time() - start) * 1000,
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.history.append(cycle_summary)
        return cycle_summary

    def get_ensemble_health(self) -> dict:
        """Get ensemble health metrics.

        Healthy ensemble:
        - Teacher changes occasionally
        - Variance decreases but never hits zero
        - All members still exploring
        """
        if len(self.history) < 2:
            return {"status": "initializing", "cycles": len(self.history)}

        recent = self.history[-10:]

        # Teacher stability (how often does teacher change?)
        teachers = [h["teacher_id"] for h in recent]
        unique_teachers = len(set(teachers))
        teacher_stability = 1 - (unique_teachers - 1) / len(recent)

        # Convergence rate
        variances = [h["score_variance"] for h in recent]
        convergence_rate = (variances[0] - variances[-1]) / max(variances[0], 0.001)

        # Exploration diversity
        exploration_rates = [m.exploration_rate for m in self.members]
        exploration_diversity = np.std(exploration_rates)

        return {
            "status": "healthy" if 0.3 < teacher_stability < 0.9 else "needs_attention",
            "cycles": len(self.history),
            "teacher_stability": teacher_stability,
            "convergence_rate": convergence_rate,
            "exploration_diversity": exploration_diversity,
            "mean_exploration": np.mean(exploration_rates),
            "current_teacher": self.teacher_id,
            "teacher_tenure": self.members[self.teacher_id].was_teacher if self.teacher_id else 0,
        }

    def emergency_distillation(self):
        """Emergency distillation: align all to most stable member.

        Triggered by kill conditions in running_estimate.
        """
        # Find most stable member (lowest variance in recent scores)
        stabilities = []
        for member in self.members:
            if len(member.score_history) >= 3:
                variance = np.var(member.score_history[-10:])
                stabilities.append((member.member_id, variance))

        if not stabilities:
            return

        # Sort by lowest variance (most stable)
        stabilities.sort(key=lambda x: x[1])
        stable_id = stabilities[0][0]

        # High-alpha distillation for emergency
        old_alpha = self.alpha
        self.alpha = 0.7  # Strong alignment
        self.distill(stable_id)
        self.alpha = old_alpha

    def update_member_metrics(
        self,
        member_id: int,
        latency_ms: float = None,
        success_rate: float = None,
        cost: float = None,
        throughput: int = None,
    ):
        """Update metrics for a specific member."""
        member = self.members[member_id]
        if latency_ms is not None:
            member.avg_latency_ms = 0.9 * member.avg_latency_ms + 0.1 * latency_ms
        if success_rate is not None:
            member.success_rate = 0.9 * member.success_rate + 0.1 * success_rate
        if cost is not None:
            member.avg_cost = 0.9 * member.avg_cost + 0.1 * cost
        if throughput is not None:
            member.task_throughput = throughput

    def get_member_rankings(self) -> list[dict]:
        """Get current rankings of all members."""
        scores = self.score_all()
        rankings = []
        for rank, (member_id, score) in enumerate(scores):
            member = self.members[member_id]
            rankings.append(
                {
                    "rank": rank + 1,
                    "member_id": member_id,
                    "name": member.name,
                    "score": score,
                    "latency_ms": member.avg_latency_ms,
                    "success_rate": member.success_rate,
                    "exploration_rate": member.exploration_rate,
                    "times_teacher": member.was_teacher,
                },
            )
        return rankings


def main():
    """Demo of ensemble distillation."""
    print("///▞ Initializing ensemble with 24 members...")
    ensemble = EnsembleDistillation(num_members=24)

    print("///▞ Running 10 CIKD cycles...")
    for _i in range(10):
        # Simulate performance variations
        for member in ensemble.members:
            member.avg_latency_ms += np.random.uniform(-10, 10)
            member.avg_latency_ms = max(10, member.avg_latency_ms)
            member.success_rate += np.random.uniform(-0.02, 0.02)
            member.success_rate = np.clip(member.success_rate, 0.5, 1.0)
            member.task_throughput += np.random.randint(-5, 10)

        result = ensemble.run_cycle()
        print(
            f"    Cycle {result['cycle']}: Teacher={result['teacher_name']}, "
            f"Score={result['teacher_score']:.3f}, Var={result['score_variance']:.4f}",
        )

    # Get health
    health = ensemble.get_ensemble_health()
    print(f"\n///▞ Ensemble Health: {health['status']}")
    print(f"    Teacher stability: {health['teacher_stability']:.2f}")
    print(f"    Convergence rate: {health['convergence_rate']:.2f}")
    print(f"    Mean exploration: {health['mean_exploration']:.3f}")

    # Get rankings
    print("\n///▞ Top 5 Members:")
    rankings = ensemble.get_member_rankings()
    for r in rankings[:5]:
        print(f"    #{r['rank']} {r['name']}: score={r['score']:.3f}, teacher×{r['times_teacher']}")


if __name__ == "__main__":
    main()
