from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Developer(Base):
    """Developer/publisher account"""

    __tablename__ = "marketplace_developers"
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    display_name = Column(String(200), nullable=False)
    bio = Column(Text)
    website = Column(String(500))
    github = Column(String(200))
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    publishing_fee_paid = Column(Boolean, default=False)
    publishing_fee_expires = Column(DateTime)
    total_earnings = Column(Numeric(10, 2), default=0)
    pending_payout = Column(Numeric(10, 2), default=0)
    total_superpowers = Column(Integer, default=0)
    total_sales = Column(Integer, default=0)
    avg_rating = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    superpowers = relationship("Superpower", back_populates="developer")
    __table_args__ = (
        Index("idx_marketplace_developers_user_id", "user_id"),
        Index("idx_marketplace_developers_verified", "verified"),
    )
