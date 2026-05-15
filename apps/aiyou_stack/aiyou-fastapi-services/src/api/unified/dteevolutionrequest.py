from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.evolution.dte import EvolutionStrategy

router = APIRouter(prefix="/api/v1/unified", tags=["Unified Ecosystem"])


class DTEEvolutionRequest(BaseModel):
    """Request for DTE self-evolution."""

    target: str = Field(description="What to evolve: 'prompt', 'kernel', 'agent'")
    current_version: str
    test_cases: list[dict[str, Any]]
    strategy: EvolutionStrategy = EvolutionStrategy.RCR_MAD
    baseline_accuracy: float = Field(ge=0.0, le=1.0)
