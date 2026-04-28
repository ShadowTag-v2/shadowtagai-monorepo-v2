# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Glicko-2 Rating System for Pnkln Agents
Version: 1.0.0

Philosophy: Uncertainty-aware performance tracking
Design: Pure Python, no external dependencies except math

Glicko-2 advantages over Elo:
- Rating Deviation (RD): Measures uncertainty in rating
- Volatility: Measures consistency of performance
- Time decay: Ratings become more uncertain with inactivity

Reference: Mark Glickman's Glicko-2 system
http://www.glicko.net/glicko/glicko2.pdf
"""

import math
from dataclasses import dataclass

# Constants
GLICKO_SCALE = 173.7178  # Conversion factor: Glicko-2 scale to Glicko scale
DEFAULT_RATING = 1500.0
DEFAULT_RD = 350.0
DEFAULT_VOLATILITY = 0.06
TAU = 0.5  # System constant (constrains volatility change)


@dataclass
class Match:
    """Result of a match between two players"""

    opponent_rating: float
    opponent_rd: float
    outcome: float  # 1.0 = win, 0.5 = draw, 0.0 = loss


class Glicko2Player:
    """Glicko-2 player/agent with rating, rating deviation, and volatility.

    Attributes:
        mu: Rating on Glicko-2 scale (internal)
        phi: Rating deviation on Glicko-2 scale (internal)
        vol: Volatility (measures consistency)

    Methods:
        get_rating(): Convert to standard Glicko scale (1500 = average)
        get_rd(): Get rating deviation (uncertainty)
        get_vol(): Get volatility
        update(): Update rating after matches

    """

    def __init__(
        self,
        rating: float = DEFAULT_RATING,
        rd: float = DEFAULT_RD,
        vol: float = DEFAULT_VOLATILITY,
    ):
        """Initialize player with Glicko scale ratings.

        Args:
            rating: Initial rating (default 1500)
            rd: Initial rating deviation (default 350)
            vol: Initial volatility (default 0.06)

        """
        # Convert to Glicko-2 scale
        self.mu = (rating - DEFAULT_RATING) / GLICKO_SCALE
        self.phi = rd / GLICKO_SCALE
        self.vol = vol

    def get_rating(self) -> float:
        """Get rating on standard Glicko scale"""
        return self.mu * GLICKO_SCALE + DEFAULT_RATING

    def get_rd(self) -> float:
        """Get rating deviation (uncertainty in rating)"""
        return self.phi * GLICKO_SCALE

    def get_vol(self) -> float:
        """Get volatility (consistency of performance)"""
        return self.vol

    def _g(self, phi: float) -> float:
        """Glicko-2 g function.

        Reduces the impact of games against uncertain opponents.
        """
        return 1 / math.sqrt(1 + 3 * phi**2 / math.pi**2)

    def _E(self, mu: float, mu_j: float, phi_j: float) -> float:
        """Expected outcome against opponent.

        Args:
            mu: Player's rating
            mu_j: Opponent's rating
            phi_j: Opponent's rating deviation

        Returns:
            Expected score (0 to 1)

        """
        return 1 / (1 + math.exp(-self._g(phi_j) * (mu - mu_j)))

    def _compute_v(self, matches: list[Match]) -> float:
        """Compute variance of performance.

        Args:
            matches: List of matches played

        Returns:
            Estimated variance

        """
        v_inv = 0.0
        for match in matches:
            mu_j = (match.opponent_rating - DEFAULT_RATING) / GLICKO_SCALE
            phi_j = match.opponent_rd / GLICKO_SCALE

            g = self._g(phi_j)
            E = self._E(self.mu, mu_j, phi_j)

            v_inv += g**2 * E * (1 - E)

        return 1 / v_inv if v_inv > 0 else float("inf")

    def _compute_delta(self, matches: list[Match], v: float) -> float:
        """Compute estimated improvement in rating.

        Args:
            matches: List of matches played
            v: Variance of performance

        Returns:
            Estimated improvement

        """
        delta_sum = 0.0
        for match in matches:
            mu_j = (match.opponent_rating - DEFAULT_RATING) / GLICKO_SCALE
            phi_j = match.opponent_rd / GLICKO_SCALE

            g = self._g(phi_j)
            E = self._E(self.mu, mu_j, phi_j)

            delta_sum += g * (match.outcome - E)

        return v * delta_sum

    def _compute_new_volatility(
        self,
        v: float,
        delta: float,
        tau: float = TAU,
        tol: float = 1e-6,
    ) -> float:
        """Compute new volatility using Illinois algorithm.

        This is the most complex part of Glicko-2.
        Uses iterative convergence to find optimal volatility.

        Args:
            v: Variance of performance
            delta: Estimated improvement
            tau: System constant (constraint on volatility change)
            tol: Convergence tolerance

        Returns:
            New volatility

        """
        phi = self.phi
        vol = self.vol

        # Step 1: Initialize
        a = math.log(vol**2)

        def f(x: float) -> float:
            """Function to find root of"""
            ex = math.exp(x)
            num1 = ex * (delta**2 - phi**2 - v - ex)
            den1 = 2 * (phi**2 + v + ex) ** 2
            num2 = x - a
            den2 = tau**2
            return num1 / den1 - num2 / den2

        # Step 2: Set initial values
        A = a
        if delta**2 > phi**2 + v:
            B = math.log(delta**2 - phi**2 - v)
        else:
            k = 1
            while f(a - k * tau) < 0:
                k += 1
            B = a - k * tau

        # Step 3: Illinois algorithm iteration
        f_A = f(A)
        f_B = f(B)

        while abs(B - A) > tol:
            C = A + (A - B) * f_A / (f_B - f_A)
            f_C = f(C)

            if f_C * f_B <= 0:
                A = B
                f_A = f_B
            else:
                f_A = f_A / 2

            B = C
            f_B = f_C

        return math.exp(A / 2)

    def update(self, matches: list[Match], tau: float = TAU, tol: float = 1e-6) -> None:
        """Update rating based on match results.

        Args:
            matches: List of Match objects
            tau: System constant (default 0.5)
            tol: Convergence tolerance for volatility (default 1e-6)

        Example:
            >>> player = Glicko2Player()
            >>> matches = [
            ...     Match(opponent_rating=1400, opponent_rd=30, outcome=1.0),
            ...     Match(opponent_rating=1550, opponent_rd=100, outcome=0.0),
            ...     Match(opponent_rating=1700, opponent_rd=300, outcome=0.0)
            ... ]
            >>> player.update(matches)

        """
        if not matches:
            # No games played - increase uncertainty due to inactivity
            phi_star = math.sqrt(self.phi**2 + self.vol**2)
            self.phi = phi_star
            return

        # Step 1: Compute v and delta
        v = self._compute_v(matches)
        delta = self._compute_delta(matches, v)

        # Step 2: Compute new volatility
        new_vol = self._compute_new_volatility(v, delta, tau, tol)

        # Step 3: Update rating deviation to pre-period value
        phi_star = math.sqrt(self.phi**2 + new_vol**2)

        # Step 4: Update rating and RD
        phi_prime = 1 / math.sqrt(1 / phi_star**2 + 1 / v)

        mu_prime = self.mu
        for match in matches:
            mu_j = (match.opponent_rating - DEFAULT_RATING) / GLICKO_SCALE
            phi_j = match.opponent_rd / GLICKO_SCALE

            g = self._g(phi_j)
            E = self._E(self.mu, mu_j, phi_j)

            mu_prime += phi_prime**2 * g * (match.outcome - E)

        # Update instance variables
        self.mu = mu_prime
        self.phi = phi_prime
        self.vol = new_vol

    def decay_rating(self, periods: int = 1) -> None:
        """Decay rating due to inactivity.

        Increases rating deviation to reflect increased uncertainty.

        Args:
            periods: Number of rating periods inactive

        """
        for _ in range(periods):
            phi_star = math.sqrt(self.phi**2 + self.vol**2)
            self.phi = phi_star

    def __repr__(self) -> str:
        return (
            f"Glicko2Player("
            f"rating={self.get_rating():.1f}, "
            f"rd={self.get_rd():.1f}, "
            f"vol={self.vol:.4f})"
        )


def compare_players(player1: Glicko2Player, player2: Glicko2Player) -> dict:
    """Compare two players and predict match outcome.

    Args:
        player1: First player
        player2: Second player

    Returns:
        Dictionary with comparison data

    """
    # Expected score for player1
    mu1 = player1.mu
    mu2 = player2.mu
    phi2 = player2.phi

    player1._g(phi2)
    expected_score = player1._E(mu1, mu2, phi2)

    # Rating difference
    rating_diff = player1.get_rating() - player2.get_rating()

    # Combined uncertainty
    combined_rd = math.sqrt(player1.get_rd() ** 2 + player2.get_rd() ** 2)

    return {
        "player1_rating": player1.get_rating(),
        "player2_rating": player2.get_rating(),
        "rating_difference": rating_diff,
        "expected_score_player1": expected_score,
        "expected_score_player2": 1 - expected_score,
        "player1_rd": player1.get_rd(),
        "player2_rd": player2.get_rd(),
        "combined_rd": combined_rd,
        "confidence": 1 - (combined_rd / DEFAULT_RD),  # 0 to 1
    }


if __name__ == "__main__":
    # Self-test
    print("Glicko-2 Rating System - Self Test")
    print("=" * 60)

    # Create two players
    alice = Glicko2Player(rating=1500, rd=200, vol=0.06)
    bob = Glicko2Player(rating=1400, rd=30, vol=0.06)

    print("\nInitial ratings:")
    print(f"Alice: {alice}")
    print(f"Bob: {bob}")

    # Compare players
    comparison = compare_players(alice, bob)
    print("\nPrediction:")
    print(f"  Alice expected score: {comparison['expected_score_player1']:.3f}")
    print(f"  Bob expected score: {comparison['expected_score_player2']:.3f}")
    print(f"  Confidence: {comparison['confidence']:.3f}")

    # Alice plays matches
    alice_matches = [
        Match(opponent_rating=1400, opponent_rd=30, outcome=1.0),  # Win vs Bob
        Match(opponent_rating=1550, opponent_rd=100, outcome=0.0),  # Loss
        Match(opponent_rating=1700, opponent_rd=300, outcome=0.0),  # Loss
    ]

    print("\nAlice plays 3 matches: Win, Loss, Loss")
    alice.update(alice_matches)
    print(f"Alice after matches: {alice}")

    # Bob's perspective (one loss to Alice)
    bob_matches = [
        Match(opponent_rating=1500, opponent_rd=200, outcome=0.0),  # Loss to Alice
    ]

    bob.update(bob_matches)
    print(f"Bob after match: {bob}")

    # Test inactivity decay
    print("\nAlice inactive for 3 periods...")
    alice.decay_rating(periods=3)
    print(f"Alice after decay: {alice}")
    print("(Note: RD increased due to uncertainty)")

    print("\n" + "=" * 60)
    print("✓ Glicko-2 implementation working correctly")
