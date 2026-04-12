"""
Glicko-2 Rating System

Improved rating system over Elo, with rating deviation (RD) and volatility.
Used for ranking Pinkln agents based on debate/benchmark performance.

Reference: http://www.glicko.net/glicko/glicko2.pdf
"""

import math
from dataclasses import dataclass

# Constants
TAU = 0.5  # System volatility constraint (0.3–1.2 typical)
EPSILON = 0.000001  # Convergence threshold


@dataclass
class Glicko2Player:
    """
    Glicko-2 player representation

    Attributes:
        mu: Rating (default 1500, higher = better)
        phi: Rating deviation (default 350, lower = more certain)
        vol: Volatility (default 0.06, measures consistency)
    """

    mu: float = 1500.0
    phi: float = 350.0
    vol: float = 0.06

    def get_rating(self) -> float:
        """Get display rating"""
        return self.mu

    def get_rd(self) -> float:
        """Get rating deviation (uncertainty)"""
        return self.phi

    def get_vol(self) -> float:
        """Get volatility (consistency measure)"""
        return self.vol

    def to_glicko_scale(self) -> tuple[float, float]:
        """Convert to Glicko-2 scale (mu, phi)"""
        mu_scaled = (self.mu - 1500) / 173.7178
        phi_scaled = self.phi / 173.7178
        return mu_scaled, phi_scaled

    @classmethod
    def from_glicko_scale(cls, mu_scaled: float, phi_scaled: float, vol: float):
        """Create from Glicko-2 scale"""
        mu = mu_scaled * 173.7178 + 1500
        phi = phi_scaled * 173.7178
        return cls(mu=mu, phi=phi, vol=vol)


def g(phi: float) -> float:
    """
    Auxiliary function g(φ)

    Reduces impact of opponents with high RD
    """
    return 1.0 / math.sqrt(1.0 + (3.0 * phi**2) / (math.pi**2))


def E(mu: float, mu_j: float, phi_j: float) -> float:
    """
    Expected score E(μ, μ_j, φ_j)

    Probability that player with rating μ beats player with (μ_j, φ_j)
    """
    return 1.0 / (1.0 + math.exp(-g(phi_j) * (mu - mu_j)))


def update(
    player: Glicko2Player,
    opponents: list[Glicko2Player],
    results: list[float],
    tau: float = TAU,
    tol: float = EPSILON,
) -> Glicko2Player:
    """
    Update player rating after games

    Args:
        player: Player to update
        opponents: List of opponent players
        results: List of results (1.0 = win, 0.5 = draw, 0.0 = loss)
        tau: System volatility constraint (default 0.5)
        tol: Convergence tolerance for Newton-Raphson (default 1e-6)

    Returns:
        Updated Glicko2Player
    """

    if len(opponents) != len(results):
        raise ValueError("Number of opponents must match number of results")

    if len(opponents) == 0:
        # No games played: increase RD due to inactivity
        phi_new = math.sqrt(player.phi**2 + player.vol**2)
        return Glicko2Player(mu=player.mu, phi=phi_new, vol=player.vol)

    # Step 1: Convert to Glicko-2 scale
    mu, phi = player.to_glicko_scale()

    # Step 2: Compute v (variance)
    v_inv = 0.0
    for opponent, result in zip(opponents, results, strict=False):
        mu_j, phi_j = opponent.to_glicko_scale()
        E_val = E(mu, mu_j, phi_j)
        v_inv += g(phi_j) ** 2 * E_val * (1 - E_val)

    v = 1.0 / v_inv if v_inv > 0 else float("inf")

    # Step 3: Compute Δ (performance difference)
    delta = 0.0
    for opponent, result in zip(opponents, results, strict=False):
        mu_j, phi_j = opponent.to_glicko_scale()
        E_val = E(mu, mu_j, phi_j)
        delta += g(phi_j) * (result - E_val)

    delta *= v

    # Step 4: Compute new volatility (σ') using Illinois algorithm
    sigma = player.vol
    phi_sq = phi**2
    delta_sq = delta**2

    # Define f(x) for Illinois algorithm
    def f(x: float) -> float:
        exp_x = math.exp(x)
        phi_sq_plus = phi_sq + v + exp_x
        a_term = exp_x * (delta_sq - phi_sq - v - exp_x) / (2.0 * phi_sq_plus**2)
        b_term = (x - math.log(sigma**2)) / (tau**2)
        return a_term - b_term

    # Initialize bounds
    a = math.log(sigma**2)

    if delta_sq > phi_sq + v:
        b = math.log(delta_sq - phi_sq - v)
    else:
        k = 1
        while f(a - k * tau) < 0:
            k += 1
        b = a - k * tau

    # Illinois algorithm (Newton-Raphson variant)
    f_a = f(a)
    f_b = f(b)

    while abs(b - a) > tol:
        c = a + (a - b) * f_a / (f_b - f_a)
        f_c = f(c)

        if f_c * f_b < 0:
            a = b
            f_a = f_b
        else:
            f_a = f_a / 2.0

        b = c
        f_b = f_c

    sigma_new = math.exp(a / 2.0)

    # Step 5: Update rating deviation (φ*)
    phi_star = math.sqrt(phi_sq + sigma_new**2)

    # Step 6: Update rating (φ') and rating (μ')
    phi_new = 1.0 / math.sqrt(1.0 / phi_star**2 + 1.0 / v)

    mu_new = mu + phi_new**2 * sum(
        g(opponent.to_glicko_scale()[1]) * (result - E(mu, *opponent.to_glicko_scale()))
        for opponent, result in zip(opponents, results, strict=False)
    )

    # Step 7: Convert back to original scale
    return Glicko2Player.from_glicko_scale(mu_new, phi_new, sigma_new)


def predict_win_probability(player1: Glicko2Player, player2: Glicko2Player) -> float:
    """
    Predict probability that player1 beats player2

    Returns:
        float: Probability (0.0–1.0)
    """
    mu1, phi1 = player1.to_glicko_scale()
    mu2, phi2 = player2.to_glicko_scale()

    return E(mu1, mu2, phi2)


def rating_difference_to_win_probability(rating_diff: float) -> float:
    """
    Convert rating difference to win probability

    Args:
        rating_diff: Rating difference (player1.mu - player2.mu)

    Returns:
        Approximate win probability
    """
    # Simplified: assumes equal RD
    return 1.0 / (1.0 + 10.0 ** (-rating_diff / 400.0))


# Example usage and tests
if __name__ == "__main__":
    print("Glicko-2 Rating System Example\n")

    # Create players
    alice = Glicko2Player(mu=1500, phi=200, vol=0.06)
    bob = Glicko2Player(mu=1400, phi=30, vol=0.06)
    charlie = Glicko2Player(mu=1550, phi=100, vol=0.06)
    diana = Glicko2Player(mu=1700, phi=300, vol=0.06)

    print("Initial Ratings:")
    print(f"  Alice: μ={alice.mu:.1f}, φ={alice.phi:.1f}, σ={alice.vol:.3f}")
    print(f"  Bob: μ={bob.mu:.1f}, φ={bob.phi:.1f}, σ={bob.vol:.3f}")
    print(f"  Charlie: μ={charlie.mu:.1f}, φ={charlie.phi:.1f}, σ={charlie.vol:.3f}")
    print(f"  Diana: μ={diana.mu:.1f}, φ={diana.phi:.1f}, σ={diana.vol:.3f}")

    # Alice plays games: beats Bob, loses to Charlie, draws with Diana
    opponents = [bob, charlie, diana]
    results = [1.0, 0.0, 0.5]  # 1.0 = win, 0.0 = loss, 0.5 = draw

    print("\nAlice's games:")
    print("  vs Bob (1400): Win")
    print("  vs Charlie (1550): Loss")
    print("  vs Diana (1700): Draw")

    # Update Alice's rating
    alice_updated = update(alice, opponents, results, tau=0.5, tol=1e-6)

    print("\nUpdated Rating:")
    print(
        f"  Alice: μ={alice_updated.mu:.1f}, φ={alice_updated.phi:.1f}, σ={alice_updated.vol:.3f}"
    )

    change = alice_updated.mu - alice.mu
    print(f"  Change: {change:+.1f}")

    # Predict future match
    print("\nPredictions:")
    prob_alice_vs_bob = predict_win_probability(alice_updated, bob)
    prob_alice_vs_charlie = predict_win_probability(alice_updated, charlie)
    prob_alice_vs_diana = predict_win_probability(alice_updated, diana)

    print(f"  Alice vs Bob: {prob_alice_vs_bob:.1%} win probability")
    print(f"  Alice vs Charlie: {prob_alice_vs_charlie:.1%} win probability")
    print(f"  Alice vs Diana: {prob_alice_vs_diana:.1%} win probability")

    # Test convergence tolerance
    print("\n--- Testing tolerance parameter ---")
    tolerances = [1e-3, 1e-6, 1e-9]
    for tol in tolerances:
        alice_test = update(alice, opponents, results, tau=0.5, tol=tol)
        print(f"  tol={tol:.0e}: μ={alice_test.mu:.6f}, φ={alice_test.phi:.6f}")

    print("\n✅ Glicko-2 implementation complete with tolerance parameter")
