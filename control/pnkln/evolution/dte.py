#!/usr/bin/env python3
"""
DTE: Difficulty-Tracking Evolution

Adaptive difficulty management for Agent0 co-evolution.
Implements curriculum learning with dynamic difficulty adjustment.

Based on Agent0 paper (arXiv:2511.16043v1):
- Track success/failure rates per difficulty level
- Adjust difficulty to maximize learning signal
- Prevent stagnation at easy/hard extremes

Part of PNKLN evolution stack.
"""
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DifficultyStrategy(Enum):
    """Strategies for difficulty adjustment."""
    STREAK = "streak"
    WINDOW = "window"
    ADAPTIVE = "adaptive"
    GLICKO = "glicko"


@dataclass
class DifficultyLevel:
    """Statistics for a single difficulty level."""
    level: int
    attempts: int = 0
    successes: int = 0
    failures: int = 0
    avg_confidence: float = 0.0
    last_attempt: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        if self.attempts == 0:
            return 0.0
        return self.successes / self.attempts

    @property
    def mastery_score(self) -> float:
        if self.attempts == 0:
            return 0.0
        return min(self.success_rate * math.sqrt(self.attempts / 10), 1.0)


@dataclass
class EvolutionMetrics:
    """Metrics for the entire evolution process."""
    total_iterations: int = 0
    current_difficulty: int = 1
    max_difficulty_reached: int = 1
    difficulty_changes: int = 0
    total_successes: int = 0
    total_failures: int = 0
    levels: Dict[int, DifficultyLevel] = field(default_factory=dict)

    def __post_init__(self):
        for i in range(1, 11):
            if i not in self.levels:
                self.levels[i] = DifficultyLevel(level=i)


class DifficultyTracker:
    """Tracks and adjusts difficulty for Agent0 evolution."""

    TARGET_LOW = 0.60
    TARGET_HIGH = 0.85
    TARGET_OPTIMAL = 0.75

    def __init__(
        self,
        strategy: DifficultyStrategy = DifficultyStrategy.ADAPTIVE,
        min_difficulty: int = 1,
        max_difficulty: int = 10,
        streak_threshold: int = 3,
        window_size: int = 10
    ):
        self.strategy = strategy
        self.min_difficulty = min_difficulty
        self.max_difficulty = max_difficulty
        self.streak_threshold = streak_threshold
        self.window_size = window_size
        self.metrics = EvolutionMetrics()
        self.recent_outcomes: List[bool] = []
        self.streak_count = 0
        self.streak_type: Optional[bool] = None
        print(f"///▞ DTE :: Strategy: {strategy.value}")

    def record_outcome(self, success: bool, confidence: float = 0.0) -> int:
        """Record outcome and return next difficulty level."""
        self.metrics.total_iterations += 1
        level = self.metrics.levels[self.metrics.current_difficulty]
        level.attempts += 1
        level.last_attempt = datetime.now()
        if success:
            level.successes += 1
            self.metrics.total_successes += 1
        else:
            level.failures += 1
            self.metrics.total_failures += 1
        level.avg_confidence = ((level.avg_confidence * (level.attempts - 1) + confidence) / level.attempts)
        self.recent_outcomes.append(success)
        if len(self.recent_outcomes) > self.window_size:
            self.recent_outcomes.pop(0)
        if self.streak_type == success:
            self.streak_count += 1
        else:
            self.streak_type = success
            self.streak_count = 1
        next_difficulty = self._calculate_next_difficulty()
        if next_difficulty != self.metrics.current_difficulty:
            self.metrics.difficulty_changes += 1
            self.metrics.current_difficulty = next_difficulty
            self.metrics.max_difficulty_reached = max(self.metrics.max_difficulty_reached, next_difficulty)
            self.streak_count = 0
        return next_difficulty

    def _calculate_next_difficulty(self) -> int:
        if self.strategy == DifficultyStrategy.STREAK:
            return self._streak_strategy()
        elif self.strategy == DifficultyStrategy.WINDOW:
            return self._window_strategy()
        elif self.strategy == DifficultyStrategy.ADAPTIVE:
            return self._adaptive_strategy()
        return self.metrics.current_difficulty

    def _streak_strategy(self) -> int:
        current = self.metrics.current_difficulty
        if self.streak_count >= self.streak_threshold:
            if self.streak_type:
                return min(current + 1, self.max_difficulty)
            else:
                return max(current - 1, self.min_difficulty)
        return current

    def _window_strategy(self) -> int:
        current = self.metrics.current_difficulty
        if len(self.recent_outcomes) < self.window_size // 2:
            return current
        success_rate = sum(self.recent_outcomes) / len(self.recent_outcomes)
        if success_rate > self.TARGET_HIGH:
            return min(current + 1, self.max_difficulty)
        elif success_rate < self.TARGET_LOW:
            return max(current - 1, self.min_difficulty)
        return current

    def _adaptive_strategy(self) -> int:
        current = self.metrics.current_difficulty
        level = self.metrics.levels[current]
        if level.attempts < 3:
            return current
        p = level.success_rate
        n = level.attempts
        z = 1.96
        denominator = 1 + z * z / n
        center = (p + z * z / (2 * n)) / denominator
        margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denominator
        lower_bound = center - margin
        upper_bound = center + margin
        if lower_bound > self.TARGET_HIGH:
            return min(current + 1, self.max_difficulty)
        elif upper_bound < self.TARGET_LOW:
            return max(current - 1, self.min_difficulty)
        elif center > self.TARGET_OPTIMAL and level.attempts >= 10:
            return min(current + 1, self.max_difficulty)
        elif center < self.TARGET_OPTIMAL - 0.1 and level.attempts >= 10:
            return max(current - 1, self.min_difficulty)
        return current

    def get_metrics(self) -> Dict:
        return {
            "strategy": self.strategy.value,
            "current_difficulty": self.metrics.current_difficulty,
            "max_difficulty_reached": self.metrics.max_difficulty_reached,
            "total_iterations": self.metrics.total_iterations,
            "success_rate": self.metrics.total_successes / max(self.metrics.total_iterations, 1),
            "difficulty_changes": self.metrics.difficulty_changes
        }
