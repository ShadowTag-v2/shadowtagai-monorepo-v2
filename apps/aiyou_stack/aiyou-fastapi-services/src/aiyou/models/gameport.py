"""GamePort gaming integration models.

Handles game catalog, sessions, and publisher partnerships.
"""

import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class GamePublisher(Base):
    """Game publisher/developer model."""

    __tablename__ = "gameport_publishers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False, unique=True, index=True)
    api_key = Column(String(100), unique=True, nullable=False)
    revenue_share_percentage = Column(Integer, default=50)  # Publisher gets 50%
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    games = relationship("Game", back_populates="publisher")

    def __repr__(self):
        return f"<GamePublisher(id={self.id}, name={self.name})>"


class Game(Base):
    """Game catalog model."""

    __tablename__ = "gameport_games"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    publisher_id = Column(
        String(36), ForeignKey("gameport_publishers.id"), nullable=False, index=True,
    )

    # Game metadata
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    cover_image_url = Column(String(1000))
    trailer_url = Column(String(1000))
    genre = Column(JSON)  # ["mmorpg", "fps"]
    tags = Column(JSON)

    # Integration level
    integration_type = Column(String(50), nullable=False, index=True)  # stream, api, deep
    launch_url = Column(String(1000))  # API endpoint or stream URL
    sdk_version = Column(String(20))

    # Pricing
    compute_fee_per_minute_cents = Column(Integer, default=1)  # $0.01/min
    transaction_fee_percentage = Column(Integer, default=20)  # 20% platform fee

    # Analytics
    total_sessions = Column(Integer, default=0)
    total_hours_played = Column(Integer, default=0)
    revenue_cents = Column(Integer, default=0)
    average_rating = Column(Numeric(3, 2))

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    publisher = relationship("GamePublisher", back_populates="games")
    sessions = relationship("GameSession", back_populates="game")

    def __repr__(self):
        return f"<Game(id={self.id}, title={self.title})>"


class GameSession(Base):
    """Active or completed gaming session."""

    __tablename__ = "gameport_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String(36), ForeignKey("gameport_games.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Session details
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)

    # Compute & cost
    gpu_node_id = Column(String(36), index=True)  # Which edge node hosted
    gpu_type = Column(String(50))  # L40S, H100, etc.
    compute_cost_cents = Column(Integer, default=0)

    # Quality metrics
    average_latency_ms = Column(Integer)
    average_fps = Column(Integer)
    disconnect_count = Column(Integer, default=0)

    # Revenue
    revenue_cents = Column(Integer, default=0)  # From compute fees + transactions

    # Status
    is_active = Column(Boolean, default=True, index=True)

    # Relationships
    game = relationship("Game", back_populates="sessions")
    user = relationship("User", back_populates="game_sessions")

    def __repr__(self):
        return f"<GameSession(id={self.id}, game_id={self.game_id}, started_at={self.started_at})>"
