"""
Glicko Rating System - Uncertainty-aware rankings.

Glicko extends Elo by adding:
- Rating Deviation (RD): Measures uncertainty in rating
- Volatility: Measures degree of expected fluctuation

Perfect for rating agents, benchmarks, opportunities, funnels.
"""

import math
from dataclasses import dataclass


@dataclass
class GlickoRating:
    """A Glicko rating with deviation and volatility."""

    rating: float = 1500.0  # Mean rating
    rd: float = 350.0  # Rating deviation (uncertainty)
    volatility: float = 0.06  # Volatility

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "rating": self.rating,
            "rd": self.rd,
            "volatility": self.volatility,
            "confidence_interval": (self.rating - 2 * self.rd, self.rating + 2 * self.rd),
        }


class GlickoSystem:
    """
    Glicko-2 rating system implementation.

    Advantages over Elo:
    - Accounts for uncertainty (RD)
    - Handles rating periods with no games
    - More accurate for volatile performance
    """

    # System constants
    TAU = 0.5  # System volatility constraint
    EPSILON = 0.000001  # Convergence tolerance

    def __init__(self, tau: float = 0.5):
        """
        Initialize Glicko system.

        Args:
            tau: System volatility constraint
        """
        self.TAU = tau

    def update_rating(
        self,
        player_rating: GlickoRating,
        opponent_ratings: list[GlickoRating],
        outcomes: list[float],  # 1 = win, 0.5 = draw, 0 = loss
    ) -> GlickoRating:
        """
        Update a player's rating after games.

        Args:
            player_rating: Player's current rating
            opponent_ratings: List of opponent ratings
            outcomes: List of outcomes (1/0.5/0)

        Returns:
            Updated rating
        """
        if len(opponent_ratings) != len(outcomes):
            raise ValueError("Number of opponents must match number of outcomes")

        # Step 1: Convert to Glicko-2 scale
        mu = (player_rating.rating - 1500) / 173.7178
        phi = player_rating.rd / 173.7178
        sigma = player_rating.volatility

        # Step 2: Compute v (variance)
        v = self._compute_v(mu, phi, opponent_ratings)

        # Step 3: Compute delta (performance difference)
        delta = self._compute_delta(mu, opponent_ratings, outcomes, v)

        # Step 4: Update volatility
        sigma_prime = self._update_volatility(sigma, phi, delta, v)

        # Step 5: Update rating deviation
        phi_star = math.sqrt(phi**2 + sigma_prime**2)

        # Step 6: Update rating and RD
        phi_prime = 1 / math.sqrt(1 / phi_star**2 + 1 / v)
        mu_prime = mu + phi_prime**2 * self._g(phi) * sum(
            (outcome - self._E(mu, opp.rating, opp.rd))
            for opp, outcome in zip(opponent_ratings, outcomes, strict=False)
        )

        # Step 7: Convert back to original scale
        new_rating = GlickoRating(
            rating=173.7178 * mu_prime + 1500, rd=173.7178 * phi_prime, volatility=sigma_prime
        )

        return new_rating

    def _compute_v(self, mu: float, phi: float, opponents: list[GlickoRating]) -> float:
        """Compute variance."""
        return 1 / sum(
            self._g(opp.rd / 173.7178) ** 2
            * self._E(mu, opp.rating, opp.rd)
            * (1 - self._E(mu, opp.rating, opp.rd))
            for opp in opponents
        )

    def _compute_delta(
        self, mu: float, opponents: list[GlickoRating], outcomes: list[float], v: float
    ) -> float:
        """Compute performance difference."""
        return v * sum(
            self._g(opp.rd / 173.7178) * (outcome - self._E(mu, opp.rating, opp.rd))
            for opp, outcome in zip(opponents, outcomes, strict=False)
        )

    def _update_volatility(self, sigma: float, phi: float, delta: float, v: float) -> float:
        """Update volatility using Illinois algorithm."""
        # Simplified volatility update
        # Full implementation would use iterative Illinois algorithm
        a = math.log(sigma**2)

        # Compute f(x)
        def f(x):
            ex = math.exp(x)
            return (ex * (delta**2 - phi**2 - v - ex)) / (2 * (phi**2 + v + ex) ** 2) - (
                x - a
            ) / self.TAU**2

        # Find new volatility (simplified)
        A = a
        if delta**2 > phi**2 + v:
            B = math.log(delta**2 - phi**2 - v)
        else:
            k = 1
            while f(a - k * self.TAU) < 0:
                k += 1
            B = a - k * self.TAU

        # Iterate to convergence
        fA = f(A)
        fB = f(B)

        while abs(B - A) > self.EPSILON:
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

    def _g(self, phi: float) -> float:
        """g function for Glicko-2."""
        return 1 / math.sqrt(1 + 3 * phi**2 / math.pi**2)

    def _E(self, mu: float, opp_rating: float, opp_rd: float) -> float:
        """Expected outcome."""
        opp_mu = (opp_rating - 1500) / 173.7178
        opp_phi = opp_rd / 173.7178
        return 1 / (1 + math.exp(-self._g(opp_phi) * (mu - opp_mu)))

    def decay_rd(self, rating: GlickoRating, periods: int = 1) -> GlickoRating:
        """
        Decay RD due to inactivity.

        Args:
            rating: Current rating
            periods: Number of inactive periods

        Returns:
            Rating with decayed RD
        """
        new_rd = min(
            math.sqrt(rating.rd**2 + periods * rating.volatility**2),
            350.0,  # Max RD
        )

        return GlickoRating(rating=rating.rating, rd=new_rd, volatility=rating.volatility)


# Example usage
def example_glicko_usage():
    """Example of using Glicko rating system."""
    system = GlickoSystem()

    # Initialize player ratings
    player = GlickoRating(rating=1500, rd=200, volatility=0.06)
    opponent1 = GlickoRating(rating=1400, rd=30, volatility=0.06)
    opponent2 = GlickoRating(rating=1550, rd=100, volatility=0.06)
    opponent3 = GlickoRating(rating=1700, rd=300, volatility=0.06)

    # Player outcomes: win, loss, draw
    outcomes = [1.0, 0.0, 0.5]
    opponents = [opponent1, opponent2, opponent3]

    # Update rating
    new_rating = system.update_rating(player, opponents, outcomes)

    print(f"Original rating: {player.rating:.2f} ± {player.rd:.2f}")
    print(f"New rating: {new_rating.rating:.2f} ± {new_rating.rd:.2f}")
    print(f"New volatility: {new_rating.volatility:.4f}")

    return new_rating
