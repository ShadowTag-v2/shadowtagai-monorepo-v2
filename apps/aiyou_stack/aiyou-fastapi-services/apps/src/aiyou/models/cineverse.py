"""CineVerse streaming platform models (Updated for Cor.18).

Handles content, creators, streams, subscriptions, and Verification Index.
"""

import uuid
from enum import StrEnum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class ContentType(StrEnum):
    """Content type enumeration."""

    MOVIE = "movie"
    SERIES = "series"
    EPISODE = "episode"
    SHORT = "short"
    LIVE = "live"
    INTERACTIVE = "interactive"
    CREATOR_UPLOAD = "creator_upload"  # Added for Creator Network


class Content(Base):
    """Content model for CineVerse streaming.

    Every piece of content is ShadowTag-verified for authenticity.
    """

    __tablename__ = "cineverse_content"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys
    creator_id = Column(String(36), ForeignKey("cineverse_creators.id"), nullable=False, index=True)

    # Content metadata
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    content_type = Column(SQLEnum(ContentType), nullable=False, index=True)
    duration_seconds = Column(Integer)
    release_date = Column(DateTime(timezone=True))

    # Media files
    video_url = Column(String(1000))
    thumbnail_url = Column(String(1000))
    trailer_url = Column(String(1000))

    # ShadowTag verified attributes
    shadowtag_signature = Column(String(500), nullable=False, index=True)
    shadowtag_chain_id = Column(String(100), nullable=False)
    shadowtag_verified_at = Column(DateTime(timezone=True), nullable=False)

    # AI Analysis & Safety
    ai_generated_score = Column(Integer)  # 0-100 likelihood
    content_safety_labels = Column(JSON)  # ["safe", "educational"]
    provenance_hash_trail = Column(JSON)  # List of previous edit hashes

    # Encoding & quality
    available_resolutions = Column(JSON)
    encoding_format = Column(String(50))
    hdr_available = Column(Boolean, default=False)

    # Metadata
    genres = Column(JSON)
    tags = Column(JSON)
    language = Column(String(10), index=True)
    subtitle_languages = Column(JSON)

    # Analytics & metrics
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    average_rating = Column(Numeric(3, 2))

    # Creator Network specific
    audience_energy_score = Column(Integer, default=0)  # Engagement quality metric
    trust_weighted_views = Column(Integer, default=0)  # Views filtered by bot detection

    # Revenue tracking
    price_cents = Column(Integer)
    revenue_cents = Column(Integer, default=0)

    # Status
    is_published = Column(Boolean, default=False, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    is_premium = Column(Boolean, default=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))

    # Relationships
    creator = relationship("Creator", back_populates="content")
    streams = relationship("Stream", back_populates="content")

    def __repr__(self):
        return f"<Content(id={self.id}, title={self.title}, type={self.content_type})>"


class Creator(Base):
    """Content creator model with Verification Index.
    """

    __tablename__ = "cineverse_creators"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Creator profile
    display_name = Column(String(200), nullable=False)
    channel_url = Column(String(200), unique=True, index=True)
    bio = Column(Text)
    avatar_url = Column(String(1000))
    banner_url = Column(String(1000))

    # Verification & Trust (Cor.18 Updates)
    is_verified = Column(Boolean, default=False, index=True)
    verified_at = Column(DateTime(timezone=True))

    # Creator Verification Index (CVI) components
    trust_score = Column(Integer, default=50)  # 0-100 Public trust score
    shadowtag_hash_history_score = Column(Integer, default=0)  # Provenance reliability
    audience_energy_rank = Column(Integer, default=0)  # "Cognition score"
    ai_authenticity_rank = Column(
        Integer, default=0,
    )  # 100 = Human Verified, 0 = Unmarked Synthetic

    # Revenue share settings
    revenue_share_percentage = Column(Integer, default=70)  # Cor.18 Base: 70%

    # Analytics
    subscriber_count = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    lifetime_revenue_cents = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="creator_profile")
    content = relationship("Content", back_populates="creator")

    def __repr__(self):
        return (
            f"<Creator(id={self.id}, display_name={self.display_name}, trust={self.trust_score})>"
        )


class Stream(Base):
    """Streaming session model.
    """

    __tablename__ = "cineverse_streams"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys
    content_id = Column(String(36), ForeignKey("cineverse_content.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), index=True)

    # Stream metadata
    resolution = Column(String(10))
    bitrate_kbps = Column(Integer)
    cdn_node_id = Column(String(36), index=True)  # Edge Node ID

    # Playback tracking
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    completion_percentage = Column(Integer)

    # Device & location
    device_type = Column(String(50))
    ip_address = Column(String(45))
    country_code = Column(String(2), index=True)

    # Engagement Quality
    attention_score = Column(Integer)  # Derived from client heuristics

    # Revenue attribution
    was_ad_supported = Column(Boolean, default=False)
    revenue_cents = Column(Integer, default=0)

    # Relationships
    content = relationship("Content", back_populates="streams")

    def __repr__(self):
        return f"<Stream(id={self.id}, content_id={self.content_id}, started_at={self.started_at})>"


class Subscription(Base):
    """User subscription to a Creator.
    """

    __tablename__ = "cineverse_subscriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    creator_id = Column(String(36), ForeignKey("cineverse_creators.id"), nullable=False, index=True)

    tier = Column(String(50))  # free, supporter, vip
    status = Column(String(20), default="active")  # active, expired, cancelled

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))

    price_cents = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    creator = relationship("Creator")

    def __repr__(self):
        return f"<Subscription(user_id={self.user_id}, creator_id={self.creator_id}, status={self.status})>"
