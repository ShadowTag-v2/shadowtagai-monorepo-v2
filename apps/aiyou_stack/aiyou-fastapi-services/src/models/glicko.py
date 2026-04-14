"""Glicko-2 Rating System for Performance Tracking
Tracks uncertainty and volatility in addition to skill rating
"""

import math
from datetime import datetime

from pydantic import BaseModel, Field


class Glicko2Player(BaseModel):
    """A player/agent/strategy in the Glicko-2 rating system

    Attributes:
        mu: Rating (mean skill level), default 1500
        phi: Rating deviation (uncertainty), default 350
        sigma: Volatility (degree of expected fluctuation), default 0.06

    """

    player_id: str
    mu: float = Field(default=1500.0, description="Rating (skill level)")
    phi: float = Field(default=350.0, description="Rating deviation (uncertainty)")
    sigma: float = Field(default=0.06, description="Volatility")

    # Metadata
    name: str | None = None
    games_played: int = Field(default=0)
    last_updated: datetime | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "player_id": "strategy_001",
                "mu": 1650.0,
                "phi": 120.0,
                "sigma": 0.055,
                "name": "Activation Funnel Strategy A",
                "games_played": 47,
            },
        }


class Glicko2Match(BaseModel):
    """A single match/comparison result"""

    player1_id: str
    player2_id: str
    score: float = Field(
        ..., description="Score: 1.0 = player1 wins, 0.5 = draw, 0.0 = player2 wins",
    )
    timestamp: datetime | None = None
    metadata: dict | None = None


class Glicko2System(BaseModel):
    """Glicko-2 rating system

    Attributes:
        tau: System constant controlling volatility change (typically 0.3-1.2)
        tol: Convergence tolerance for iterative calculation (default 1e-6)

    """

    tau: float = Field(default=0.5, description="Volatility constraint")
    tol: float = Field(default=1e-6, description="Convergence tolerance")
    epsilon: float = Field(default=0.000001, description="Numerical stability constant")

    class Config:
        json_schema_extra = {"example": {"tau": 0.5, "tol": 1e-6}}

    def rating_to_glicko2_scale(self, mu: float, phi: float) -> tuple[float, float]:
        """Convert from Glicko-1 scale to Glicko-2 scale"""
        mu_prime = (mu - 1500.0) / 173.7178
        phi_prime = phi / 173.7178
        return mu_prime, phi_prime

    def glicko2_to_rating_scale(self, mu_prime: float, phi_prime: float) -> tuple[float, float]:
        """Convert from Glicko-2 scale to Glicko-1 scale"""
        mu = mu_prime * 173.7178 + 1500.0
        phi = phi_prime * 173.7178
        return mu, phi

    def g(self, phi: float) -> float:
        """Calculate g(φ) function
        Reduces impact of opponents with high uncertainty
        """
        return 1.0 / math.sqrt(1.0 + (3.0 * phi * phi) / (math.pi * math.pi))

    def E(self, mu: float, mu_j: float, phi_j: float) -> float:
        """Expected score function
        Probability that player beats opponent j
        """
        g_phi = self.g(phi_j)
        return 1.0 / (1.0 + math.exp(-g_phi * (mu - mu_j)))

    def compute_variance(self, matches: list[tuple[float, float, float]]) -> float:
        """Compute variance v from matches
        matches: List of (mu_j, phi_j, score) tuples
        """
        variance_sum = 0.0
        for mu_j, phi_j, _ in matches:
            g_phi = self.g(phi_j)
            E_val = self.E(0.0, mu_j, phi_j)  # Using mu=0 in Glicko-2 scale
            variance_sum += (g_phi**2) * E_val * (1 - E_val)

        return 1.0 / variance_sum if variance_sum > 0 else float("inf")

    def compute_delta(
        self, variance: float, matches: list[tuple[float, float, float]], mu: float,
    ) -> float:
        """Compute improvement Δ
        matches: List of (mu_j, phi_j, score) tuples
        """
        delta_sum = 0.0
        for mu_j, phi_j, score in matches:
            g_phi = self.g(phi_j)
            E_val = self.E(mu, mu_j, phi_j)
            delta_sum += g_phi * (score - E_val)

        return variance * delta_sum

    def compute_new_volatility(
        self, sigma: float, phi: float, variance: float, delta: float,
    ) -> float:
        """Compute new volatility σ' using iterative algorithm
        This is the complex part of Glicko-2
        """
        phi_sq = phi * phi
        delta_sq = delta * delta
        tau_sq = self.tau * self.tau

        # Initial values
        a = math.log(sigma * sigma)

        def f(x: float) -> float:
            """Function to find root of"""
            exp_x = math.exp(x)
            num1 = exp_x * (delta_sq - phi_sq - variance - exp_x)
            denom1 = 2.0 * ((phi_sq + variance + exp_x) ** 2)
            return (num1 / denom1) - ((x - a) / tau_sq)

        # Find bounds
        A = a
        if delta_sq > phi_sq + variance:
            B = math.log(delta_sq - phi_sq - variance)
        else:
            k = 1
            while f(a - k * self.tau) < 0:
                k += 1
            B = a - k * self.tau

        # Iterate to find solution
        fA = f(A)
        fB = f(B)

        while abs(B - A) > self.tol:
            C = A + (A - B) * fA / (fB - fA)
            fC = f(C)

            if fC * fB <= 0:
                A = B
                fA = fB
            else:
                fA = fA / 2.0

            B = C
            fB = fC

        return math.exp(A / 2.0)

    def update_rating(
        self,
        player: Glicko2Player,
        matches: list[Glicko2Match],
        opponent_ratings: dict[str, Glicko2Player],
    ) -> Glicko2Player:
        """Update player rating based on match results

        Args:
            player: Player to update
            matches: List of matches involving this player
            opponent_ratings: Dictionary mapping opponent_id to their Glicko2Player

        Returns:
            Updated Glicko2Player

        """
        if not matches:
            # No matches: Increase uncertainty
            new_phi = math.sqrt(player.phi**2 + player.sigma**2)
            return Glicko2Player(
                player_id=player.player_id,
                mu=player.mu,
                phi=min(new_phi, 350.0),  # Cap at initial uncertainty
                sigma=player.sigma,
                name=player.name,
                games_played=player.games_played,
                last_updated=datetime.now(),
            )

        # Convert to Glicko-2 scale
        mu, phi = self.rating_to_glicko2_scale(player.mu, player.phi)
        sigma = player.sigma

        # Prepare match data
        match_data = []
        for match in matches:
            if match.player1_id == player.player_id:
                opponent_id = match.player2_id
                score = match.score
            else:
                opponent_id = match.player1_id
                score = 1.0 - match.score

            opponent = opponent_ratings.get(opponent_id)
            if opponent:
                opp_mu, opp_phi = self.rating_to_glicko2_scale(opponent.mu, opponent.phi)
                match_data.append((opp_mu, opp_phi, score))

        # Step 1: Compute variance
        variance = self.compute_variance(match_data)

        # Step 2: Compute delta (improvement)
        delta = self.compute_delta(variance, match_data, mu)

        # Step 3: Compute new volatility
        new_sigma = self.compute_new_volatility(sigma, phi, variance, delta)

        # Step 4: Update phi
        phi_star = math.sqrt(phi**2 + new_sigma**2)

        # Step 5: Update phi and mu
        new_phi = 1.0 / math.sqrt((1.0 / (phi_star**2)) + (1.0 / variance))

        improvement_sum = 0.0
        for mu_j, phi_j, score in match_data:
            g_phi = self.g(phi_j)
            E_val = self.E(mu, mu_j, phi_j)
            improvement_sum += g_phi * (score - E_val)

        new_mu = mu + (new_phi**2) * improvement_sum

        # Convert back to rating scale
        final_mu, final_phi = self.glicko2_to_rating_scale(new_mu, new_phi)

        return Glicko2Player(
            player_id=player.player_id,
            mu=final_mu,
            phi=final_phi,
            sigma=new_sigma,
            name=player.name,
            games_played=player.games_played + len(matches),
            last_updated=datetime.now(),
        )


class PerformanceTracker(BaseModel):
    """Tracks performance of different strategies/agents/approaches using Glicko-2
    """

    system: Glicko2System = Field(default_factory=Glicko2System)
    players: dict[str, Glicko2Player] = Field(default_factory=dict)
    match_history: list[Glicko2Match] = Field(default_factory=list)

    def add_player(self, player_id: str, name: str | None = None) -> Glicko2Player:
        """Add a new player/strategy to track"""
        player = Glicko2Player(player_id=player_id, name=name)
        self.players[player_id] = player
        return player

    def record_match(
        self, player1_id: str, player2_id: str, score: float, metadata: dict | None = None,
    ) -> Glicko2Match:
        """Record a match result

        Args:
            player1_id: First player ID
            player2_id: Second player ID
            score: 1.0 = player1 wins, 0.5 = draw, 0.0 = player2 wins
            metadata: Optional match context

        """
        match = Glicko2Match(
            player1_id=player1_id,
            player2_id=player2_id,
            score=score,
            timestamp=datetime.now(),
            metadata=metadata,
        )
        self.match_history.append(match)
        return match

    def update_all_ratings(self) -> dict[str, Glicko2Player]:
        """Update all player ratings based on match history"""
        # Group matches by player
        player_matches: dict[str, list[Glicko2Match]] = {}
        for player_id in self.players:
            player_matches[player_id] = [
                m
                for m in self.match_history
                if m.player1_id == player_id or m.player2_id == player_id
            ]

        # Update each player
        updated_players = {}
        for player_id, matches in player_matches.items():
            player = self.players[player_id]
            updated_player = self.system.update_rating(player, matches, self.players)
            updated_players[player_id] = updated_player
            self.players[player_id] = updated_player

        return updated_players

    def get_leaderboard(self, min_games: int = 0) -> list[Glicko2Player]:
        """Get leaderboard sorted by rating

        Args:
            min_games: Minimum games played to be included

        """
        eligible = [p for p in self.players.values() if p.games_played >= min_games]
        return sorted(eligible, key=lambda p: p.mu, reverse=True)
