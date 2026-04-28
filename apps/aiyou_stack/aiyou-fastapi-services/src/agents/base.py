# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Base agent framework implementing ADK integration for governance decisions.

Provides foundational agent interface with deterministic guardrails,
streaming support, and comprehensive metrics tracking.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class DecisionStatus(StrEnum):
    """Decision outcome status."""

    APPROVED = "APPROVED"
    DENIED = "DENIED"
    ESCALATED = "ESCALATED"
    ERROR = "ERROR"


class RiskLevel(StrEnum):
    """ATP 5-19 risk levels."""

    EXTREMELY_HIGH = "EH"
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"


@dataclass
class AgentMetrics:
    """Performance and cost metrics for agent execution."""

    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    latency_ms: int | None = None
    ttft_ms: int | None = None  # Time to first token
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    cost_usd: float = 0.0
    cached_savings_usd: float = 0.0
    model_used: str = ""
    cache_hit: bool = False

    def finalize(self) -> None:
        """Calculate final metrics."""
        self.end_time = time.time()
        self.latency_ms = int((self.end_time - self.start_time) * 1000)


class PolicyReference(BaseModel):
    """Reference to policy document section."""

    policy_id: str
    section: str
    clause: str | None = None
    effective_date: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class GovernanceDecision(BaseModel):
    """Structured governance decision output."""

    decision_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: DecisionStatus
    confidence_score: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel | None = None

    # Decision details
    reasoning_trace: list[str] = Field(default_factory=list)
    policy_references: list[PolicyReference] = Field(default_factory=list)
    evidence_snippets: list[str] = Field(default_factory=list)

    # Context
    user_id: str | None = None
    resource_id: str | None = None
    action_type: str = ""

    # Metrics
    metrics: dict[str, Any] | None = None

    # Escalation
    requires_escalation: bool = False
    escalation_reason: str | None = None

    # Trust scoring (GaaS)
    trust_score: float | None = Field(default=None, ge=0.0, le=1.0)
    enforcement_mode: str | None = None  # "coercive", "normative", "adaptive"

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class BaseGovernanceAgent(ABC):
    """Abstract base class for governance agents.

    Implements core interface for policy-based decision making with
    metrics tracking, error handling, and extensibility hooks.
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        model: str = "gemini-3.1-flash-lite-preview",
        temperature: float = 0.1,
        max_input_tokens: int = 1500,
        max_output_tokens: int = 300,
    ):
        self.agent_id = agent_id
        self.name = name
        self.model = model
        self.temperature = temperature
        self.max_input_tokens = max_input_tokens
        self.max_output_tokens = max_output_tokens
        self.metrics = AgentMetrics(model_used=model)

    @abstractmethod
    async def evaluate(
        self,
        request: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> GovernanceDecision:
        """Evaluate governance request and return decision.

        Args:
            request: Governance request containing action, resource, user context
            context: Additional context for decision making

        Returns:
            Structured governance decision with reasoning and references

        """

    @abstractmethod
    async def get_policy_context(self, request: dict[str, Any]) -> list[str]:
        """Retrieve relevant policy context for request.

        Args:
            request: Governance request

        Returns:
            List of relevant policy document snippets

        """

    def validate_request(self, request: dict[str, Any]) -> bool:
        """Validate request structure and required fields.

        Args:
            request: Request to validate

        Returns:
            True if valid, raises ValueError otherwise

        """
        required_fields = ["action", "resource"]
        for field in required_fields:  # noqa: F402
            if field not in request:
                raise ValueError(f"Missing required field: {field}")
        return True

    async def _calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
    ) -> tuple[float, float]:
        """Calculate cost and savings for model inference.

        Pricing (per 1M tokens):
        - Flash-Lite: $0.10 input, $0.40 output
        - Flash: $0.30 input, $2.50 output
        - Pro: $1.25 input, $10.00 output

        Args:
            input_tokens: Input token count
            output_tokens: Output token count
            cached_tokens: Cached token count

        Returns:
            Tuple of (cost_usd, cached_savings_usd)

        """
        pricing = {
            "gemini-3.1-flash-lite-preview-lite": (0.10, 0.40),
            "gemini-3.1-flash-lite-preview": (0.30, 2.50),
            "gemini-3.1-flash-lite-preview": (1.25, 10.00),  # noqa: F601
        }

        input_price, output_price = pricing.get(
            self.model, pricing["gemini-3.1-flash-lite-preview"]
        )

        # Calculate base cost
        uncached_input = max(0, input_tokens - cached_tokens)
        cost = (uncached_input * input_price + output_tokens * output_price) / 1_000_000

        # Calculate savings from caching (90% discount on cached tokens)
        savings = (cached_tokens * input_price * 0.90) / 1_000_000

        return cost, savings

    def _should_escalate(
        self,
        confidence: float,
        risk_level: RiskLevel | None,
        escalation_threshold: float = 0.6,
    ) -> tuple[bool, str | None]:
        """Determine if decision requires human escalation.

        Args:
            confidence: Confidence score
            risk_level: Assessed risk level
            escalation_threshold: Minimum confidence threshold

        Returns:
            Tuple of (should_escalate, reason)

        """
        if confidence < escalation_threshold:
            return True, f"Low confidence: {confidence:.2f} < {escalation_threshold}"

        if risk_level in [RiskLevel.EXTREMELY_HIGH, RiskLevel.HIGH]:
            return True, f"High risk level: {risk_level.value}"

        return False, None

    async def _apply_guardrails(
        self,
        decision: GovernanceDecision,
    ) -> GovernanceDecision:
        """Apply deterministic guardrails to agent decision.

        Implements safety checks that override model output if needed.

        Args:
            decision: Raw agent decision

        Returns:
            Decision with guardrails applied

        """
        # Confidence threshold check
        if decision.confidence_score < 0.5:
            decision.requires_escalation = True
            decision.escalation_reason = (
                decision.escalation_reason or "Confidence below safety threshold"
            )

        # Ensure evidence for high-stakes decisions
        if decision.status == DecisionStatus.DENIED and not decision.evidence_snippets:
            decision.requires_escalation = True
            decision.escalation_reason = "DENIED decision requires evidence"

        return decision

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for this agent."""
        self.metrics.finalize()
        return {
            "agent_id": self.agent_id,
            "model": self.model,
            "latency_ms": self.metrics.latency_ms,
            "ttft_ms": self.metrics.ttft_ms,
            "input_tokens": self.metrics.input_tokens,
            "output_tokens": self.metrics.output_tokens,
            "cached_tokens": self.metrics.cached_tokens,
            "cost_usd": self.metrics.cost_usd,
            "cached_savings_usd": self.metrics.cached_savings_usd,
            "cache_hit": self.metrics.cache_hit,
        }
