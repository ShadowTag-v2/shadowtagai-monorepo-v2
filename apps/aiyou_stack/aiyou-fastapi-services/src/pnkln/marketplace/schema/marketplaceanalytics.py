# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MarketplaceAnalytics(Base):
    """Daily marketplace analytics snapshot"""

    __tablename__ = "marketplace_analytics"
    id = Column(String(50), primary_key=True)
    date = Column(DateTime, nullable=False)
    total_transactions = Column(Integer, default=0)
    gmv = Column(Numeric(10, 2), default=0)
    platform_revenue = Column(Numeric(10, 2), default=0)
    developer_revenue = Column(Numeric(10, 2), default=0)
    total_superpowers = Column(Integer, default=0)
    new_superpowers = Column(Integer, default=0)
    active_superpowers = Column(Integer, default=0)
    total_buyers = Column(Integer, default=0)
    new_buyers = Column(Integer, default=0)
    active_developers = Column(Integer, default=0)
    category_breakdown = Column(JSON, default=dict)
    pricing_model_breakdown = Column(JSON, default=dict)
    top_superpowers = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (Index("idx_marketplace_analytics_date", "date"),)
