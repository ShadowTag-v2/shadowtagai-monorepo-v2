# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Glicko-2 Rating System
Superior to Elo for AI agent ranking with volatility tracking

Advantages over Elo/PPO:
- Tracks rating deviation (uncertainty)
- Volatility parameter (consistency)
- More accurate for sparse interactions
- Better handles rating inflation/deflation
"""

import logging
import math
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Glicko2Player:
    """Glicko-2 player/agent with rating, deviation, and volatility

    Attributes:
        mu: Rating (mean skill level)
        phi: Rating deviation (uncertainty)
        sigma: Volatility (consistency of performance)

    """

    mu: float = 1500.0  # Initial rating (Glicko scale)
    phi: float = 350.0  # Initial rating deviation
    sigma: float = 0.06  # Initial volatility

    def get_rating(self) -> float:
        """Get rating on standard Glicko-2 scale"""
        return self.mu

    def get_rd(self) -> float:
        """Get rating deviation (uncertainty)"""
        return self.phi

    def get_volatility(self) -> float:
        """Get volatility (consistency)"""
        return self.sigma

    def to_glicko2_scale(self) -> tuple[float, float]:
        """Convert to Glicko-2 internal scale"""
        mu = (self.mu - 1500) / 173.7178
        phi = self.phi / 173.7178
        return mu, phi

    def from_glicko2_scale(self, mu: float, phi: float):
        """Convert from Glicko-2 internal scale"""
        self.mu = mu * 173.7178 + 1500
        self.phi = phi * 173.7178


class Glicko2System:
    """Glicko-2 rating system for AI agent ranking

    Parameters
    ----------
        tau: System constant (constrains volatility change) - default 0.5
        tol: Convergence tolerance for volatility calculation - default 1e-6

    """

    def __init__(self, tau: float = 0.5, tol: float = 1e-6):
        self.tau = tau
        self.tol = tol
        logger.info(f"Glicko-2 system initialized (tau={tau}, tol={tol})")

    def update(
        self,
        player: Glicko2Player,
        opponent_ratings: list[float],
        opponent_rds: list[float],
        scores: list[float],
    ) -> Glicko2Player:
        """Update player rating based on match results

        Args:
            player: Player to update
            opponent_ratings: List of opponent ratings
            opponent_rds: List of opponent rating deviations
            scores: List of match outcomes (1=win, 0.5=draw, 0=loss)

        Returns:
            Updated player with new rating, RD, and volatility

        """
        if len(opponent_ratings) != len(opponent_rds) != len(scores):
            raise ValueError("Opponent ratings, RDs, and scores must have same length")

        if len(scores) == 0:
            # No games played - increase uncertainty
            player.phi = math.sqrt(player.phi**2 + player.sigma**2)
            return player

        # Convert to Glicko-2 scale
        mu, phi = player.to_glicko2_scale()

        # Convert opponents to Glicko-2 scale
        opponents = [
            ((r - 1500) / 173.7178, rd / 173.7178)
            for r, rd in zip(opponent_ratings, opponent_rds, strict=False)
        ]

        # Step 1: Calculate variance (v)
        v = self._calculate_variance(mu, opponents)

        # Step 2: Calculate delta
        delta = self._calculate_delta(mu, opponents, scores, v)

        # Step 3: Calculate new volatility (sigma')
        sigma_prime = self._calculate_new_volatility(phi, delta, v, player.sigma)

        # Step 4: Update rating deviation (phi*)
        phi_star = math.sqrt(phi**2 + sigma_prime**2)

        # Step 5: Update rating and RD
        phi_prime = 1 / math.sqrt(1 / phi_star**2 + 1 / v)
        mu_prime = mu + phi_prime**2 * sum(
            self._g(opp_phi) * (score - self._E(mu, opp_mu, opp_phi))
            for (opp_mu, opp_phi), score in zip(opponents, scores, strict=False)
        )

        # Update player
        player.from_glicko2_scale(mu_prime, phi_prime)
        player.sigma = sigma_prime

        return player

    def _g(self, phi: float) -> float:
        """Glicko-2 g function"""
        return 1 / math.sqrt(1 + 3 * phi**2 / math.pi**2)

    def _E(self, mu: float, mu_j: float, phi_j: float) -> float:
        """Expected score against opponent j"""
        return 1 / (1 + math.exp(-self._g(phi_j) * (mu - mu_j)))

    def _calculate_variance(self, mu: float, opponents: list[tuple[float, float]]) -> float:
        """Calculate variance (v)"""
        v_inv = sum(
            self._g(opp_phi) ** 2
            * self._E(mu, opp_mu, opp_phi)
            * (1 - self._E(mu, opp_mu, opp_phi))
            for opp_mu, opp_phi in opponents
        )
        return 1 / v_inv if v_inv > 0 else float("inf")

    def _calculate_delta(
        self,
        mu: float,
        opponents: list[tuple[float, float]],
        scores: list[float],
        v: float,
    ) -> float:
        """Calculate improvement (delta)"""
        return v * sum(
            self._g(opp_phi) * (score - self._E(mu, opp_mu, opp_phi))
            for (opp_mu, opp_phi), score in zip(opponents, scores, strict=False)
        )

    def _calculate_new_volatility(self, phi: float, delta: float, v: float, sigma: float) -> float:
        """Calculate new volatility using Illinois algorithm
        This is the complex part with the f function
        """
        # Initial values
        a = math.log(sigma**2)

        def f(x: float) -> float:
            """Volatility update function"""
            ex = math.exp(x)
            phi2 = phi**2
            return (
                ex * (delta**2 - phi2 - v - ex) / (2 * (phi2 + v + ex) ** 2) - (x - a) / self.tau**2
            )

        # Find bounds
        A = a
        if delta**2 > phi**2 + v:
            B = math.log(delta**2 - phi**2 - v)
        else:
            k = 1
            while f(a - k * self.tau) < 0:
                k += 1
            B = a - k * self.tau

        # Illinois algorithm for root finding
        fA = f(A)
        fB = f(B)

        while abs(B - A) > self.tol:
            C = A + (A - B) * fA / (fB - fA)
            fC = f(C)

            if fC * fB < 0:
                A = B
                fA = fB
            else:
                fA = fA / 2

            B = C
            fB = fC

        return math.exp(A / 2)

    def expected_score(self, player1: Glicko2Player, player2: Glicko2Player) -> float:
        """Calculate expected score for player1 vs player2"""
        mu1, phi1 = player1.to_glicko2_scale()
        mu2, phi2 = player2.to_glicko2_scale()
        return self._E(mu1, mu2, phi2)

    def match_quality(self, player1: Glicko2Player, player2: Glicko2Player) -> float:
        """Calculate match quality (0 to 1)
        Higher = more competitive/uncertain outcome
        """
        expected = self.expected_score(player1, player2)
        # Match quality peaks at 0.5 (even match)
        return 1 - 2 * abs(expected - 0.5)


# Agent ranking use case
class AgentRanking:
    """Track and rank AI agents using Glicko-2"""

    def __init__(self):
        self.system = Glicko2System(tau=0.5, tol=1e-6)
        self.agents: dict[str, Glicko2Player] = {}
        logger.info("Agent ranking system initialized")

    def register_agent(self, agent_id: str, initial_rating: float = 1500.0):
        """Register new agent"""
        self.agents[agent_id] = Glicko2Player(mu=initial_rating)
        logger.info(f"Registered agent {agent_id} with rating {initial_rating}")

    def record_match(self, agent_id: str, opponent_id: str, score: float):
        """Record a match result (1=win, 0.5=draw, 0=loss)"""
        if agent_id not in self.agents:
            self.register_agent(agent_id)
        if opponent_id not in self.agents:
            self.register_agent(opponent_id)

        agent = self.agents[agent_id]
        opponent = self.agents[opponent_id]

        # Update agent rating
        self.agents[agent_id] = self.system.update(agent, [opponent.mu], [opponent.phi], [score])

        # Update opponent rating (inverse score)
        self.agents[opponent_id] = self.system.update(
            opponent,
            [agent.mu],
            [agent.phi],
            [1 - score],
        )

    def get_rankings(self) -> list[tuple[str, float, float]]:
        """Get ranked list of agents (agent_id, rating, RD)"""
        rankings = [(agent_id, player.mu, player.phi) for agent_id, player in self.agents.items()]
        return sorted(rankings, key=lambda x: x[1], reverse=True)

    def get_top_agents(self, n: int = 10) -> list[tuple[str, float]]:
        """Get top N agents"""
        rankings = self.get_rankings()
        return [(agent_id, rating) for agent_id, rating, _ in rankings[:n]]
