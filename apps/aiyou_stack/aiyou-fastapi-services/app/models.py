# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Pydantic models for request/response validation"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field


class UserRole(StrEnum):
    """User role enumeration"""

    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class UserBase(BaseModel):
    """Base user model"""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str | None = None
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    """User creation model"""

    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """User response model"""

    id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class TaskStatus(StrEnum):
    """Task status enumeration"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskBase(BaseModel):
    """Base task model"""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus = TaskStatus.PENDING
    priority: int = Field(default=1, ge=1, le=5)


class TaskCreate(TaskBase):
    """Task creation model"""

    user_id: int


class TaskResponse(TaskBase):
    """Task response model"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class HealthCheck(BaseModel):
    """Health check response"""

    status: str
    version: str
    timestamp: datetime
    database: str
    uptime: float


class MetricsResponse(BaseModel):
    """System metrics response"""

    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    active_connections: int
    total_requests: int
    avg_response_time_ms: float


class LoadTestConfig(BaseModel):
    """Load test configuration"""

    users: int = Field(default=100, ge=1, le=10000)
    spawn_rate: int = Field(default=10, ge=1, le=1000)
    duration: int = Field(default=60, ge=1)  # seconds
    target_url: str = "http://localhost:8000"


class LoadTestResult(BaseModel):
    """Load test result"""

    total_requests: int
    failed_requests: int
    success_rate: float
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    requests_per_second: float
    breaking_point_detected: bool
    breaking_point_users: int | None = None
    recommendations: list[str] = []
