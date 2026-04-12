from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/v1/unified", tags=["Unified Ecosystem"])


class AerospaceDeploymentRequest(BaseModel):
    """Request for aerospace edge mesh deployment analysis."""

    num_cell_towers: int = Field(ge=1, le=100000)
    num_vehicles: int = Field(ge=1, le=10000000)
    num_satellites: int = Field(ge=0, le=1000)
    deployment_months: int = Field(ge=1, le=120)
    uplink_type: str = "hybrid_redundant"
    gpu_config: str = "h100_dual"
