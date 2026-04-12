from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/api/v1/unified", tags=["Unified Ecosystem"])


class InferenceRequest(BaseModel):
    """Unified inference request across all models."""

    prompt: str
    model: str | None = "default"
    max_tokens: int = 512
    temperature: float = 0.7
    use_debate: bool = False
    debate_agents: int = 3
    debate_rounds: int = 2
    enable_kernels: bool = True
    trace_id: str | None = None
