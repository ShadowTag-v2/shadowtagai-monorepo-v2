# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""ScholarEval API — FastAPI endpoint for the 8-dimension quality framework.

Wraps the ScholarEvaluator library into a REST endpoint for CounselConduit.

Endpoint:
    POST /api/v1/evaluate — Evaluate a research discovery

Architecture:
    CounselConduit Frontend → FastAPI → ScholarEvaluator → 8-dimension scores
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.research.scholar_eval import ScholarEvaluator, ScholarEvalResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["research"])

# Singleton evaluator instance
_evaluator = ScholarEvaluator()


class EvaluateRequest(BaseModel):
  """Request body for research discovery evaluation."""

  discovery_id: str = Field(..., description="Unique identifier for the discovery")
  text: str = Field(..., min_length=10, description="Discovery text or abstract")
  citations: list[str] = Field(default_factory=list, description="Citation strings")
  methodology: str = Field(default="", description="Methodology description")
  p_values: list[float] = Field(
    default_factory=list, description="Statistical p-values"
  )


class DimensionScoreResponse(BaseModel):
  """Single dimension score in the response."""

  dimension: str
  score: float
  confidence: float
  evidence: str
  flags: list[str]


class EvaluateResponse(BaseModel):
  """Response from the evaluation endpoint."""

  discovery_id: str
  overall_score: float
  passed: bool
  recommendation: str
  dimensions: list[DimensionScoreResponse]


def _result_to_response(result: ScholarEvalResult) -> EvaluateResponse:
  """Convert internal dataclass to Pydantic response model."""
  return EvaluateResponse(
    discovery_id=result.discovery_id,
    overall_score=round(result.overall_score, 4),
    passed=result.passed,
    recommendation=result.recommendation,
    dimensions=[
      DimensionScoreResponse(
        dimension=d.dimension,
        score=round(d.score, 4),
        confidence=round(d.confidence, 4),
        evidence=d.evidence,
        flags=d.flags,
      )
      for d in result.dimensions
    ],
  )


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_discovery(request: EvaluateRequest) -> EvaluateResponse:
  """Evaluate a research discovery across 8 quality dimensions.

  Dimensions:
      1. Novelty — genuinely new or restating known results?
      2. Reproducibility — independently verifiable?
      3. Statistical Rigor — valid methods and p-values?
      4. Citation Grounding — claims supported by real references?
      5. Logical Coherence — argument flows without gaps?
      6. Practical Impact — real-world application?
      7. Ethical Compliance — no fabrication, bias, or harmful framing?
      8. Temporal Validity — based on current, non-retracted science?

  Returns:
      EvaluateResponse with scores, pass/fail, and recommendation.
  """
  try:
    result = _evaluator.evaluate(
      discovery_id=request.discovery_id,
      text=request.text,
      citations=request.citations or [],
      methodology=request.methodology,
      p_values=request.p_values or [],
    )
    logger.info(
      "Evaluated discovery %s: score=%.3f recommendation=%s",
      request.discovery_id,
      result.overall_score,
      result.recommendation,
    )
    return _result_to_response(result)
  except Exception as exc:
    logger.exception("Evaluation failed for %s", request.discovery_id)
    raise HTTPException(status_code=500, detail=f"Evaluation failed: {exc}") from exc


@router.get("/evaluate/health")
async def evaluate_health() -> dict[str, Any]:
  """Health check for the evaluation service."""
  return {
    "status": "healthy",
    "service": "scholar-eval",
    "version": "1.0.0",
    "dimensions": 8,
    "acceptance_threshold": 0.65,
  }
