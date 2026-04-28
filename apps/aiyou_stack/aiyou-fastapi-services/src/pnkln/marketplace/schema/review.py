# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Review(Base):
    """User reviews and ratings"""

    __tablename__ = "marketplace_reviews"
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    superpower_id = Column(String(50), ForeignKey("marketplace_superpowers.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    title = Column(String(200))
    review_text = Column(Text)
    verified_purchase = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=False)
    developer_response = Column(Text)
    developer_responded_at = Column(DateTime)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (
        Index("idx_marketplace_reviews_superpower", "superpower_id"),
        Index("idx_marketplace_reviews_user", "user_id"),
        Index("idx_marketplace_reviews_rating", "rating"),
    )
