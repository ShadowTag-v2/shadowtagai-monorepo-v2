# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Decision-specific data models for ATP 5-19 governance."""

from pydantic import BaseModel, Field
from typing import Any
from enum import IntEnum
from datetime import datetime, timezone


class RiskTier(IntEnum):
  """Risk classification tiers (1-5)."""

  TIER_1_MINIMAL = 1
  TIER_2_LOW = 2
  TIER_3_MODERATE = 3
  TIER_4_HIGH = 4
  TIER_5_CRITICAL = 5


class Violation(BaseModel):
  """Structured ATP 5-19 violation."""

  rule_id: str = Field(..., description="ATP 5-19 rule identifier")
  description: str
  severity: str = Field(
    ..., description="violation severity: minor, moderate, major, critical"
  )
  context: str | None = None
  suggested_action: str | None = None
  metadata: dict[str, Any] = Field(default_factory=dict)


class DecisionContext(BaseModel):
  """Raw decision context input (up to 50KB)."""

  content: str = Field(..., description="Decision context content")
  context_type: str = Field(
    default="text", description="Type of context: text, json, xml"
  )
  metadata: dict[str, Any] = Field(default_factory=dict)
  trace_id: str | None = None


class ViolationsScanOutput(BaseModel):
  """Output from kernel_1: ATP_519_scan."""

  violations: list[Violation]
  scan_metadata: dict[str, Any] = Field(default_factory=dict)
  total_violations: int = 0
  scan_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

  def model_post_init(self, __context):
    """Auto-calculate total violations."""
    self.total_violations = len(self.violations)


class JudgeSixClassification(BaseModel):
  """Output from kernel_2: judge_six_classify."""

  decision: bool = Field(..., description="Binary go/no-go decision")
  confidence: float = Field(..., ge=0.0, le=1.0)
  risk_tier: RiskTier
  reasoning: str | None = None


class AuditTrail(BaseModel):
  """Compressed audit trail from kernel_3."""

  compressed_data: bytes = Field(..., description="zstd compressed decision metadata")
  compression_ratio: float
  original_size_bytes: int
  compressed_size_bytes: int
  checksum: str = Field(..., description="SHA256 checksum of compressed data")


class DecisionResult(BaseModel):
  """Final decision result with full audit trail."""

  decision: bool
  confidence: float
  risk_tier: RiskTier
  violations: list[Violation]
  audit_trail: AuditTrail
  total_latency_ms: float
  total_cost_usd: float
  trace_id: str
  timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  kernel_metrics: dict[str, Any] = Field(default_factory=dict)
