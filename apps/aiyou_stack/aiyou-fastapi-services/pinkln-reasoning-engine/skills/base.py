"""
Base Skill class for Pinkln reasoning skills

All skills have:
- Glicko-2 rating (performance-based)
- Benchmark results (HumanEval, BigCodeBench, SWE-bench)
- DTE evolution history
- CheatSheet integration
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..ranking.glicko2 import Glicko2Rating, update_rating


@dataclass
class SkillResult:
    """Result from skill execution"""

    output: str
    reasoning_trace: list[str]
    confidence: float  # 0-1
    tokens_used: int
    latency_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkScore:
    """Benchmark performance for a skill"""

    suite: str  # "HumanEval", "BigCodeBench", "SWE-bench"
    score: float  # 0-1 (percentage correct)
    timestamp: datetime
    details: dict[str, Any] = field(default_factory=dict)


class Skill:
    """
    Base class for all Pinkln reasoning skills

    Skills are reusable reasoning patterns (CoT, ToT, RCR, etc.)
    that can be:
    - Rated via Glicko-2
    - Benchmarked
    - Evolved via DTE
    - Combined with CheatSheets
    """

    def __init__(
        self,
        name: str,
        description: str,
        initial_rating: float = 1500.0,
        cheatsheet: str | None = None,
    ):
        self.name = name
        self.description = description

        # Glicko-2 rating
        self.rating = Glicko2Rating(
            mu=initial_rating,
            phi=350.0,
            sigma=0.06,  # Moderate uncertainty  # Low volatility
        )

        # CheatSheet integration
        self.cheatsheet = cheatsheet

        # Benchmark history
        self.benchmarks: list[BenchmarkScore] = []

        # DTE evolution
        self.evolution_history: list[dict[str, Any]] = []

        # Usage stats
        self.total_uses = 0
        self.successful_uses = 0

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> SkillResult:
        """
        Execute this skill on a task

        Must be implemented by subclasses
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement execute()")

    def update_rating_from_benchmark(self, benchmark: BenchmarkScore):
        """
        Update Glicko rating based on benchmark performance

        Treats benchmark as a match against a standardized opponent:
        - Benchmark score 1.0 (100%) → Rating 2000
        - Benchmark score 0.5 (50%) → Rating 1500
        - Benchmark score 0.0 (0%) → Rating 1000
        """
        # Map benchmark score to opponent rating
        opponent_rating_value = 1000 + (benchmark.score * 1000)
        opponent = Glicko2Rating(mu=opponent_rating_value, phi=200.0, sigma=0.06)

        # Map score to game result (0 = loss, 0.5 = draw, 1 = win)
        # Use sigmoid to convert: score 0.6 → result 0.7, score 0.4 → result 0.3
        result = 1.0 / (1.0 + 10 ** ((1500 - opponent_rating_value) / 400))

        # Update rating
        self.rating = update_rating(
            player=self.rating,
            opponents=[opponent],
            results=[result],
            tau=0.5,  # Standard volatility
            tol=1e-6,  # Tight convergence
        )

        # Store benchmark
        self.benchmarks.append(benchmark)

    def get_benchmark_avg(self, suite: str | None = None) -> float:
        """
        Get average benchmark score

        Args:
            suite: Filter by benchmark suite (optional)

        Returns:
            Average score (0-1)
        """
        filtered = [b for b in self.benchmarks if b.suite == suite] if suite else self.benchmarks

        if not filtered:
            return 0.0

        return sum(b.score for b in filtered) / len(filtered)

    def get_conservative_rating(self) -> float:
        """
        Get conservative rating estimate (μ - 2σ)

        Used for ranking when uncertainty is high
        """
        return self.rating.mu - 2 * self.rating.phi

    def record_use(self, success: bool):
        """Record skill usage for stats"""
        self.total_uses += 1
        if success:
            self.successful_uses += 1

    def success_rate(self) -> float:
        """Get success rate (0-1)"""
        if self.total_uses == 0:
            return 0.0
        return self.successful_uses / self.total_uses

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict"""
        return {
            "name": self.name,
            "description": self.description,
            "rating": {
                "mu": self.rating.mu,
                "phi": self.rating.phi,
                "sigma": self.rating.sigma,
                "conservative": self.get_conservative_rating(),
            },
            "benchmarks": {
                "average": self.get_benchmark_avg(),
                "count": len(self.benchmarks),
                "by_suite": {
                    suite: self.get_benchmark_avg(suite)
                    for suite in set(b.suite for b in self.benchmarks)
                },
            },
            "usage": {
                "total": self.total_uses,
                "successful": self.successful_uses,
                "success_rate": self.success_rate(),
            },
            "evolution": {"iterations": len(self.evolution_history)},
        }

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"name='{self.name}' "
            f"rating={self.rating.mu:.0f}±{self.rating.phi:.0f} "
            f"benchmarks={len(self.benchmarks)} "
            f"uses={self.total_uses}>"
        )
