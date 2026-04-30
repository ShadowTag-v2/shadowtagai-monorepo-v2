"""Metric models for storing calculated analytics metrics"""

import uuid

from sqlalchemy import JSON, Column, DateTime, Float, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from src.database import Base


class Metric(Base):
    """Real-time metric tracking"""

    __tablename__ = "metrics"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Metric identification
    metric_name = Column(String(255), nullable=False, index=True)
    metric_type = Column(String(100), nullable=False)  # count, sum, avg, unique, etc.

    # Metric value
    value = Column(Float, nullable=False)

    # Dimensions
    dimensions = Column(JSON, default={})  # Key-value pairs for filtering/grouping

    # Time information
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # Metadata
    metadata = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes for efficient querying
    __table_args__ = (Index("idx_metric_name_timestamp", "metric_name", "timestamp"),)

    def __repr__(self):
        return f"<Metric(metric_name={self.metric_name}, value={self.value}, timestamp={self.timestamp})>"


class AggregatedMetric(Base):
    """Pre-aggregated metrics for faster dashboard queries"""

    __tablename__ = "aggregated_metrics"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Metric identification
    metric_name = Column(String(255), nullable=False, index=True)
    aggregation_type = Column(String(50), nullable=False)  # hourly, daily, weekly, monthly

    # Time period
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Aggregated values
    count = Column(Integer, default=0)
    sum = Column(Float, default=0.0)
    avg = Column(Float, default=0.0)
    min = Column(Float)
    max = Column(Float)
    unique_count = Column(Integer)

    # Dimensions
    dimensions = Column(JSON, default={})

    # Additional statistics
    percentile_50 = Column(Float)
    percentile_90 = Column(Float)
    percentile_95 = Column(Float)
    percentile_99 = Column(Float)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_agg_metric_name_period", "metric_name", "aggregation_type", "period_start"),
    )

    def __repr__(self):
        return f"<AggregatedMetric(metric_name={self.metric_name}, period_start={self.period_start}, count={self.count})>"
