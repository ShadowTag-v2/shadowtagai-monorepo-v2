# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Glicko-2 Rating System for LLM Provider Performance

Implements the Glicko-2 rating system (Glickman, 2012) to dynamically rank
LLM providers based on:
- Decision accuracy (vs ground truth or consensus)
- Response latency (bonus for fast responses <70ms)
- Decision quality (confidence scores >0.9)

This enables:
1. Dynamic failover order (best-rated provider first)
2. Automatic rebalancing of provider allocation percentages
3. Data-driven provider selection (not hardcoded preferences)

Reference:
Glickman, M. E. (2012). "Example of the Glicko-2 system."
Boston University. http://www.glicko.net/glicko/glicko2.pdf
"""

import math
from dataclasses import dataclass


# Glicko-2 system constants
_MU = 1500  # Initial rating (mean skill)
_PHI = 350  # Initial rating deviation (uncertainty)
_SIGMA = 0.06  # Initial volatility
_TAU = 0.5  # System constraint on volatility change
_EPSILON = 0.000001  # Convergence tolerance


@dataclass
class Glicko2Player:
    """
    Represents a player (LLM provider) in the Glicko-2 rating system.

    Attributes:
        mu: Rating (skill level). Default 1500. Higher = better.
        phi: Rating deviation (uncertainty). Default 350. Lower = more certain.
        sigma: Volatility (consistency). Default 0.06. Lower = more consistent.
    """

    mu: float = _MU
    phi: float = _PHI
    sigma: float = _SIGMA

    def __post_init__(self):
        """Convert to Glicko-2 scale on initialization."""
        # Glicko-2 uses a different scale internally
        # mu: rating → μ (mean)
        # phi: RD → φ (deviation)
        # sigma: volatility → σ
        self._mu = (self.mu - _MU) / 173.7178
        self._phi = self.phi / 173.7178
        self._sigma = self.sigma

    def get_rating(self) -> float:
        """Get current rating (converted back to Glicko-1 scale for readability)."""
        return self._mu * 173.7178 + _MU

    def get_rd(self) -> float:
        """Get current rating deviation (RD)."""
        return self._phi * 173.7178

    def get_volatility(self) -> float:
        """Get current volatility."""
        return self._sigma

    def update(self, matches: list[tuple[float, "Glicko2Player"]], tau: float = _TAU, tol: float = _EPSILON):
        """
        Update rating based on match results.

        Args:
            matches: List of (outcome, opponent) tuples.
                     outcome: 1.0 (win), 0.5 (draw), 0.0 (loss)
                     opponent: Glicko2Player representing opponent
            tau: System constraint on volatility change (default: 0.5)
            tol: Convergence tolerance for Illinois algorithm (default: 1e-6)

        Example:
            # Provider won against system average
            provider.update([(1.0, system_average)])

            # Provider lost against high-rated opponent
            provider.update([(0.0, high_rated_provider)])
        """
        if not matches:
            # No matches - increase uncertainty (RD) due to inactivity
            self._phi = math.sqrt(self._phi**2 + self._sigma**2)
            return

        # Step 2: Compute v and delta (variance and improvement)
        v, delta = self._compute_v_and_delta(matches)

        # Step 3: Update volatility using Illinois algorithm
        self._sigma = self._update_volatility(v, delta, tau, tol)

        # Step 4: Update rating deviation
        phi_star = math.sqrt(self._phi**2 + self._sigma**2)

        # Step 5: Update rating and RD
        self._phi = 1 / math.sqrt(1 / phi_star**2 + 1 / v)

        delta_mu = self._phi**2 * sum(self._g(opponent._phi) * (outcome - self._E(opponent)) for outcome, opponent in matches)
        self._mu += delta_mu

    def _compute_v_and_delta(self, matches: list[tuple[float, "Glicko2Player"]]) -> tuple[float, float]:
        """
        Compute variance (v) and improvement (delta).

        v: Estimated variance of rating based on game outcomes
        delta: Estimated improvement in rating
        """
        # Variance
        v_inv = sum(self._g(opponent._phi) ** 2 * self._E(opponent) * (1 - self._E(opponent)) for _, opponent in matches)
        v = 1 / v_inv if v_inv > 0 else float("inf")

        # Delta (improvement)
        delta = v * sum(self._g(opponent._phi) * (outcome - self._E(opponent)) for outcome, opponent in matches)

        return v, delta

    def _update_volatility(self, v: float, delta: float, tau: float, tol: float) -> float:
        """
        Update volatility using Illinois algorithm (step 5.5 in Glickman's paper).

        This is the most complex part of Glicko-2, using iterative root-finding
        to determine optimal volatility.
        """
        phi = self._phi
        sigma = self._sigma

        # Initial values
        a = math.log(sigma**2)
        A = a

        # Define f(x) function (equation 5.9 in paper)
        def f(x):
            ex = math.exp(x)
            num = ex * (delta**2 - phi**2 - v - ex)
            denom = 2 * (phi**2 + v + ex) ** 2
            return num / denom - (x - a) / tau**2

        # Set initial values for B
        if delta**2 > phi**2 + v:
            B = math.log(delta**2 - phi**2 - v)
        else:
            k = 1
            while f(a - k * tau) < 0:
                k += 1
            B = a - k * tau

        # Illinois algorithm iteration
        fA = f(A)
        fB = f(B)

        while abs(B - A) > tol:
            # Calculate midpoint
            C = A + (A - B) * fA / (fB - fA)
            fC = f(C)

            # Update bounds
            if fC * fB < 0:
                A, fA = B, fB
            else:
                fA /= 2

            B, fB = C, fC

        # Return new volatility
        return math.exp(A / 2)

    def _g(self, phi: float) -> float:
        """
        g(φ) function - reduces impact of high RD opponents.

        High RD (uncertainty) opponents have less impact on rating changes.
        """
        return 1 / math.sqrt(1 + 3 * phi**2 / math.pi**2)

    def _E(self, opponent: "Glicko2Player") -> float:
        """
        E(μ, μj, φj) - expected outcome against opponent.

        Returns probability of beating opponent (0.0 to 1.0).
        """
        return 1 / (1 + math.exp(-self._g(opponent._phi) * (self._mu - opponent._mu)))

    def __repr__(self):
        return f"Glicko2Player(rating={self.get_rating():.0f}, RD={self.get_rd():.0f}, vol={self.get_volatility():.4f})"


# Convenience functions for LLM provider rating


def create_provider_ratings() -> dict:
    """
    Create initial Glicko-2 ratings for all LLM providers.

    Returns:
        dict mapping ProviderType to Glicko2Player
    """
    from .failover_engine import ProviderType

    return {
        ProviderType.GEMINI: Glicko2Player(mu=1500, phi=350, sigma=0.06),
        ProviderType.CLAUDE: Glicko2Player(mu=1500, phi=350, sigma=0.06),
        ProviderType.GPT5: Glicko2Player(mu=1500, phi=350, sigma=0.06),
        ProviderType.LOCAL: Glicko2Player(mu=1200, phi=100, sigma=0.06),  # Lower initial rating
    }


def update_provider_rating(
    provider: Glicko2Player, outcome: float, opponent: Glicko2Player, latency_bonus: float = 0.0, quality_bonus: float = 0.0
) -> None:
    """
    Update provider's Glicko-2 rating based on decision outcome.

    Args:
        provider: Provider to update
        outcome: Base outcome (1.0 = success, 0.0 = failure)
        opponent: Opponent (typically system average)
        latency_bonus: Bonus for fast response (0.0 to 0.2)
        quality_bonus: Bonus for high confidence (0.0 to 0.2)

    Example:
        # Provider succeeded with fast response and high confidence
        update_provider_rating(
            provider=gemini_player,
            outcome=1.0,
            opponent=system_average,
            latency_bonus=0.1,  # <70ms response
            quality_bonus=0.1   # >0.9 confidence
        )
        # Effective outcome: 1.0 + 0.1 + 0.1 = 1.2 (capped at 1.0)
    """
    # Composite outcome (capped at 1.0)
    composite_outcome = min(1.0, outcome + latency_bonus + quality_bonus)

    # Update rating
    provider.update([(composite_outcome, opponent)])


def get_ranked_providers(ratings: dict) -> list[tuple[object, Glicko2Player]]:
    """
    Get providers ranked by Glicko-2 rating (highest first).

    Args:
        ratings: dict mapping ProviderType to Glicko2Player

    Returns:
        List of (ProviderType, Glicko2Player) tuples sorted by rating
    """
    return sorted(ratings.items(), key=lambda x: x[1].get_rating(), reverse=True)


def get_allocation_percentages(ratings: dict) -> dict:
    """
    Calculate recommended allocation percentages based on Glicko ratings.

    Uses softmax to convert ratings into allocation percentages:
    - Higher rated providers get more allocation
    - Temperature parameter controls distribution steepness

    Args:
        ratings: dict mapping ProviderType to Glicko2Player

    Returns:
        dict mapping ProviderType to allocation percentage (0.0 to 1.0)
    """
    # Temperature parameter (lower = more aggressive, higher = more uniform)
    temperature = 300.0

    # Calculate softmax
    rating_values = [player.get_rating() for player in ratings.values()]
    exp_ratings = [math.exp(r / temperature) for r in rating_values]
    sum_exp = sum(exp_ratings)

    allocations = {}
    for (provider, player), exp_rating in zip(ratings.items(), exp_ratings):
        allocations[provider] = exp_rating / sum_exp

    return allocations


# Example usage
if __name__ == "__main__":
    print("=== Glicko-2 Rating System Demo ===\n")

    # Initialize providers
    gemini = Glicko2Player(mu=1500, phi=350, sigma=0.06)
    claude = Glicko2Player(mu=1500, phi=350, sigma=0.06)
    gpt5 = Glicko2Player(mu=1500, phi=350, sigma=0.06)
    system_avg = Glicko2Player(mu=1500, phi=200, sigma=0.06)

    print("Initial ratings:")
    print(f"  Gemini: {gemini}")
    print(f"  Claude: {claude}")
    print(f"  GPT-5: {gpt5}")
    print()

    # Simulate 10 decisions
    print("Simulating 10 decisions:\n")

    for i in range(1, 11):
        # Gemini wins most (70% success rate)
        if i <= 7:
            gemini.update([(1.0, system_avg)])  # Success
            print(f"  Decision {i}: Gemini SUCCESS")
        else:
            gemini.update([(0.0, system_avg)])  # Failure
            print(f"  Decision {i}: Gemini FAILURE")

        # Claude wins some (50% success rate)
        if i % 2 == 0:
            claude.update([(1.0, system_avg)])
            print(f"  Decision {i}: Claude SUCCESS")
        else:
            claude.update([(0.0, system_avg)])
            print(f"  Decision {i}: Claude FAILURE")

        # GPT-5 wins few (30% success rate)
        if i <= 3:
            gpt5.update([(1.0, system_avg)])
            print(f"  Decision {i}: GPT-5 SUCCESS")
        else:
            gpt5.update([(0.0, system_avg)])
            print(f"  Decision {i}: GPT-5 FAILURE")

        print()

    print("\nFinal ratings after 10 decisions:")
    print(f"  Gemini: {gemini}")
    print(f"  Claude: {claude}")
    print(f"  GPT-5: {gpt5}")
    print()

    # Show allocation percentages
    ratings = {"gemini": gemini, "claude": claude, "gpt5": gpt5}

    allocations = get_allocation_percentages(ratings)
    print("Recommended allocation percentages:")
    for provider, pct in sorted(allocations.items(), key=lambda x: x[1], reverse=True):
        print(f"  {provider}: {pct * 100:.1f}%")
    print()

    # Show ranked providers
    print("Provider ranking (best to worst):")
    for i, (provider, player) in enumerate(get_ranked_providers(ratings), 1):
        print(f"  {i}. {provider}: {player.get_rating():.0f} rating")
    print()

    # Demonstrate latency/quality bonuses
    print("=== Bonus System Demo ===\n")
    test_provider = Glicko2Player(mu=1500, phi=350, sigma=0.06)

    print(f"Initial: {test_provider}")

    # Success with bonuses
    update_provider_rating(
        provider=test_provider,
        outcome=1.0,
        opponent=system_avg,
        latency_bonus=0.1,  # Fast response
        quality_bonus=0.1,  # High confidence
    )

    print(f"After success + bonuses: {test_provider}")
    print(f"Rating change: {test_provider.get_rating() - 1500:.0f} points")
