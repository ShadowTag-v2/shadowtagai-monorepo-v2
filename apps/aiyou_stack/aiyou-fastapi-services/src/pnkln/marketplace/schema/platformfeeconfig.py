from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    String,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PlatformFeeConfig(Base):
    """Platform fee configuration

    Allows dynamic fee adjustment based on:
    - Developer tier (new vs. established)
    - Superpower category
    - Transaction volume
    """

    __tablename__ = "marketplace_fee_config"
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    base_fee_pct = Column(Float, default=25.0)
    min_fee_pct = Column(Float, default=20.0)
    max_fee_pct = Column(Float, default=30.0)
    volume_discount_tiers = Column(JSON, default=list)
    category_fees = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
