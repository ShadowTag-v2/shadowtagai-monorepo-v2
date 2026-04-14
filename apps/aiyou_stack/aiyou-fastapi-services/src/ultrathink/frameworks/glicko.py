import math


class Glicko2Engine:
    """Implementation of the Glicko-2 rating system for agent evaluation.
    Reference: http://www.glicko.net/glicko/glicko2.pdf
    """

    def __init__(self, tau: float = 0.5):
        self.tau = tau  # Constrain on volatility change
        self.epsilon = 0.000001  # Convergence tolerance

    def _g(self, phi: float) -> float:
        return 1.0 / math.sqrt(1.0 + 3.0 * (phi**2) / (math.pi**2))

    def _E(self, mu: float, mu_j: float, phi_j: float) -> float:
        return 1.0 / (1.0 + math.exp(-self._g(phi_j) * (mu - mu_j)))

    def update_rating(
        self, rating: float, rd: float, volatility: float, results: list[tuple[float, float, float]],
    ) -> tuple[float, float, float]:
        """Update rating for a single player based on a series of game results.

        Args:
            rating: Current rating (standard scale, e.g., 1500)
            rd: Current rating deviation
            volatility: Current volatility
            results: List of (opponent_rating, opponent_rd, score) tuples.
                     Score is 1.0 (win), 0.5 (draw), 0.0 (loss).

        Returns:
            (new_rating, new_rd, new_volatility)

        """
        # Step 2: Convert to Glicko-2 scale
        mu = (rating - 1500.0) / 173.7178
        phi = rd / 173.7178

        # Step 3: Compute v (variance)
        v_inv = 0.0
        for opp_rating, opp_rd, score in results:
            mu_j = (opp_rating - 1500.0) / 173.7178
            phi_j = opp_rd / 173.7178
            g_phi_j = self._g(phi_j)
            E_val = self._E(mu, mu_j, phi_j)
            v_inv += (g_phi_j**2) * E_val * (1.0 - E_val)

        if v_inv == 0:
            # No games or effectively no info, return possibly aged out values
            # For simplicity, if no games, we just return inputs processed for time which is not handled here
            # Assuming this function is called ONLY when there are results.
            return rating, rd, volatility

        v = 1.0 / v_inv

        # Step 4: Compute Delta
        delta_sum = 0.0
        for opp_rating, opp_rd, score in results:
            mu_j = (opp_rating - 1500.0) / 173.7178
            phi_j = opp_rd / 173.7178
            delta_sum += self._g(phi_j) * (score - self._E(mu, mu_j, phi_j))

        delta = v * delta_sum

        # Step 5: Update volatility (sigma) - Simplified iterative procedure
        a = math.log(volatility**2)

        def f(x):
            exp_x = math.exp(x)
            term1 = (exp_x * (delta**2 - phi**2 - v - exp_x)) / (2 * ((phi**2 + v + exp_x) ** 2))
            term2 = (x - a) / (self.tau**2)
            return term1 - term2

        # Illinois algorithm or similar root finding could be used.
        # Using simple Newton-Raphson or bounded bisection is standard.
        # Implementing a simple iterative check as per paper suggestion (A)
        A = a
        if (delta**2) > (phi**2 + v):
            B = math.log(delta**2 - phi**2 - v)
        else:
            k = 1
            while f(a - k * self.tau) < 0:
                k += 1
            B = a - k * self.tau

        fA = f(A)
        fB = f(B)

        while abs(B - A) > self.epsilon:
            C = A + (A - B) * fA / (fB - fA)
            fC = f(C)
            if fC * fB < 0:
                A = B
                fA = fB
            else:
                fA = fA / 2.0

            B = C
            fB = fC

        sigma_prime = math.exp(A / 2.0)

        # Step 6: Update Rating Deviation to new pre-rating period value
        phi_star = math.sqrt(phi**2 + sigma_prime**2)

        # Step 7: Update Rating and RD
        phi_prime = 1.0 / math.sqrt(1.0 / (phi_star**2) + 1.0 / v)
        mu_prime = mu + (phi_prime**2) * delta_sum

        # Step 8: Convert back
        new_rating = 173.7178 * mu_prime + 1500.0
        new_rd = 173.7178 * phi_prime

        return new_rating, new_rd, sigma_prime
