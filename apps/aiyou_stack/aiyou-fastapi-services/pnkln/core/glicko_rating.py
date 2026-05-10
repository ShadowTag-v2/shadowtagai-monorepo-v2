"""Glicko-2 Rating Engine for Agent Performance Tracking

Implements the Glicko-2 rating system (ELO evolution) for tracking agent performance
over time. Used by MAD Orchestrator and other Track B components.

Key Features:
- Rating (r): Base rating value (default 1500)
- Rating Deviation (RD): Uncertainty in rating (default 350)
- Volatility (σ): Consistency of performance (default 0.06)
- tol=1e-6: Convergence parameter for volatility calculation
- <100μs rating update target
- Historical tracking: 100K+ matches
- Ranking accuracy: ≥95% (vs true skill)

References:
- Glickman, M. E. (2001). "Dynamic paired comparison models with stochastic variances"
- http://www.glicko.net/glicko/glicko2.pdf

"""

import math
import time
from dataclasses import dataclass, field
from enum import Enum


class MatchOutcome(Enum):
    """Match outcome from perspective of player 1."""

    WIN = 1.0
    DRAW = 0.5
    LOSS = 0.0


@dataclass
class GlickoRating:
    """Glicko-2 rating representation.

    Attributes:
        rating: Rating value (μ in Glicko-2 scale, default 1500)
        rd: Rating Deviation - uncertainty (φ in Glicko-2 scale, default 350)
        volatility: Volatility - consistency (σ, default 0.06)
        matches_played: Total matches played
        last_update_timestamp: Unix timestamp of last update

    """

    rating: float = 1500.0
    rd: float = 350.0
    volatility: float = 0.06
    matches_played: int = 0
    last_update_timestamp: float = field(default_factory=time.time)

    def to_glicko2_scale(self) -> tuple[float, float]:
        """Convert rating and RD to Glicko-2 scale (μ, φ)."""
        mu = (self.rating - 1500.0) / 173.7178
        phi = self.rd / 173.7178
        return (mu, phi)

    @staticmethod
    def from_glicko2_scale(
        mu: float,
        phi: float,
        volatility: float,
        matches_played: int = 0,
    ) -> "GlickoRating":
        """Convert from Glicko-2 scale to standard rating."""
        rating = mu * 173.7178 + 1500.0
        rd = phi * 173.7178
        return GlickoRating(
            rating=rating,
            rd=rd,
            volatility=volatility,
            matches_played=matches_played,
            last_update_timestamp=time.time(),
        )


@dataclass
class Match:
    """Single match result.

    Attributes:
        opponent_rating: Opponent's Glicko rating
        outcome: Match outcome (WIN/DRAW/LOSS from player's perspective)
        timestamp: Unix timestamp of match

    """

    opponent_rating: GlickoRating
    outcome: MatchOutcome
    timestamp: float = field(default_factory=time.time)


@dataclass
class RatingUpdate:
    """Rating update result.

    Attributes:
        old_rating: Rating before update
        new_rating: Rating after update
        execution_time_us: Execution time in microseconds
        matches_processed: Number of matches processed

    """

    old_rating: GlickoRating
    new_rating: GlickoRating
    execution_time_us: float
    matches_processed: int


class GlickoEngine:
    """Glicko-2 rating engine for agent performance tracking.

    Performance target: <100μs per rating update
    Historical capacity: 100K+ matches
    Ranking accuracy: ≥95% (vs true skill)
    """

    # Glicko-2 system constants
    TAU = 0.5  # System constant (constrains volatility changes)
    EPSILON = 1e-6  # Convergence tolerance (tol parameter)
    CONVERGENCE_MAX_ITERATIONS = 100  # Safety limit for volatility calculation

    def __init__(self, tau: float = 0.5, tol: float = 1e-6):
        """Initialize Glicko-2 engine.

        Args:
            tau: System constant controlling volatility changes (default 0.5)
            tol: Convergence tolerance for volatility calculation (default 1e-6)

        """
        self.TAU = tau
        self.EPSILON = tol

        # Historical tracking
        self.agent_ratings: dict[str, GlickoRating] = {}
        self.match_history: dict[str, list[Match]] = {}

    def get_rating(self, agent_id: str) -> GlickoRating:
        """Get current rating for agent.

        Args:
            agent_id: Unique agent identifier

        Returns:
            Current Glicko rating (default if new agent)

        """
        if agent_id not in self.agent_ratings:
            self.agent_ratings[agent_id] = GlickoRating()
            self.match_history[agent_id] = []

        return self.agent_ratings[agent_id]

    def _g(self, phi: float) -> float:
        """g(φ) function from Glicko-2 algorithm.

        Reduces impact of games against high RD opponents.
        """
        return 1.0 / math.sqrt(1.0 + 3.0 * phi * phi / (math.pi * math.pi))

    def _E(self, mu: float, mu_j: float, phi_j: float) -> float:
        """E(μ, μ_j, φ_j) function from Glicko-2 algorithm.

        Expected score against opponent j.
        """
        g_phi_j = self._g(phi_j)
        return 1.0 / (1.0 + math.exp(-g_phi_j * (mu - mu_j)))

    def _compute_variance(self, mu: float, matches: list[tuple[float, float]]) -> float:
        """Compute variance (v) from match results.

        Args:
            mu: Player's rating (Glicko-2 scale)
            matches: List of (opponent_mu, opponent_phi) tuples

        Returns:
            Variance value

        """
        variance_inv = 0.0

        for mu_j, phi_j in matches:
            g_phi_j = self._g(phi_j)
            E_val = self._E(mu, mu_j, phi_j)
            variance_inv += g_phi_j * g_phi_j * E_val * (1.0 - E_val)

        if variance_inv == 0.0:
            return float("inf")

        return 1.0 / variance_inv

    def _compute_delta(self, mu: float, matches: list[tuple[float, float, float]]) -> float:
        """Compute delta (Δ) from match results.

        Args:
            mu: Player's rating (Glicko-2 scale)
            matches: List of (opponent_mu, opponent_phi, outcome) tuples

        Returns:
            Delta value

        """
        delta_sum = 0.0

        for mu_j, phi_j, s_j in matches:
            g_phi_j = self._g(phi_j)
            E_val = self._E(mu, mu_j, phi_j)
            delta_sum += g_phi_j * (s_j - E_val)

        return delta_sum

    def _f(self, x: float, delta: float, phi: float, v: float, a: float) -> float:
        """f(x) function for volatility calculation (Illinois algorithm)."""
        ex = math.exp(x)
        phi_sq = phi * phi
        tau_sq = self.TAU * self.TAU

        numerator = ex * (delta * delta - phi_sq - v - ex)
        denominator = 2.0 * (phi_sq + v + ex) * (phi_sq + v + ex)

        return numerator / denominator - (x - a) / tau_sq

    def _compute_new_volatility(self, sigma: float, phi: float, v: float, delta: float) -> float:
        """Compute new volatility using Illinois algorithm.

        This is the most computationally intensive part of Glicko-2.
        Target: <50μs of the total <100μs budget.

        Args:
            sigma: Current volatility
            phi: Current RD (Glicko-2 scale)
            v: Variance
            delta: Delta value

        Returns:
            New volatility value

        """
        a = math.log(sigma * sigma)

        # Initial search bounds
        delta_sq = delta * delta
        phi_sq = phi * phi

        if delta_sq > phi_sq + v:
            B = math.log(delta_sq - phi_sq - v)
        else:
            k = 1
            while self._f(a - k * self.TAU, delta, phi, v, a) < 0:
                k += 1
            B = a - k * self.TAU

        # Illinois algorithm for root finding
        A = a
        f_A = self._f(A, delta, phi, v, a)
        f_B = self._f(B, delta, phi, v, a)

        iterations = 0
        while abs(B - A) > self.EPSILON and iterations < self.CONVERGENCE_MAX_ITERATIONS:
            C = A + (A - B) * f_A / (f_B - f_A)
            f_C = self._f(C, delta, phi, v, a)

            if f_C * f_B < 0:
                A = B
                f_A = f_B
            else:
                f_A = f_A / 2.0

            B = C
            f_B = f_C
            iterations += 1

        return math.exp(A / 2.0)

    def update_rating(self, agent_id: str, matches: list[Match]) -> RatingUpdate:
        """Update agent rating based on match results.

        Performance target: <100μs

        Args:
            agent_id: Unique agent identifier
            matches: List of match results

        Returns:
            RatingUpdate with old/new ratings and execution time

        """
        start_time = time.perf_counter()

        # Get current rating
        old_rating = self.get_rating(agent_id)

        # Handle no matches (rating decay due to inactivity)
        if not matches:
            # RD increases over time with no matches
            mu, phi = old_rating.to_glicko2_scale()
            sigma = old_rating.volatility

            # Step 6: Update RD for new period
            phi_star = math.sqrt(phi * phi + sigma * sigma)

            new_rating = GlickoRating.from_glicko2_scale(
                mu=mu,
                phi=phi_star,
                volatility=sigma,
                matches_played=old_rating.matches_played,
            )

            execution_time_us = (time.perf_counter() - start_time) * 1_000_000

            self.agent_ratings[agent_id] = new_rating

            return RatingUpdate(
                old_rating=old_rating,
                new_rating=new_rating,
                execution_time_us=execution_time_us,
                matches_processed=0,
            )

        # Convert to Glicko-2 scale
        mu, phi = old_rating.to_glicko2_scale()
        sigma = old_rating.volatility

        # Step 3: Compute variance (v)
        match_opponents = [
            (m.opponent_rating.to_glicko2_scale()[0], m.opponent_rating.to_glicko2_scale()[1])
            for m in matches
        ]
        v = self._compute_variance(mu, match_opponents)

        # Step 4: Compute delta (Δ)
        match_data = [
            (
                m.opponent_rating.to_glicko2_scale()[0],
                m.opponent_rating.to_glicko2_scale()[1],
                m.outcome.value,
            )
            for m in matches
        ]
        delta = v * self._compute_delta(mu, match_data)

        # Step 5: Compute new volatility (σ')
        sigma_prime = self._compute_new_volatility(sigma, phi, v, delta)

        # Step 6: Update RD to new pre-rating period value (φ*)
        phi_star = math.sqrt(phi * phi + sigma_prime * sigma_prime)

        # Step 7: Update rating and RD (μ', φ')
        phi_prime = 1.0 / math.sqrt(1.0 / (phi_star * phi_star) + 1.0 / v)
        mu_prime = mu + phi_prime * phi_prime * self._compute_delta(mu, match_data)

        # Convert back to standard scale
        new_rating = GlickoRating.from_glicko2_scale(
            mu=mu_prime,
            phi=phi_prime,
            volatility=sigma_prime,
            matches_played=old_rating.matches_played + len(matches),
        )

        execution_time_us = (time.perf_counter() - start_time) * 1_000_000

        # Update stored rating
        self.agent_ratings[agent_id] = new_rating

        # Store matches in history
        if agent_id not in self.match_history:
            self.match_history[agent_id] = []
        self.match_history[agent_id].extend(matches)

        return RatingUpdate(
            old_rating=old_rating,
            new_rating=new_rating,
            execution_time_us=execution_time_us,
            matches_processed=len(matches),
        )

    def record_match(
        self,
        agent1_id: str,
        agent2_id: str,
        outcome: MatchOutcome,
    ) -> tuple[RatingUpdate, RatingUpdate]:
        """Record a match between two agents and update both ratings.

        Args:
            agent1_id: First agent identifier
            agent2_id: Second agent identifier
            outcome: Match outcome from agent1's perspective

        Returns:
            Tuple of (agent1_update, agent2_update)

        """
        # Get current ratings
        agent1_rating = self.get_rating(agent1_id)
        agent2_rating = self.get_rating(agent2_id)

        # Create match records
        match1 = Match(opponent_rating=agent2_rating, outcome=outcome)

        # Reverse outcome for agent2
        if outcome == MatchOutcome.WIN:
            outcome2 = MatchOutcome.LOSS
        elif outcome == MatchOutcome.LOSS:
            outcome2 = MatchOutcome.WIN
        else:
            outcome2 = MatchOutcome.DRAW

        match2 = Match(opponent_rating=agent1_rating, outcome=outcome2)

        # Update both ratings
        update1 = self.update_rating(agent1_id, [match1])
        update2 = self.update_rating(agent2_id, [match2])

        return (update1, update2)

    def get_leaderboard(self, top_n: int | None = None) -> list[tuple[str, GlickoRating]]:
        """Get ranked leaderboard of agents.

        Ranking is based on conservative rating estimate: rating - 2*RD
        (95% confidence that true rating is above this value)

        Args:
            top_n: Return only top N agents (None = all)

        Returns:
            List of (agent_id, rating) tuples sorted by conservative rating

        """
        leaderboard = [(agent_id, rating) for agent_id, rating in self.agent_ratings.items()]

        # Sort by conservative rating estimate
        leaderboard.sort(key=lambda x: x[1].rating - 2 * x[1].rd, reverse=True)

        if top_n is not None:
            leaderboard = leaderboard[:top_n]

        return leaderboard

    def get_match_history(self, agent_id: str, limit: int | None = None) -> list[Match]:
        """Get match history for agent.

        Args:
            agent_id: Agent identifier
            limit: Maximum matches to return (None = all)

        Returns:
            List of matches (most recent first)

        """
        if agent_id not in self.match_history:
            return []

        history = list(reversed(self.match_history[agent_id]))

        if limit is not None:
            history = history[:limit]

        return history

    def expected_score(self, agent1_id: str, agent2_id: str) -> float:
        """Compute expected score for agent1 vs agent2.

        Args:
            agent1_id: First agent identifier
            agent2_id: Second agent identifier

        Returns:
            Expected score (0.0 = certain loss, 0.5 = even, 1.0 = certain win)

        """
        agent1_rating = self.get_rating(agent1_id)
        agent2_rating = self.get_rating(agent2_id)

        mu1, phi1 = agent1_rating.to_glicko2_scale()
        mu2, phi2 = agent2_rating.to_glicko2_scale()

        return self._E(mu1, mu2, phi2)

    def get_statistics(self) -> dict[str, any]:
        """Get engine statistics.

        Returns:
            Dictionary with statistics (total agents, total matches, etc.)

        """
        total_agents = len(self.agent_ratings)
        total_matches = sum(len(matches) for matches in self.match_history.values())

        if total_agents > 0:
            avg_rating = sum(r.rating for r in self.agent_ratings.values()) / total_agents
            avg_rd = sum(r.rd for r in self.agent_ratings.values()) / total_agents
            avg_volatility = sum(r.volatility for r in self.agent_ratings.values()) / total_agents
        else:
            avg_rating = avg_rd = avg_volatility = 0.0

        return {
            "total_agents": total_agents,
            "total_matches": total_matches,
            "avg_rating": avg_rating,
            "avg_rd": avg_rd,
            "avg_volatility": avg_volatility,
            "tau": self.TAU,
            "epsilon": self.EPSILON,
        }
