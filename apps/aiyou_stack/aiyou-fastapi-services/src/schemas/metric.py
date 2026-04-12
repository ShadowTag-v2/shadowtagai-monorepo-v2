"""Metric schemas"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class MetricResponse(BaseModel):
    """Schema for metric response"""

    id: UUID
    metric_name: str
    metric_type: str
    value: float
    dimensions: dict[str, Any]
    timestamp: datetime
    metadata: dict[str, Any]

    class Config:
        from_attributes = True


class AggregatedMetricResponse(BaseModel):
    """Schema for aggregated metric response"""

    id: UUID
    metric_name: str
    aggregation_type: str
    period_start: datetime
    period_end: datetime
    count: int
    sum: float
    avg: float
    min: float | None
    max: float | None
    unique_count: int | None
    dimensions: dict[str, Any]
    percentile_50: float | None
    percentile_90: float | None
    percentile_95: float | None
    percentile_99: float | None

    class Config:
        from_attributes = True
