from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field
from .layerhealth import HealthStatus, LayerHealth


router = APIRouter(prefix="/api/v1/unified", tags=["Unified Ecosystem"])


class SystemHealthResponse(BaseModel):
    """Complete system health across all 8 layers."""

    overall_status: HealthStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    layers: list[LayerHealth]
    gpu_utilization: float
    models_loaded: int
    active_users: int
    cost_savings_percent: float = Field(description="GPU cost savings vs baseline")
