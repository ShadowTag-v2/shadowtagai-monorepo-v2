# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserSuperpower(Base):
    """User's installed/purchased superpowers

    Tracks which superpowers a user has access to
    """

    __tablename__ = "marketplace_user_superpowers"
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    superpower_id = Column(String(50), ForeignKey("marketplace_superpowers.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    activated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    usage_count = Column(Integer, default=0)
    usage_limit = Column(Integer)
    last_used_at = Column(DateTime)
    subscription_id = Column(String(50))
    auto_renew = Column(Boolean, default=True)
    transaction_id = Column(String(50), ForeignKey("marketplace_transactions.id"))
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (
        Index("idx_marketplace_user_superpowers_user", "user_id"),
        Index("idx_marketplace_user_superpowers_superpower", "superpower_id"),
        Index("idx_marketplace_user_superpowers_active", "is_active"),
    )
