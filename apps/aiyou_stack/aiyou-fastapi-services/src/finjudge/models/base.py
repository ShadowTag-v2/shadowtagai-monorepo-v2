# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""FinJudge Base Models
Pydantic models for financial governance decisions
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

import uuid_utils as uuid
from pydantic import BaseModel, Field

# ============================================================================
# Enums
# ============================================================================


class DecisionType(StrEnum):
    """Financial decision types"""

    TRADE_APPROVAL = "trade_approval"
    RISK_ASSESSMENT = "risk_assessment"
    COMPLIANCE_CHECK = "compliance_check"
    PORTFOLIO_REBALANCE = "portfolio_rebalance"
    LIMIT_BREACH = "limit_breach"
    COUNTERPARTY_APPROVAL = "counterparty_approval"
    INSTRUMENT_AUTHORIZATION = "instrument_authorization"
    STRATEGY_VALIDATION = "strategy_validation"


class DecisionOutcome(StrEnum):
    """Ruling decisions"""

    APPROVE = "APPROVE"
    DENY = "DENY"
    APPROVE_WITH_CONDITIONS = "APPROVE_WITH_CONDITIONS"
    ESCALATE = "ESCALATE"
    DEFER = "DEFER"


class Probability(StrEnum):
    """ATP 5-19 Probability Levels"""

    A = "A"  # Frequent: ≥80%
    B = "B"  # Likely: 50-79%
    C = "C"  # Occasional: 20-49%
    D = "D"  # Seldom: 5-19%
    E = "E"  # Unlikely: <5%


class Severity(StrEnum):
    """ATP 5-19 Severity Levels"""

    I = "I"  # Catastrophic: >$10M loss  # noqa: E741
    II = "II"  # Critical: $1M-$10M loss
    III = "III"  # Moderate: $100K-$1M loss
    IV = "IV"  # Negligible: <$100K loss


class RiskLevel(StrEnum):
    """ATP 5-19 Risk Levels"""

    EH = "EH"  # Extremely High
    H = "H"  # High
    M = "M"  # Medium
    L = "L"  # Low


class EvidenceType(StrEnum):
    """Evidence types"""

    MARKET_DATA = "market_data"
    RISK_METRIC = "risk_metric"
    COMPLIANCE_DOC = "compliance_doc"
    PRECEDENT = "precedent"
    MODEL_OUTPUT = "model_output"
    HISTORICAL_PERFORMANCE = "historical_performance"
    CREDIT_RATING = "credit_rating"
    REGULATORY_FILING = "regulatory_filing"


class Urgency(StrEnum):
    """Request urgency levels"""

    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class Liquidity(StrEnum):
    """Market liquidity states"""

    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    STRESSED = "stressed"


class MarketRegime(StrEnum):
    """Market regime types"""

    NORMAL = "normal"
    CRISIS = "crisis"
    RECOVERY = "recovery"
    EXPANSION = "expansion"


class ComplianceStatus(StrEnum):
    """Compliance check status"""

    COMPLIANT = "compliant"
    VIOLATION = "violation"
    WARNING = "warning"
    UNCLEAR = "unclear"


# ============================================================================
# Sub-Models
# ============================================================================


class MarketConditions(BaseModel):
    """Market state at decision time"""

    volatility: float | None = Field(None, description="Market volatility metric")
    liquidity: Liquidity | None = Field(None, description="Liquidity state")
    regime: MarketRegime | None = Field(None, description="Market regime")


class DecisionContext(BaseModel):
    """Decision request context"""

    timestamp: datetime = Field(..., description="Request timestamp")
    entity: str = Field(..., description="Trading desk, fund, counterparty")
    purpose: str = Field(..., min_length=10, description="Business rationale")
    market_conditions: MarketConditions | None = None
    urgency: Urgency = Field(default=Urgency.NORMAL, description="Request urgency")


class Evidence(BaseModel):
    """Supporting evidence item"""

    type: EvidenceType = Field(..., description="Evidence type")
    source: str = Field(..., description="Evidence source (Bloomberg, Reuters, etc.)")
    data: dict[str, Any] = Field(..., description="Evidence payload")
    confidence: float = Field(default=100.0, ge=0, le=100, description="Evidence quality (0-100)")
    timestamp: datetime | None = Field(None, description="Evidence collection time")


class RiskLimits(BaseModel):
    """Risk constraint limits"""

    var_limit: float | None = Field(None, description="Value at Risk limit (USD)")
    position_limit: float | None = Field(None, description="Max position size")
    concentration_limit: float | None = Field(None, description="Max % of portfolio")
    stop_loss: float | None = Field(None, description="Stop loss threshold")


class Constraints(BaseModel):
    """Decision constraints"""

    regulatory: list[str] = Field(default_factory=list, description="Applicable regulations")
    risk_limits: RiskLimits | None = None
    policy_rules: list[str] = Field(default_factory=list, description="Internal policy IDs")
    max_exposure: float | None = Field(None, description="Maximum exposure (USD)")
    time_horizon: str | None = Field(None, description="Decision time horizon")


class Precedent(BaseModel):
    """Historical precedent reference"""

    ruling_id: str = Field(..., description="Past ruling identifier")
    similarity: float = Field(..., ge=0, le=100, description="Similarity score")
    outcome: str = Field(..., description="Past outcome")


class Rationale(BaseModel):
    """Ruling rationale (Supreme Court format)"""

    summary: str = Field(..., min_length=50, description="1-3 paragraph explanation")
    key_factors: list[str] = Field(..., min_items=1, description="Critical factors")
    precedents: list[Precedent] = Field(default_factory=list, description="Similar rulings")
    dissent: str | None = Field(None, description="Minority opinion")
    legal_basis: list[str] = Field(default_factory=list, description="Legal citations")


class QuantitativeRisk(BaseModel):
    """Quantitative risk metrics"""

    var_95: float | None = Field(None, description="95% Value at Risk (USD)")
    expected_loss: float | None = Field(None, description="Expected loss (USD)")
    worst_case: float | None = Field(None, description="Worst-case loss (USD)")


class RiskAssessment(BaseModel):
    """ATP 5-19 risk assessment"""

    probability: Probability = Field(..., description="Probability level (A-E)")
    severity: Severity = Field(..., description="Severity level (I-IV)")
    level: RiskLevel = Field(..., description="Risk level (EH/H/M/L)")
    mitigation: list[str] = Field(default_factory=list, description="Mitigation measures")
    residual_risk: RiskLevel | None = Field(None, description="Risk after mitigation")
    quantitative: QuantitativeRisk | None = None


class Condition(BaseModel):
    """Approval condition"""

    condition: str = Field(..., description="Condition description")
    mandatory: bool = Field(..., description="Is condition mandatory")
    deadline: datetime | None = Field(None, description="Condition deadline")
    responsible_party: str | None = Field(None, description="Responsible entity")


class AuditTrail(BaseModel):
    """Decision audit trail"""

    evidence_reviewed: int = Field(..., ge=0, description="Evidence items analyzed")
    rules_applied: list[str] = Field(..., description="Rules applied")
    computation_time_ms: float = Field(..., ge=0, description="Computation time (ms)")
    model_version: str = Field(default="v0.1.0", description="FinJudge version")
    reviewer: str | None = Field(None, description="Human reviewer ID")


class ComplianceFlag(BaseModel):
    """Compliance assessment flag"""

    regulation: str = Field(..., description="Regulation identifier")
    status: ComplianceStatus = Field(..., description="Compliance status")
    details: str = Field(..., description="Status details")


class FinancialImpact(BaseModel):
    """Financial impact estimates"""

    estimated_pnl: float | None = Field(None, description="Expected P&L (USD)")
    capital_requirement: float | None = Field(None, description="Required capital (USD)")
    cost: float | None = Field(None, description="Transaction cost (USD)")


# ============================================================================
# Main Models
# ============================================================================


class DecisionRequest(BaseModel):
    """Financial governance decision request"""

    request_id: UUID = Field(default_factory=uuid4, description="Unique request ID")
    decision_type: DecisionType = Field(..., description="Decision type")
    context: DecisionContext = Field(..., description="Decision context")
    evidence: list[Evidence] = Field(..., min_length=1, description="Supporting evidence")
    constraints: Constraints = Field(..., description="Constraints")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "decision_type": "trade_approval",
                "context": {
                    "timestamp": "2025-11-17T14:30:00Z",
                    "entity": "Equity Trading Desk Alpha",
                    "purpose": "Large block trade approval for AAPL 10K shares",
                    "urgency": "high",
                },
                "evidence": [
                    {
                        "type": "market_data",
                        "source": "Bloomberg",
                        "data": {"symbol": "AAPL", "price": 175.50, "volume": 85000000},
                        "confidence": 95.0,
                    },
                ],
                "constraints": {
                    "regulatory": ["SEC Rule 15c3-1"],
                    "risk_limits": {"position_limit": 50000},
                },
            },
        }


class DecisionRuling(BaseModel):
    """Financial governance ruling (Supreme Court format)"""

    ruling_id: UUID = Field(default_factory=lambda: uuid.uuid7(), description="UUID v7 ruling ID")
    request_id: UUID = Field(..., description="Originating request ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Ruling timestamp")
    decision: DecisionOutcome = Field(..., description="Final decision")
    rationale: Rationale = Field(..., description="Ruling rationale")
    risk_assessment: RiskAssessment = Field(..., description="ATP 5-19 risk assessment")
    confidence: float = Field(..., ge=0, le=100, description="Confidence (0-100)")
    conditions: list[Condition] = Field(default_factory=list, description="Approval conditions")
    next_steps: list[str] = Field(default_factory=list, description="Recommended actions")
    audit_trail: AuditTrail = Field(..., description="Audit trail")
    compliance_flags: list[ComplianceFlag] = Field(
        default_factory=list,
        description="Compliance flags",
    )
    financial_impact: FinancialImpact | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "ruling_id": "018c3f5e-1234-7890-abcd-ef1234567890",
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-11-17T14:35:00Z",
                "decision": "APPROVE_WITH_CONDITIONS",
                "rationale": {
                    "summary": "Approval granted with position size limit...",
                    "key_factors": ["Market liquidity sufficient", "Within risk limits"],
                    "precedents": [],
                },
                "risk_assessment": {
                    "probability": "C",
                    "severity": "III",
                    "level": "M",
                    "mitigation": ["Reduce position size by 20%"],
                },
                "confidence": 87.5,
                "audit_trail": {
                    "evidence_reviewed": 3,
                    "rules_applied": ["RiskLimit-001", "RegCompliance-SEC"],
                    "computation_time_ms": 142.5,
                },
            },
        }
