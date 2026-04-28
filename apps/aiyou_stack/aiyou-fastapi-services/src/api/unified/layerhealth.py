# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from enum import StrEnum

from fastapi import APIRouter
from pydantic import BaseModel


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


router = APIRouter(prefix="/api/v1/unified", tags=["Unified Ecosystem"])


class LayerHealth(BaseModel):
    """Health status for individual layer."""

    name: str
    status: HealthStatus
    latency_ms: float | None = None
    message: str | None = None
