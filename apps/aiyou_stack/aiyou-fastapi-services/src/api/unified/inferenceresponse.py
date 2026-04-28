# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/unified", tags=["Unified Ecosystem"])


class InferenceResponse(BaseModel):
    """Unified inference response with performance metrics."""

    response: str
    model_used: str
    latency_ms: float
    tokens_generated: int
    cost_usd: float
    gpu_savings_percent: float
    token_compression_ratio: float
    debate_used: bool = False
    consensus_score: float | None = None
    glicko_rating: float | None = None
    kernels_executed: list[str] = []
    audit_trail_bytes: int | None = None
    watermark_signature: str | None = None
