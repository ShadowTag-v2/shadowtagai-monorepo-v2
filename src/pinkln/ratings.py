# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Glicko-2 Rating System for AI Performance Tracking

Better than Elo for:
- Uncertainty tracking (rating deviation)
- Volatility detection (performance consistency)
- Inactive player handling

tau = 0.5 (volatility constraint)
tol = 1e-6 (convergence tolerance)
"""

import math
from dataclasses import dataclass


@dataclass
class Glicko2Player:
    """
    Glicko-2 player/agent representation

    Attributes:
        mu: Rating on Glicko-2 scale (default 0)
        phi: Rating deviation/uncertainty (default 2.014761872416068)
        sigma: Volatility (default 0.06)
    """

    mu: float = 0.0
    phi: float = 2.014761872416068  # Converts to RD=350 on Glicko scale
    sigma: float = 0.06

    @classmethod
    def from_glicko(cls, rating: float = 1500, rd: float = 350, vol: float = 0.06):
        """
        Create from Glicko-1 scale (rating/RD)

        Args:
            rating: Glicko-1 rating (default 1500)
            rd: Rating deviation (default 350)
            vol: Volatility (default 0.06)

        Returns:
            Glicko2Player
        """
        mu = (rating - 1500) / 173.7178
        phi = rd / 173.7178
        return cls(mu=mu, phi=phi, sigma=vol)

    def get_rating(self) -> float:
        """Convert to Glicko-1 rating"""
        return 173.7178 * self.mu + 1500

    def get_rd(self) -> float:
        """Convert to Glicko-1 RD"""
        return 173.7178 * self.phi

    def get_vol(self) -> float:
        """Get volatility"""
        return self.sigma


class Glicko2System:
    """
    Glicko-2 rating system

    Usage:
        system = Glicko2System(tau=0.5, tol=1e-6)
        player = Glicko2Player.from_glicko(rating=1500, rd=350)

        # After match
        updated = system.update(player, [(opponent, score)])
    """

    def __init__(self, tau: float = 0.5, tol: float = 1e-6):
        """
        Initialize Glicko-2 system

        Args:
            tau: Volatility constraint (0.3-1.2 typical, 0.5 default)
            tol: Convergence tolerance for volatility calculation
        """
        self.tau = tau
        self.tol = tol

    def update(
        self,
        player: Glicko2Player,
        results: list[tuple[Glicko2Player, float]],
    ) -> Glicko2Player:
        """
        Update player rating based on match results

        Args:
            player: Player to update
            results: List of (opponent, score) tuples
                     score: 1.0 = win, 0.5 = draw, 0.0 = loss

        Returns:
            Updated Glicko2Player
        """
        if not results:
            # No matches: increase uncertainty
            new_phi = math.sqrt(player.phi**2 + player.sigma**2)
            return Glicko2Player(mu=player.mu, phi=new_phi, sigma=player.sigma)

        # Step 2: Compute v (estimated variance)
        v = self._compute_v(player, results)

        # Step 3: Compute delta (performance difference)
        delta = self._compute_delta(player, results, v)

        # Step 4: Update volatility
        new_sigma = self._update_volatility(player, delta, v)

        # Step 5: Update rating deviation
        phi_star = math.sqrt(player.phi**2 + new_sigma**2)

        # Step 6: Update rating and RD
        new_phi = 1 / math.sqrt(1 / phi_star**2 + 1 / v)
        new_mu = player.mu + new_phi**2 * self._g(player, results)

        return Glicko2Player(mu=new_mu, phi=new_phi, sigma=new_sigma)

    def _g(self, player: Glicko2Player, results: list[tuple[Glicko2Player, float]]) -> float:
        """Compute g function (rating impact)"""
        total = 0.0
        for opponent, score in results:
            g_phi = 1 / math.sqrt(1 + 3 * opponent.phi**2 / math.pi**2)
            e_val = 1 / (1 + math.exp(-g_phi * (player.mu - opponent.mu)))
            total += g_phi * (score - e_val)
        return total

    def _compute_v(
        self,
        player: Glicko2Player,
        results: list[tuple[Glicko2Player, float]],
    ) -> float:
        """Compute estimated variance"""
        total = 0.0
        for opponent, _ in results:
            g_phi = 1 / math.sqrt(1 + 3 * opponent.phi**2 / math.pi**2)
            e_val = 1 / (1 + math.exp(-g_phi * (player.mu - opponent.mu)))
            total += g_phi**2 * e_val * (1 - e_val)
        return 1 / total if total > 0 else float("inf")

    def _compute_delta(
        self,
        player: Glicko2Player,
        results: list[tuple[Glicko2Player, float]],
        v: float,
    ) -> float:
        """Compute performance difference"""
        return v * self._g(player, results)

    def _update_volatility(
        self,
        player: Glicko2Player,
        delta: float,
        v: float,
    ) -> float:
        """Update volatility using Illinois algorithm"""
        phi = player.phi
        sigma = player.sigma
        tau = self.tau

        # Step 5.1
        a = math.log(sigma**2)

        def f(x: float) -> float:
            """Convergence function"""
            exp_x = math.exp(x)
            phi2 = phi**2
            delta2 = delta**2

            term1 = exp_x * (delta2 - phi2 - v - exp_x)
            term2 = 2 * (phi2 + v + exp_x) ** 2
            term3 = (x - a) / tau**2

            return term1 / term2 - term3

        # Step 5.2
        if delta**2 > phi**2 + v:
            b = math.log(delta**2 - phi**2 - v)
        else:
            k = 1
            while f(a - k * tau) < 0:
                k += 1
            b = a - k * tau

        # Step 5.3: Illinois algorithm
        f_a = f(a)
        f_b = f(b)

        while abs(b - a) > self.tol:
            # Step 5.4
            c = a + (a - b) * f_a / (f_b - f_a)
            f_c = f(c)

            # Step 5.5
            if f_c * f_b <= 0:
                a = b
                f_a = f_b
            else:
                f_a = f_a / 2

            b = c
            f_b = f_c

        # Step 5.6
        return math.exp(a / 2)
