# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Governance Gateway Data Models

Elegant, type-safe models for governance requests and responses.
Every field chosen deliberately. Nothing superfluous.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class RiskLevel(str, Enum):
    """ATP 5-19 Risk Classification"""

    EXTREMELY_HIGH = "extremely_high"  # E-H: Immediate OPA blocking
    HIGH = "high"  # H: OPA with logging
    MEDIUM = "medium"  # M: Agent evaluation
    LOW = "low"  # L: Agent with async audit


class DecisionPath(str, Enum):
    """Routing decision for governance requests"""

    FAST_PATH = "fast_path"  # OPA rule engine (<10ms)
    SLOW_PATH = "slow_path"  # Agent evaluation (2-5s)
    HYBRID = "hybrid"  # OPA + Agent verification


class DecisionOutcome(str, Enum):
    """Final governance decision"""

    APPROVED = "approved"
    DENIED = "denied"
    ESCALATED = "escalated"  # Requires human review
    DEFERRED = "deferred"  # Awaiting additional information


class GovernanceRequest(BaseModel):
    """
    Incoming governance decision request.

    Designed for clarity: every field essential, every type explicit.
    """

    request_id: str = Field(..., description="Unique request identifier")
    user_id: str = Field(..., description="Requesting user identifier")
    action: str = Field(..., description="Action requiring governance approval")
    resource: dict[str, Any] = Field(..., description="Resource being acted upon")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context for decision-making")

    # Risk indicators
    financial_value: float | None = Field(None, ge=0, description="USD value if applicable")
    data_sensitivity: str | None = Field(None, description="PII, PHI, confidential, public")
    urgency: str | None = Field(None, description="immediate, standard, low")

    # Metadata
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_system: str = Field(..., description="Originating system identifier")

    @field_validator("action")
    def action_not_empty(cls, v: str) -> str:
        """Ensure action is meaningful"""
        if not v or not v.strip():
            raise ValueError("Action cannot be empty")
        return v.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "request_id": "req_20251117_001",
                "user_id": "user_789",
                "action": "approve_expense",
                "resource": {"type": "expense", "id": "exp_12345", "amount": 5000.00, "category": "travel"},
                "context": {"department": "engineering", "project": "gke-migration"},
                "financial_value": 5000.00,
                "data_sensitivity": "internal",
                "urgency": "standard",
                "source_system": "expense-tracker-api",
            }
        }
    )


class RiskAssessment(BaseModel):
    """
    ATP 5-19 Risk Assessment Result.

    Probability × Severity → Risk Level
    """

    probability: str = Field(..., description="A-E scale (A=frequent, E=unlikely)")
    severity: str = Field(..., description="I-IV scale (I=catastrophic, IV=negligible)")
    risk_level: RiskLevel
    hazards: list[str] = Field(default_factory=list, description="Identified hazards")
    controls: list[str] = Field(default_factory=list, description="Recommended controls")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "probability": "C",
                "severity": "II",
                "risk_level": "medium",
                "hazards": ["Budget overrun risk", "Unauthorized approval"],
                "controls": ["Manager approval required", "Budget check"],
            }
        }
    )


class RoutingDecision(BaseModel):
    """
    How this request will be processed.

    Fast path = OPA rules (deterministic, <10ms)
    Slow path = Agent reasoning (contextual, 2-5s)
    """

    path: DecisionPath
    risk_assessment: RiskAssessment
    reason: str = Field(..., description="Why this path was chosen")
    estimated_latency_ms: int = Field(..., ge=0, description="Expected processing time")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "path": "slow_path",
                "risk_assessment": {
                    "probability": "C",
                    "severity": "II",
                    "risk_level": "medium",
                    "hazards": ["Budget overrun"],
                    "controls": ["Manager approval"],
                },
                "reason": "Medium risk requires contextual evaluation",
                "estimated_latency_ms": 2500,
            }
        }
    )


class GovernanceResponse(BaseModel):
    """
    Final governance decision with full provenance.

    Every decision traceable. Every reason cited.
    """

    request_id: str
    outcome: DecisionOutcome
    confidence: float = Field(..., ge=0, le=1, description="Decision confidence score")

    # Decision details
    reasoning: list[str] = Field(..., description="Step-by-step decision logic")
    policy_citations: list[str] = Field(default_factory=list, description="Specific policy sections applied")

    # Processing metadata
    path_taken: DecisionPath
    latency_ms: int = Field(..., ge=0, description="Actual processing time")
    model_used: str | None = Field(None, description="LLM model if agent path")

    # Trust & quality
    trust_score: float = Field(..., ge=0, le=1, description="Agent trust score")
    hallucination_check: bool = Field(default=True, description="Passed hallucination detection")

    # Audit trail
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    audit_id: str = Field(..., description="Immutable audit log entry ID")

    # Optional escalation
    escalation_required: bool = Field(default=False)
    escalation_reason: str | None = None
    assigned_reviewer: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "request_id": "req_20251117_001",
                "outcome": "approved",
                "confidence": 0.92,
                "reasoning": [
                    "Amount within user's approval limit ($10,000)",
                    "Budget available in project allocation",
                    "Category matches project scope",
                ],
                "policy_citations": ["POL-FIN-001 §3.2", "POL-EXP-005 §1.1"],
                "path_taken": "slow_path",
                "latency_ms": 2347,
                "model_used": "gemini-2.5-flash-002",
                "trust_score": 0.87,
                "hallucination_check": True,
                "timestamp": "2025-11-17T10:30:45Z",
                "audit_id": "audit_abc123def456",
                "escalation_required": False,
            }
        }
    )


class CircuitBreakerState(BaseModel):
    """
    Circuit breaker state for fallback management.

    Protects against cascade failures when agents misbehave.
    """

    state: str = Field(..., description="CLOSED, OPEN, or HALF_OPEN")
    failure_count: int = Field(0, ge=0)
    last_failure: datetime | None = None
    success_count: int = Field(0, ge=0)
    last_success: datetime | None = None

    threshold_failures: int = Field(5, description="Failures before opening")
    timeout_seconds: int = Field(60, description="Time before attempting recovery")


class AgentMetrics(BaseModel):
    """
    Real-time agent performance metrics.

    Used for circuit breaker decisions and trust scoring.
    """

    agent_id: str
    response_time_ms: float
    error_rate: float = Field(..., ge=0, le=1)
    confidence_avg: float = Field(..., ge=0, le=1)
    decisions_count: int = Field(..., ge=0)
    overrides_count: int = Field(0, ge=0, description="Human overrides of agent decisions")

    # Performance window
    window_start: datetime
    window_end: datetime
