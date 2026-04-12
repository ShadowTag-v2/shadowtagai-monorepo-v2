"""
Glicko-2 Rating System for AI Model Selection
Implements dynamic model performance tracking and selection
"""

import math
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Column, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Session

from ..database import Base


class TaskType(StrEnum):
    """Types of content moderation tasks"""

    IMAGE_MODERATION = "image_moderation"
    VIDEO_MODERATION = "video_moderation"
    TEXT_MODERATION = "text_moderation"
    NSFW_DETECTION = "nsfw_detection"
    COPYRIGHT_CHECK = "copyright_check"
    POLICY_INTERPRETATION = "policy_interpretation"
    METADATA_GENERATION = "metadata_generation"


@dataclass
class Glicko2Player:
    """
    Glicko-2 rating system implementation for AI model performance tracking

    Based on: http://www.glicko.net/glicko/glicko2.pdf

    Attributes:
        mu: Rating (default 1500)
        phi: Rating deviation (uncertainty, default 350)
        sigma: Volatility (consistency, default 0.06)
    """

    mu: float = 1500.0
    phi: float = 350.0
    sigma: float = 0.06

    # System constant (constrains volatility changes)
    tau: float = 0.5

    # Convergence tolerance for rating updates
    tol: float = 1e-6

    def get_rating(self) -> float:
        """Get current rating"""
        return self.mu

    def get_rd(self) -> float:
        """Get rating deviation (uncertainty)"""
        return self.phi

    def get_volatility(self) -> float:
        """Get volatility (consistency)"""
        return self.sigma

    def scale_down(self) -> tuple[float, float]:
        """Convert to Glicko-2 scale"""
        mu_scaled = (self.mu - 1500) / 173.7178
        phi_scaled = self.phi / 173.7178
        return mu_scaled, phi_scaled

    def scale_up(self, mu_scaled: float, phi_scaled: float):
        """Convert back to Glicko scale"""
        self.mu = mu_scaled * 173.7178 + 1500
        self.phi = phi_scaled * 173.7178

    def update(
        self, opponents: list["Glicko2Player"], scores: list[float], task_type: str | None = None
    ):
        """
        Update rating based on match results

        Args:
            opponents: List of opponent players (other AI models)
            scores: List of scores (1.0 = win, 0.5 = draw, 0.0 = loss)
            task_type: Optional task type for tracking
        """
        if not opponents or len(opponents) != len(scores):
            raise ValueError("Opponents and scores must have same length")

        # Scale down to Glicko-2 scale
        mu, phi = self.scale_down()

        # Opponent ratings
        opponent_ratings = []
        for opp in opponents:
            opp_mu, opp_phi = opp.scale_down()
            opponent_ratings.append((opp_mu, opp_phi))

        # Step 3: Compute v (estimated variance)
        v = self._compute_v(mu, opponent_ratings)

        # Step 4: Compute Delta (improvement in rating)
        delta = self._compute_delta(mu, opponent_ratings, scores, v)

        # Step 5: Update volatility (sigma)
        sigma_new = self._compute_new_volatility(phi, v, delta)

        # Step 6: Update phi (rating deviation)
        phi_star = math.sqrt(phi**2 + sigma_new**2)

        # Step 7: Update mu and phi
        phi_new = 1 / math.sqrt(1 / phi_star**2 + 1 / v)
        mu_new = mu + phi_new**2 * sum(
            self._g(opp_phi) * (score - self._E(mu, opp_mu, opp_phi))
            for (opp_mu, opp_phi), score in zip(opponent_ratings, scores, strict=False)
        )

        # Scale back up
        self.scale_up(mu_new, phi_new)
        self.sigma = sigma_new

    def _g(self, phi: float) -> float:
        """Glicko-2 g function"""
        return 1 / math.sqrt(1 + 3 * phi**2 / math.pi**2)

    def _E(self, mu: float, mu_j: float, phi_j: float) -> float:
        """Expected score against opponent j"""
        return 1 / (1 + math.exp(-self._g(phi_j) * (mu - mu_j)))

    def _compute_v(self, mu: float, opponents: list[tuple[float, float]]) -> float:
        """Compute estimated variance of rating"""
        v_inv = sum(
            self._g(opp_phi) ** 2
            * self._E(mu, opp_mu, opp_phi)
            * (1 - self._E(mu, opp_mu, opp_phi))
            for opp_mu, opp_phi in opponents
        )
        return 1 / v_inv if v_inv > 0 else float("inf")

    def _compute_delta(
        self, mu: float, opponents: list[tuple[float, float]], scores: list[float], v: float
    ) -> float:
        """Compute improvement in rating"""
        return v * sum(
            self._g(opp_phi) * (score - self._E(mu, opp_mu, opp_phi))
            for (opp_mu, opp_phi), score in zip(opponents, scores, strict=False)
        )

    def _compute_new_volatility(self, phi: float, v: float, delta: float) -> float:
        """
        Compute new volatility using Illinois algorithm
        This is the complex part of Glicko-2
        """
        # Step 5.1
        alpha = math.log(self.sigma**2)

        # Step 5.2: Define f(x)
        def f(x: float) -> float:
            exp_x = math.exp(x)
            phi2 = phi**2

            term1 = (exp_x * (delta**2 - phi2 - v - exp_x)) / (2 * (phi2 + v + exp_x) ** 2)
            term2 = (x - alpha) / self.tau**2

            return term1 - term2

        # Step 5.3: Initial values
        if delta**2 > phi**2 + v:
            B = math.log(delta**2 - phi**2 - v)
        else:
            k = 1
            while f(alpha - k * self.tau) < 0:
                k += 1
            B = alpha - k * self.tau

        # Step 5.4: Illinois algorithm iteration
        A = alpha
        f_A = f(A)
        f_B = f(B)

        while abs(B - A) > self.tol:
            # Step 5.4a
            C = A + (A - B) * f_A / (f_B - f_A)
            f_C = f(C)

            # Step 5.4b
            if f_C * f_B < 0:
                A = B
                f_A = f_B
            else:
                f_A = f_A / 2

            B = C
            f_B = f_C

        # Step 5.5
        return math.exp(A / 2)


class ModelRating(Base):
    """
    Track Glicko-2 ratings for AI models across different task types
    """

    __tablename__ = "model_ratings"

    id = Column(String(36), primary_key=True)

    # Model identification
    model_name = Column(
        String(100), nullable=False, index=True
    )  # "gemini-1.5-pro", "claude-3.5-sonnet"
    model_version = Column(String(50))
    task_type = Column(String(50), nullable=False, index=True)

    # Glicko-2 parameters
    mu = Column(Float, default=1500.0, nullable=False)  # Rating
    phi = Column(Float, default=350.0, nullable=False)  # Rating deviation
    sigma = Column(Float, default=0.06, nullable=False)  # Volatility

    # Performance tracking
    total_matches = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)

    # Recent performance (last 100 matches)
    recent_accuracy = Column(Float)  # 0.0-1.0
    recent_cost_per_match = Column(Float)  # USD
    recent_latency_p95 = Column(Integer)  # milliseconds

    # Cost-effectiveness score
    cost_adjusted_rating = Column(Float)  # mu / (cost * latency_factor)

    # Metadata
    last_match_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_model_task_rating", "task_type", "mu"),
        Index("idx_model_cost_rating", "task_type", "cost_adjusted_rating"),
    )


class ModelMatch(Base):
    """
    Record of model performance comparison (match result)
    """

    __tablename__ = "model_matches"

    id = Column(String(36), primary_key=True)

    # Match participants
    model_a = Column(String(100), nullable=False, index=True)
    model_b = Column(String(100), nullable=False, index=True)
    task_type = Column(String(50), nullable=False, index=True)

    # Match result (from ground truth or human evaluation)
    winner = Column(String(100))  # model_a, model_b, or "draw"
    score_a = Column(Float, nullable=False)  # 0.0-1.0
    score_b = Column(Float, nullable=False)  # 0.0-1.0

    # Performance details
    latency_a_ms = Column(Integer)
    latency_b_ms = Column(Integer)
    cost_a_cents = Column(Integer)
    cost_b_cents = Column(Integer)

    # Ground truth
    content_id = Column(String(36), index=True)
    human_decision = Column(String(50))  # The "correct" answer
    model_a_decision = Column(String(50))
    model_b_decision = Column(String(50))

    # Match metadata
    match_date = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("idx_match_date", "match_date"),
        Index("idx_match_task", "task_type", "match_date"),
    )


class GlickoModelSelector:
    """
    Select best AI model for each task using Glicko-2 ratings
    """

    def __init__(self, db: Session):
        self.db = db
        self._cache = {}  # Cache recent ratings

    def get_best_model(
        self,
        task_type: TaskType,
        optimize_for: str = "accuracy",  # "accuracy", "cost", "latency", "balanced"
    ) -> dict[str, any]:
        """
        Select best model for task type

        Args:
            task_type: Type of moderation task
            optimize_for: Optimization criterion

        Returns:
            {
                "model_name": str,
                "rating": float,
                "confidence": float (based on phi),
                "expected_cost": float,
                "expected_latency": int
            }
        """
        # Get all models for this task type
        ratings = self.db.query(ModelRating).filter(ModelRating.task_type == task_type.value).all()

        if not ratings:
            # No ratings yet, return default
            return self._get_default_model(task_type)

        # Select based on optimization criterion
        if optimize_for == "accuracy":
            best = max(ratings, key=lambda r: r.mu)
        elif optimize_for == "cost":
            best = min(ratings, key=lambda r: r.recent_cost_per_match or float("inf"))
        elif optimize_for == "latency":
            best = min(ratings, key=lambda r: r.recent_latency_p95 or float("inf"))
        else:  # balanced
            best = max(ratings, key=lambda r: r.cost_adjusted_rating or 0)

        return {
            "model_name": best.model_name,
            "rating": best.mu,
            "confidence": 1 / (1 + best.phi / 350),  # Normalize confidence
            "expected_cost": best.recent_cost_per_match or 0,
            "expected_latency": best.recent_latency_p95 or 0,
            "wins": best.wins,
            "total_matches": best.total_matches,
            "win_rate": best.wins / best.total_matches if best.total_matches > 0 else 0,
        }

    def record_match(
        self,
        model_a_name: str,
        model_b_name: str,
        task_type: TaskType,
        winner: str,
        performance_data: dict[str, any],
    ):
        """
        Record match result and update ratings

        Args:
            model_a_name: First model name
            model_b_name: Second model name
            task_type: Task type
            winner: "model_a", "model_b", or "draw"
            performance_data: Cost, latency, accuracy data
        """
        # Get or create ratings
        rating_a = self._get_or_create_rating(model_a_name, task_type)
        rating_b = self._get_or_create_rating(model_b_name, task_type)

        # Create Glicko2Player instances
        player_a = Glicko2Player(mu=rating_a.mu, phi=rating_a.phi, sigma=rating_a.sigma)
        player_b = Glicko2Player(mu=rating_b.mu, phi=rating_b.phi, sigma=rating_b.sigma)

        # Determine scores
        if winner == "model_a":
            score_a, score_b = 1.0, 0.0
        elif winner == "model_b":
            score_a, score_b = 0.0, 1.0
        else:  # draw
            score_a, score_b = 0.5, 0.5

        # Update ratings
        player_a.update([player_b], [score_a])
        player_b.update([player_a], [score_b])

        # Save updated ratings
        rating_a.mu = player_a.mu
        rating_a.phi = player_a.phi
        rating_a.sigma = player_a.sigma
        rating_a.total_matches += 1
        if winner == "model_a":
            rating_a.wins += 1
        elif winner == "draw":
            rating_a.draws += 1
        else:
            rating_a.losses += 1
        rating_a.last_match_at = datetime.utcnow()

        rating_b.mu = player_b.mu
        rating_b.phi = player_b.phi
        rating_b.sigma = player_b.sigma
        rating_b.total_matches += 1
        if winner == "model_b":
            rating_b.wins += 1
        elif winner == "draw":
            rating_b.draws += 1
        else:
            rating_b.losses += 1
        rating_b.last_match_at = datetime.utcnow()

        # Update cost-adjusted ratings
        rating_a.cost_adjusted_rating = self._compute_cost_adjusted_rating(
            rating_a.mu,
            performance_data.get("cost_a_cents", 0) / 100.0,
            performance_data.get("latency_a_ms", 1000),
        )
        rating_b.cost_adjusted_rating = self._compute_cost_adjusted_rating(
            rating_b.mu,
            performance_data.get("cost_b_cents", 0) / 100.0,
            performance_data.get("latency_b_ms", 1000),
        )

        self.db.commit()

        # Record match
        match = ModelMatch(
            id=str(uuid.uuid4()),
            model_a=model_a_name,
            model_b=model_b_name,
            task_type=task_type.value,
            winner=winner,
            score_a=score_a,
            score_b=score_b,
            **performance_data,
        )
        self.db.add(match)
        self.db.commit()

    def _get_or_create_rating(self, model_name: str, task_type: TaskType) -> ModelRating:
        """Get existing rating or create new one"""
        rating = (
            self.db.query(ModelRating)
            .filter(ModelRating.model_name == model_name, ModelRating.task_type == task_type.value)
            .first()
        )

        if not rating:
            import uuid

            rating = ModelRating(
                id=str(uuid.uuid4()), model_name=model_name, task_type=task_type.value
            )
            self.db.add(rating)
            self.db.commit()

        return rating

    def _compute_cost_adjusted_rating(self, mu: float, cost_usd: float, latency_ms: int) -> float:
        """
        Compute cost-adjusted rating
        Higher rating, lower cost, lower latency = better score
        """
        # Normalize latency (penalize >2s heavily)
        latency_factor = 1.0 / (1.0 + latency_ms / 2000.0)

        # Normalize cost (penalize >$0.05 per request)
        cost_factor = 1.0 / (1.0 + cost_usd / 0.05)

        # Combined score
        return mu * latency_factor * cost_factor

    def _get_default_model(self, task_type: TaskType) -> dict[str, any]:
        """Return default model when no ratings exist"""
        defaults = {
            TaskType.IMAGE_MODERATION: "gemini-1.5-pro-vision",
            TaskType.VIDEO_MODERATION: "gemini-1.5-pro-vision",
            TaskType.TEXT_MODERATION: "claude-3.5-sonnet",
            TaskType.NSFW_DETECTION: "nsfw-detector-v4",
            TaskType.COPYRIGHT_CHECK: "copyright-matcher-v2",
            TaskType.POLICY_INTERPRETATION: "claude-3.5-sonnet",
            TaskType.METADATA_GENERATION: "gemini-1.5-flash",
        }

        return {
            "model_name": defaults.get(task_type, "gemini-1.5-pro"),
            "rating": 1500.0,
            "confidence": 0.3,  # Low confidence initially
            "expected_cost": 0.015,
            "expected_latency": 1000,
            "wins": 0,
            "total_matches": 0,
            "win_rate": 0.0,
        }


# Import at end to avoid circular imports
import uuid
