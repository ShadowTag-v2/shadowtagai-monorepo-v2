"""Analytics and revenue tracking models.

Captures user events, revenue attribution, and performance metrics.
"""

import uuid

from sqlalchemy import JSON, Column, DateTime, Index, Integer, Numeric, String
from sqlalchemy.sql import func

from ..database import Base


class RevenueEvent(Base):
    """Revenue event tracking.

    Every revenue-generating action is logged here for analytics.
    """

    __tablename__ = "analytics_revenue_events"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Event classification
    event_type = Column(
        String(100), nullable=False, index=True,
    )  # subscription, purchase, stream, etc.
    service = Column(String(50), nullable=False, index=True)  # cineverse, gameport, commerce

    # Attribution
    user_id = Column(String(36), index=True)
    entity_id = Column(String(36), index=True)  # content_id, product_id, etc.
    entity_type = Column(String(100), index=True)

    # Revenue
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default="USD")
    platform_fee_cents = Column(Integer, default=0)
    partner_revenue_cents = Column(Integer, default=0)

    # Context
    country_code = Column(String(2), index=True)
    device_type = Column(String(50))
    referral_source = Column(String(200))
    # Metadata
    event_metadata = Column(JSON)

    # Timestamp
    occurred_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True,
    )

    def __repr__(self):
        return f"<RevenueEvent(id={self.id}, type={self.event_type}, amount_cents={self.amount_cents})>"

    __table_args__ = (
        Index("idx_revenue_service_date", "service", "occurred_at"),
        Index("idx_revenue_user_date", "user_id", "occurred_at"),
    )


class UserEvent(Base):
    """User behavior event tracking.

    Logs user actions for funnel analysis and product optimization.
    """

    __tablename__ = "analytics_user_events"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Event details
    event_name = Column(String(200), nullable=False, index=True)
    user_id = Column(String(36), index=True)
    session_id = Column(String(36), index=True)

    # Context
    page_url = Column(String(1000))
    referrer_url = Column(String(1000))
    device_type = Column(String(50))
    browser = Column(String(100))
    os = Column(String(100))

    # Location
    country_code = Column(String(2), index=True)
    city = Column(String(100))
    ip_address = Column(String(45))

    # Properties
    properties = Column(JSON)  # Flexible event properties

    # Timestamp
    occurred_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True,
    )

    def __repr__(self):
        return f"<UserEvent(id={self.id}, event={self.event_name}, user_id={self.user_id})>"

    __table_args__ = (
        Index("idx_event_name_date", "event_name", "occurred_at"),
        Index("idx_user_event_date", "user_id", "occurred_at"),
    )


class PerformanceMetric(Base):
    """System performance metrics.

    Tracks latency, throughput, and reliability across services.
    """

    __tablename__ = "analytics_performance_metrics"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Metric identification
    metric_name = Column(String(200), nullable=False, index=True)
    service = Column(String(50), nullable=False, index=True)
    node_id = Column(String(36), index=True)  # Infrastructure node if applicable

    # Measurement
    value = Column(Numeric(precision=15, scale=5), nullable=False)
    unit = Column(String(50))  # ms, percent, requests/sec, etc.

    # Aggregation level
    aggregation_period = Column(String(20), index=True)  # minute, hour, day
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True))

    # Context
    tags = Column(JSON)  # Additional metadata

    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<PerformanceMetric(metric={self.metric_name}, value={self.value}{self.unit})>"

    __table_args__ = (Index("idx_metric_service_period", "metric_name", "service", "period_start"),)
