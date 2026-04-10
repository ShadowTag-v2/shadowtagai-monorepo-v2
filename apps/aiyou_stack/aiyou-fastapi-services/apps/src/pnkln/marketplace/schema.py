"""
PNKLN Marketplace - Database Schema
Two-sided marketplace for AI superpowers and kernel chains

Revenue model:
- Platform fees: 20-30% of all transactions
- Publishing fees: $99/year per superpower
- Featured placement: $500-$5K/mo
- Enterprise bundles: $10K-$100K/year

Year 1 target: $100K revenue (50 superpowers @ $2K GMV avg, 20% take rate)
Year 5 target: $10M revenue (marketplace GMV $50M @ 20% take rate)
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Developer(Base):
    __tablename__ = "marketplace_developers"
    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    verified = Column(Boolean, default=False)
    revenue_share_pct = Column(Float, default=0.70)  # Developer keeps 70%


class Superpower(Base):
    __tablename__ = "marketplace_superpowers"
    id = Column(String, primary_key=True)
    developer_id = Column(String, ForeignKey("marketplace_developers.id"))
    title = Column(String)
    description = Column(Text)
    price_once = Column(Float, nullable=True)
    price_subscription = Column(Float, nullable=True)
    is_featured = Column(Boolean, default=False)

    installations = Column(Integer, default=0)
    rating_avg = Column(Float, default=0.0)


class Transaction(Base):
    __tablename__ = "marketplace_transactions"
    id = Column(String, primary_key=True)
    buyer_id = Column(String)  # User ID
    superpower_id = Column(String, ForeignKey("marketplace_superpowers.id"))
    amount = Column(Float)
    platform_fee = Column(Float)  # Calculated at transaction time
    developer_revenue = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)


class UserSuperpower(Base):
    """Record of installed superpower"""

    __tablename__ = "user_superpowers"
    user_id = Column(String, primary_key=True)
    superpower_id = Column(String, primary_key=True)
    installed_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)
