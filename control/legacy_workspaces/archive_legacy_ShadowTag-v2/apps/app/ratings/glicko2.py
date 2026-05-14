# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Glicko-2 rating system for kernels, agents, and strategies.

Implementation with configurable tolerance (tol) parameter for convergence.
Used to rank performance of kernels/agents across benchmarks.
"""

import math

from pydantic import BaseModel


class Glicko2Player(BaseModel):
    """
    Glicko-2 player representation.

    Attributes:
        mu: Rating (default 1500 on Glicko scale, 0 on Glicko-2 scale)
        phi: Rating deviation (uncertainty, default 350 → ~2.014761 on Glicko-2)
        vol: Volatility (how erratic performance is, default 0.06)
    """

    mu: float = 0.0  # Glicko-2 scale (0 = 1500 on original scale)
    phi: float = 2.014761  # Rating deviation on Glicko-2 scale
    vol: float = 0.06  # Volatility

    # Conversion constant: 173.7178
    SCALE: float = 173.7178

    def get_rating(self) -> float:
        """Get rating on original Glicko scale (1500 center)."""
        return self.mu * self.SCALE + 1500

    def get_rd(self) -> float:
        """Get rating deviation on original Glicko scale."""
        return self.phi * self.SCALE

    def get_vol(self) -> float:
        """Get volatility."""
        return self.vol

    @classmethod
    def from_glicko(cls, rating: float = 1500, rd: float = 350, vol: float = 0.06):
        """Create from original Glicko scale values."""
        mu = (rating - 1500) / cls.SCALE
        phi = rd / cls.SCALE
        return cls(mu=mu, phi=phi, vol=vol)


class Glicko2System:
    """
    Glicko-2 rating system with configurable tolerance.

    Used to rank kernels, agents, and strategies based on performance.
    """

    def __init__(self, tau: float = 0.5, tol: float = 1e-6):
        """
        Initialize Glicko-2 system.

        Args:
            tau: System constant (constrains volatility changes, default 0.5)
            tol: Convergence tolerance for volatility calculation (default 1e-6)
        """
        self.tau = tau
        self.tol = tol

    def update(
        self,
        player: Glicko2Player,
        results: list[tuple[Glicko2Player, float]],
    ) -> Glicko2Player:
        """
        Update player rating based on match results.

        Args:
            player: Player to update
            results: List of (opponent, score) tuples where score is:
                     1.0 = win, 0.5 = draw, 0.0 = loss

        Returns:
            Updated Glicko2Player
        """
        if not results:
            # No games played: increase uncertainty
            phi_new = math.sqrt(player.phi**2 + player.vol**2)
            return Glicko2Player(mu=player.mu, phi=phi_new, vol=player.vol)

        # Step 2: Compute v and delta
        v_inv = 0.0
        delta_sum = 0.0

        for opponent, score in results:
            g_phi = self._g(opponent.phi)
            e_val = self._E(player.mu, opponent.mu, opponent.phi)

            v_inv += g_phi**2 * e_val * (1 - e_val)
            delta_sum += g_phi * (score - e_val)

        v = 1.0 / v_inv if v_inv > 0 else float("inf")
        delta = v * delta_sum

        # Step 3: Compute new volatility using Illinois algorithm
        vol_new = self._compute_volatility(player, v, delta)

        # Step 4: Compute new rating deviation
        phi_star = math.sqrt(player.phi**2 + vol_new**2)

        # Step 5: Compute new rating and rating deviation
        phi_new = 1.0 / math.sqrt(1.0 / phi_star**2 + 1.0 / v)
        mu_new = player.mu + phi_new**2 * delta_sum

        return Glicko2Player(mu=mu_new, phi=phi_new, vol=vol_new)

    def _g(self, phi: float) -> float:
        """Compute g(φ) function."""
        return 1.0 / math.sqrt(1 + 3 * phi**2 / math.pi**2)

    def _E(self, mu: float, mu_j: float, phi_j: float) -> float:
        """Compute expected score E(μ, μj, φj)."""
        return 1.0 / (1 + math.exp(-self._g(phi_j) * (mu - mu_j)))

    def _compute_volatility(
        self,
        player: Glicko2Player,
        v: float,
        delta: float,
    ) -> float:
        """
        Compute new volatility using Illinois algorithm.

        Args:
            player: Current player state
            v: Variance
            delta: Delta value

        Returns:
            New volatility
        """
        phi = player.phi
        sigma = player.vol
        tau = self.tau

        # Step 3.1: Initialize
        a = math.log(sigma**2)

        def f(x: float) -> float:
            """Function to find root of."""
            ex = math.exp(x)
            phi2 = phi**2
            v_inv = 1.0 / v if v > 0 else 0

            num1 = ex * (delta**2 - phi2 - v - ex)
            den1 = 2 * (phi2 + v + ex) ** 2

            num2 = x - a
            den2 = tau**2

            return num1 / den1 - num2 / den2

        # Step 3.2: Find initial bracket
        A = a
        if delta**2 > phi**2 + v:
            B = math.log(delta**2 - phi**2 - v)
        else:
            k = 1
            while f(a - k * tau) < 0:
                k += 1
            B = a - k * tau

        # Step 3.3-3.6: Illinois algorithm
        f_A = f(A)
        f_B = f(B)

        while abs(B - A) > self.tol:
            C = A + (A - B) * f_A / (f_B - f_A)
            f_C = f(C)

            if f_C * f_B < 0:
                A = B
                f_A = f_B
            else:
                f_A = f_A / 2.0

            B = C
            f_B = f_C

        return math.exp(A / 2.0)


class RatingComparison(BaseModel):
    """Comparison of rating systems (Glicko-2 vs Elo vs PPO)."""

    system_name: str
    rating: float
    uncertainty: float | None = None
    volatility: float | None = None
    notes: str

    def __str__(self) -> str:
        parts = [f"{self.system_name}: {self.rating:.1f}"]
        if self.uncertainty:
            parts.append(f"±{self.uncertainty:.1f}")
        if self.volatility:
            parts.append(f"(vol: {self.volatility:.3f})")
        parts.append(f"- {self.notes}")
        return " ".join(parts)


def compare_rating_systems() -> list[RatingComparison]:
    """
    Compare Glicko-2 vs Elo vs PPO rating approaches.

    Returns:
        List of rating system comparisons
    """
    return [
        RatingComparison(
            system_name="Glicko-2",
            rating=1500,
            uncertainty=350,
            volatility=0.06,
            notes="Captures uncertainty + volatility, handles inactive players",
        ),
        RatingComparison(
            system_name="Elo",
            rating=1500,
            uncertainty=None,
            volatility=None,
            notes="Simple but no uncertainty tracking, assumes constant skill",
        ),
        RatingComparison(
            system_name="PPO (Policy)",
            rating=0.0,  # Not directly comparable
            uncertainty=None,
            volatility=None,
            notes="Optimizes policy directly, not a rating system per se",
        ),
    ]
