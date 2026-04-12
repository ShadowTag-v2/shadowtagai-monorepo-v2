"""
Glicko-2 Rating System Implementation

A chess-style rating system that tracks:
- Rating (skill strength): 1500 = average, 2000 = expert, 2500 = world-class
- RD (rating deviation): uncertainty about rating
- Volatility (sigma): how erratic/consistent performance is

Use cases:
- Rank AI agents/skills by performance
- Track improvement over time
- Compare effectiveness of different approaches
- Identify regressions (rating drops)

References:
- Original paper: Glickman (2012) "Example of the Glicko-2 system"
- http://www.glicko.net/glicko/glicko2.pdf
"""

import math
from dataclasses import dataclass


@dataclass
class Player:
    """Represents a player/agent with Glicko-2 rating."""

    rating: float = 1500  # μ (mu): skill rating
    rd: float = 350  # φ (phi): rating deviation (uncertainty)
    volatility: float = 0.06  # σ (sigma): volatility

    def __post_init__(self):
        """Validate initial values."""
        assert self.rd > 0, "RD must be positive"
        assert self.volatility > 0, "Volatility must be positive"


class Glicko2:
    """
    Glicko-2 rating system implementation.

    Key parameters:
    - tau (τ): System volatility constraint (0.3-1.2, default 0.6)
      - Low tau (0.3): Conservative, slow rating changes
      - High tau (1.2): Aggressive, fast rating changes
    - epsilon: Convergence tolerance for volatility iteration (default 0.000001)
    """

    # Glicko-2 scale factor (converts Glicko to Glicko-2 scale)
    SCALE = 173.7178

    def __init__(self, tau: float = 0.6, epsilon: float = 0.000001):
        """
        Initialize Glicko-2 system.

        Args:
            tau: System volatility constraint (0.3-1.2)
            epsilon: Convergence tolerance for volatility calculation
        """
        self.tau = tau
        self.epsilon = epsilon

    def _g(self, phi: float) -> float:
        """
        g(φ) function from Glicko-2 paper.
        Measures impact of opponent's RD on rating change.
        """
        return 1 / math.sqrt(1 + 3 * phi**2 / math.pi**2)

    def _E(self, mu: float, mu_j: float, phi_j: float) -> float:
        """
        E(μ, μ_j, φ_j) function from Glicko-2 paper.
        Expected score against opponent j.
        """
        return 1 / (1 + math.exp(-self._g(phi_j) * (mu - mu_j)))

    def _to_glicko2_scale(self, rating: float, rd: float) -> tuple[float, float]:
        """Convert from Glicko scale to Glicko-2 scale."""
        mu = (rating - 1500) / self.SCALE
        phi = rd / self.SCALE
        return mu, phi

    def _from_glicko2_scale(self, mu: float, phi: float) -> tuple[float, float]:
        """Convert from Glicko-2 scale to Glicko scale."""
        rating = mu * self.SCALE + 1500
        rd = phi * self.SCALE
        return rating, rd

    def _compute_variance(self, mu: float, opponents: list[tuple[float, float]]) -> float:
        """
        Compute variance v from Step 3 of Glicko-2 algorithm.

        Args:
            mu: Player's rating (Glicko-2 scale)
            opponents: List of (mu_j, phi_j) for each opponent

        Returns:
            Variance v
        """
        v_inv = 0
        for mu_j, phi_j in opponents:
            g_phi_j = self._g(phi_j)
            E_val = self._E(mu, mu_j, phi_j)
            v_inv += g_phi_j**2 * E_val * (1 - E_val)

        return 1 / v_inv if v_inv > 0 else float("inf")

    def _compute_delta(
        self, mu: float, opponents: list[tuple[float, float]], outcomes: list[float], v: float
    ) -> float:
        """
        Compute delta (Δ) from Step 4 of Glicko-2 algorithm.
        Measures improvement in rating.

        Args:
            mu: Player's rating (Glicko-2 scale)
            opponents: List of (mu_j, phi_j) for each opponent
            outcomes: List of outcomes (1=win, 0.5=draw, 0=loss)
            v: Variance from _compute_variance

        Returns:
            Delta (Δ)
        """
        delta_sum = 0
        for (mu_j, phi_j), outcome in zip(opponents, outcomes, strict=False):
            g_phi_j = self._g(phi_j)
            E_val = self._E(mu, mu_j, phi_j)
            delta_sum += g_phi_j * (outcome - E_val)

        return v * delta_sum

    def _compute_new_volatility(self, phi: float, sigma: float, v: float, delta: float) -> float:
        """
        Compute new volatility σ' using Illinois algorithm (Step 5).

        This is the most complex part of Glicko-2, involving iterative
        solving of a non-linear equation.

        Args:
            phi: Current RD (Glicko-2 scale)
            sigma: Current volatility
            v: Variance
            delta: Rating improvement

        Returns:
            New volatility σ'
        """
        # Step 5.1
        a = math.log(sigma**2)

        # Step 5.2: Define f(x)
        def f(x: float) -> float:
            ex = math.exp(x)
            phi2 = phi**2
            delta2 = delta**2
            1 / v

            term1 = (ex * (delta2 - phi2 - v - ex)) / (2 * (phi2 + v + ex) ** 2)
            term2 = (x - a) / self.tau**2
            return term1 - term2

        # Step 5.3: Set initial values for iterative algorithm
        A = a
        if delta**2 > phi**2 + v:
            B = math.log(delta**2 - phi**2 - v)
        else:
            k = 1
            while f(a - k * self.tau) < 0:
                k += 1
            B = a - k * self.tau

        # Step 5.4: Illinois algorithm iteration
        f_A = f(A)
        f_B = f(B)

        while abs(B - A) > self.epsilon:
            # Step 5.4a
            C = A + (A - B) * f_A / (f_B - f_A)
            f_C = f(C)

            # Step 5.4b
            if f_C * f_B <= 0:
                A = B
                f_A = f_B
            else:
                f_A = f_A / 2

            B = C
            f_B = f_C

        # Step 5.5
        return math.exp(A / 2)

    def update_rating(
        self, player: Player, opponents: list[Player], outcomes: list[float]
    ) -> Player:
        """
        Update player rating based on match outcomes.

        Args:
            player: Player whose rating to update
            opponents: List of opponent Players
            outcomes: List of outcomes (1=win, 0.5=draw, 0=loss)

        Returns:
            Updated Player with new rating, RD, and volatility

        Example:
            >>> system = Glicko2()
            >>> alice = Player(rating=1500, rd=200, volatility=0.06)
            >>> bob = Player(rating=1600, rd=150, volatility=0.06)
            >>> outcomes = [1.0]  # Alice beat Bob
            >>> alice_new = system.update_rating(alice, [bob], outcomes)
        """
        assert len(opponents) == len(outcomes), "Must have one outcome per opponent"

        # Step 1: Convert to Glicko-2 scale
        mu, phi = self._to_glicko2_scale(player.rating, player.rd)
        sigma = player.volatility

        opponents_g2 = [self._to_glicko2_scale(opp.rating, opp.rd) for opp in opponents]

        # Step 2: Compute variance v
        v = self._compute_variance(mu, opponents_g2)

        # Step 3: Compute delta Δ
        delta = self._compute_delta(mu, opponents_g2, outcomes, v)

        # Step 4: Compute new volatility σ'
        sigma_prime = self._compute_new_volatility(phi, sigma, v, delta)

        # Step 5: Compute new RD φ*
        phi_star = math.sqrt(phi**2 + sigma_prime**2)

        # Step 6: Compute new rating μ' and RD φ'
        phi_prime = 1 / math.sqrt(1 / phi_star**2 + 1 / v)

        mu_sum = 0
        for (mu_j, phi_j), outcome in zip(opponents_g2, outcomes, strict=False):
            g_phi_j = self._g(phi_j)
            E_val = self._E(mu, mu_j, phi_j)
            mu_sum += g_phi_j * (outcome - E_val)

        mu_prime = mu + phi_prime**2 * mu_sum

        # Convert back to Glicko scale
        rating_new, rd_new = self._from_glicko2_scale(mu_prime, phi_prime)

        return Player(rating=rating_new, rd=rd_new, volatility=sigma_prime)

    def update_rd_if_inactive(self, player: Player, periods: int = 1) -> Player:
        """
        Increase RD if player has been inactive (no matches).

        Called once per rating period for inactive players.
        RD increases to reflect growing uncertainty.

        Args:
            player: Player who has been inactive
            periods: Number of rating periods of inactivity

        Returns:
            Player with increased RD
        """
        mu, phi = self._to_glicko2_scale(player.rating, player.rd)
        sigma = player.volatility

        # Increase RD for each period
        for _ in range(periods):
            phi = math.sqrt(phi**2 + sigma**2)

        rating_new, rd_new = self._from_glicko2_scale(mu, phi)

        return Player(rating=rating_new, rd=rd_new, volatility=sigma)


# Example usage and testing
if __name__ == "__main__":
    # Example from Glicko-2 paper
    print("=== Glicko-2 System Demo ===\n")

    # Initialize system with moderate volatility constraint
    system = Glicko2(tau=0.5)

    # Alice: average player
    alice = Player(rating=1500, rd=200, volatility=0.06)
    print(f"Alice (before): Rating={alice.rating:.1f}, RD={alice.rd:.1f}, σ={alice.volatility:.4f}")

    # Opponents
    bob = Player(rating=1400, rd=30, volatility=0.06)  # Weaker, very certain
    charlie = Player(rating=1550, rd=100, volatility=0.06)  # Slightly stronger
    diana = Player(rating=1700, rd=300, volatility=0.06)  # Much stronger, uncertain

    # Alice's results: beat Bob, lost to Charlie, lost to Diana
    outcomes = [1.0, 0.0, 0.0]  # 1=win, 0=loss
    opponents = [bob, charlie, diana]

    # Update Alice's rating
    alice_new = system.update_rating(alice, opponents, outcomes)
    print(
        f"Alice (after):  Rating={alice_new.rating:.1f}, RD={alice_new.rd:.1f}, σ={alice_new.volatility:.4f}\n"
    )

    # Demonstrate RD increase for inactive player
    print("=== RD Increase for Inactive Player ===\n")
    eve = Player(rating=1800, rd=50, volatility=0.06)
    print(f"Eve (active):   Rating={eve.rating:.1f}, RD={eve.rd:.1f}")

    eve_inactive = system.update_rd_if_inactive(eve, periods=10)
    print(f"Eve (10 periods inactive): Rating={eve_inactive.rating:.1f}, RD={eve_inactive.rd:.1f}")
    print("(RD increased due to uncertainty from inactivity)\n")

    # Demonstrate skill ranking
    print("=== Skill Ranking Example ===\n")
    agents = {
        "CoT": Player(rating=1650, rd=75, volatility=0.06),
        "ToT": Player(rating=1780, rd=90, volatility=0.08),
        "RoT": Player(rating=1550, rd=50, volatility=0.05),
        "ICoT": Player(rating=1920, rd=120, volatility=0.10),
        "RCR": Player(rating=1700, rd=85, volatility=0.07),
    }

    # Sort by rating
    ranked = sorted(agents.items(), key=lambda x: x[1].rating, reverse=True)

    print("Agent Rankings (by rating):")
    for rank, (name, agent) in enumerate(ranked, 1):
        confidence = "High" if agent.rd < 80 else "Medium" if agent.rd < 120 else "Low"
        stability = (
            "Stable"
            if agent.volatility < 0.07
            else "Moderate"
            if agent.volatility < 0.09
            else "Volatile"
        )
        print(
            f"{rank}. {name:6s} - Rating: {agent.rating:4.0f} (RD: {agent.rd:3.0f}, {confidence:6s} conf, {stability})"
        )

    print("\n✅ Glicko-2 implementation complete")
