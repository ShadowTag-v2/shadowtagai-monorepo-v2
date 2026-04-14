"""Performance metrics data models
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel
from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PerformanceMetric(Base):
    """Database model for performance metrics"""

    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, index=True)
    method = Column(String)
    duration = Column(Float)  # in seconds
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    status_code = Column(Integer)
    memory_usage = Column(Float, nullable=True)  # in MB
    cpu_usage = Column(Float, nullable=True)  # percentage
    query_params = Column(JSON, nullable=True)
    request_body_size = Column(Integer, nullable=True)
    response_body_size = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)


class Bottleneck(Base):
    """Database model for detected bottlenecks"""

    __tablename__ = "bottlenecks"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, index=True)
    line_number = Column(Integer, nullable=True)
    file_path = Column(String, nullable=True)
    function_name = Column(String)
    duration = Column(Float)  # time spent in this function
    call_count = Column(Integer)
    percentage = Column(Float)  # percentage of total request time
    detected_at = Column(DateTime, default=datetime.utcnow)
    severity = Column(String)  # low, medium, high, critical


class OptimizationSuggestion(Base):
    """Database model for optimization suggestions"""

    __tablename__ = "optimization_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, index=True)
    suggestion_type = Column(String)  # caching, query_optimization, etc.
    description = Column(Text)
    impact = Column(String)  # low, medium, high
    implementation = Column(Text, nullable=True)  # code suggestion
    created_at = Column(DateTime, default=datetime.utcnow)
    applied = Column(Integer, default=0)  # 0 = not applied, 1 = applied


# Pydantic models for API responses
class PerformanceMetricResponse(BaseModel):
    """Response model for performance metrics"""

    id: int
    endpoint: str
    method: str
    duration: float
    timestamp: datetime
    status_code: int
    memory_usage: float | None = None
    cpu_usage: float | None = None

    class Config:
        from_attributes = True


class BottleneckResponse(BaseModel):
    """Response model for bottlenecks"""

    id: int
    endpoint: str
    line_number: int | None
    file_path: str | None
    function_name: str
    duration: float
    call_count: int
    percentage: float
    severity: str
    detected_at: datetime

    class Config:
        from_attributes = True


class OptimizationSuggestionResponse(BaseModel):
    """Response model for optimization suggestions"""

    id: int
    endpoint: str
    suggestion_type: str
    description: str
    impact: str
    implementation: str | None
    created_at: datetime
    applied: bool

    class Config:
        from_attributes = True


class PerformanceReport(BaseModel):
    """Comprehensive performance report"""

    total_requests: int
    avg_response_time: float
    slowest_endpoints: list[dict[str, Any]]
    top_bottlenecks: list[BottleneckResponse]
    optimization_suggestions: list[OptimizationSuggestionResponse]
    cache_hit_rate: float | None = None
    time_period: str
