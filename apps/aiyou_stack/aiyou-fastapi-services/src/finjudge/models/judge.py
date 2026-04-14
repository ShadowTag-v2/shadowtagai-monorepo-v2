"""FinJudge Pure Judge Models (v0.2)
Simplified input/output for pure risk classification
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

# ============================================================================
# Enums
# ============================================================================


class ActorRole(StrEnum):
    """Actor roles"""

    TRADER = "trader"
    PM = "portfolio_manager"
    CREDIT_OFFICER = "credit_officer"
    RETAIL_USER = "retail_user"
    CFO = "cfo"
    RISK_MANAGER = "risk_manager"
    COMPLIANCE = "compliance"


class TimeHorizon(StrEnum):
    """Decision time horizons"""

    INTRA_DAY = "intra_day"
    SWING = "swing"
    LONG_TERM = "long_term"


class Objective(StrEnum):
    """Decision objectives"""

    ALPHA = "alpha"
    HEDGE = "hedge"
    INCOME = "income"
    SPECULATION = "speculation"
    RISK_REDUCTION = "risk_reduction"


class Probability(StrEnum):
    """ATP 5-19 Probability Levels"""

    A = "A"  # Frequent: ≥80%
    B = "B"  # Likely: 50-79%
    C = "C"  # Occasional: 20-49%
    D = "D"  # Seldom: 5-19%
    E = "E"  # Unlikely: <5%


class Severity(StrEnum):
    """ATP 5-19 Severity Levels"""

    I = "I"  # Catastrophic: >$10M loss
    II = "II"  # Critical: $1M-$10M loss
    III = "III"  # Moderate: $100K-$1M loss
    IV = "IV"  # Negligible: <$100K loss


class RiskLevel(StrEnum):
    """Risk levels"""

    EXTREME = "EXTREME"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"


class Disposition(StrEnum):
    """Decision dispositions"""

    APPROVE = "APPROVE"
    MODIFY = "MODIFY"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"


# ============================================================================
# Sub-Models
# ============================================================================


class Actor(BaseModel):
    """Decision actor"""

    role: ActorRole = Field(..., description="Actor role")
    org_unit: str = Field(..., description="Organizational unit (desk, team, etc.)")
    jurisdiction: str = Field(default="US", description="Jurisdiction (US, EU, UK, etc.)")


class DecisionContext(BaseModel):
    """Decision context"""

    time_horizon: TimeHorizon = Field(..., description="Decision time horizon")
    objective: Objective = Field(..., description="Decision objective")
    constraints: list[str] = Field(
        default_factory=list, description="Constraints (e.g., 'no leverage', 'max 2% capital risk')",
    )


class PnLDistribution(BaseModel):
    """P&L distribution summary"""

    mean: float = Field(..., description="Mean P&L")
    stddev: float = Field(..., description="Standard deviation")
    skew: float = Field(..., description="Skewness")
    kurtosis: float = Field(..., description="Kurtosis (fat tails)")


class TailRisk(BaseModel):
    """Tail risk metrics"""

    var_95: float | None = Field(None, description="95% Value at Risk (USD)")
    cvar_95: float | None = Field(None, description="95% Conditional VaR (USD)")
    var_99: float | None = Field(None, description="99% Value at Risk (USD)")
    cvar_99: float | None = Field(None, description="99% Conditional VaR (USD)")


class Exposure(BaseModel):
    """Exposure metrics"""

    notional: float = Field(..., description="Notional exposure (USD)")
    pct_aum: float = Field(..., description="% of AUM")
    leverage_ratio: float = Field(default=1.0, description="Leverage ratio")


class Volatility(BaseModel):
    """Volatility metrics"""

    realized_vol: float | None = Field(None, description="Realized volatility")
    implied_vol: float | None = Field(None, description="Implied volatility")
    regime_tag: str | None = Field(
        None, description="Volatility regime (low_vol, normal, high_vol, stressed)",
    )


class CreditMetrics(BaseModel):
    """Credit risk metrics"""

    pd: float | None = Field(None, description="Probability of default")
    lgd: float | None = Field(None, description="Loss given default")
    ead: float | None = Field(None, description="Exposure at default")


class LiquidityMetrics(BaseModel):
    """Liquidity metrics"""

    spread_bps: float | None = Field(None, description="Bid-ask spread (bps)")
    depth_score: float | None = Field(None, ge=0, le=100, description="Market depth score (0-100)")
    days_to_liquidate: float | None = Field(None, description="Days to liquidate position")


class Metrics(BaseModel):
    """All metrics from upstream systems"""

    pnl_distribution_summary: PnLDistribution | None = None
    tail_risk: TailRisk | None = None
    exposure: Exposure | None = None
    volatility: Volatility | None = None
    credit_metrics: CreditMetrics | None = None
    liquidity_metrics: LiquidityMetrics | None = None
    custom: dict[str, Any] = Field(default_factory=dict, description="Custom metrics from upstream")


class Flags(BaseModel):
    """Flags from upstream systems"""

    regulatory_flags: list[str] = Field(
        default_factory=list,
        description="Regulatory flags (e.g., 'concentration_breach', 'UCITS_limit')",
    )
    policy_flags: list[str] = Field(
        default_factory=list, description="Policy flags (e.g., 'outside_risk_budget')",
    )


class RiskMatrix(BaseModel):
    """ATP 5-19 risk classification"""

    probability_class: Probability = Field(..., description="Probability level (A-E)")
    severity_class: Severity = Field(..., description="Severity level (I-IV)")
    risk_level: RiskLevel = Field(..., description="Overall risk level")
    rationale_summary: str = Field(..., min_length=20, description="1-3 sentence rationale")


class NumericOverview(BaseModel):
    """Numeric overview of key metrics"""

    key_metrics: dict[str, Any] = Field(..., description="Redacted subset of input metrics")
    primary_risk_driver: str = Field(
        ..., description="Primary risk driver (tail_risk, credit, liquidity, etc.)",
    )


class TimeBoundary(BaseModel):
    """Time-based review boundaries"""

    re_review_if: str | None = Field(None, description="Condition triggering re-review")
    reassess_in_days: int | None = Field(None, description="Automatic reassessment period")


class Recommendation(BaseModel):
    """Judge recommendation"""

    disposition: Disposition = Field(..., description="Decision disposition")
    required_controls: list[str] = Field(default_factory=list, description="Required risk controls")
    time_boundaries: TimeBoundary | None = None


class PrecedentLink(BaseModel):
    """Link to similar past decision"""

    id: str = Field(..., description="Decision ID")
    outcome: str = Field(..., description="Outcome of past decision")
    note: str = Field(..., description="Brief note on similarity")


class ExplanationNL(BaseModel):
    """Natural language explanation"""

    short_summary: str = Field(..., max_length=500, description="≤3 sentences")
    detail_bullets: list[str] = Field(
        ..., min_items=1, description="Detail bullets (what/why/where)",
    )


class AuditTrail(BaseModel):
    """Audit trail"""

    input_hash: str = Field(..., description="SHA-256 of input JSON")
    feature_vector_hash: str | None = Field(None, description="Feature vector hash (for ML audit)")
    overrides: list[dict[str, str]] = Field(default_factory=list, description="Manual overrides")


# ============================================================================
# Main Models
# ============================================================================


class JudgeRequest(BaseModel):
    """Judge decision request (pure judge v0.2)"""

    decision_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Decision identifier",
    )
    module: str = Field(..., description="Calling module (e.g., 'financial_runway_monitor')")
    actor: Actor = Field(..., description="Decision actor")
    intent_nl: str = Field(..., min_length=10, description="Natural language intent")
    context: DecisionContext = Field(..., description="Decision context")
    metrics: Metrics = Field(..., description="Metrics from upstream systems")
    flags: Flags = Field(default_factory=Flags, description="Flags from upstream")
    prior_precedent_ids: list[str] = Field(
        default_factory=list, description="Similar past decisions",
    )
    user_notes: str | None = Field(None, description="Additional user notes")

    class Config:
        json_schema_extra = {
            "example": {
                "module": "financial_runway_monitor",
                "actor": {"role": "cfo", "org_unit": "Finance", "jurisdiction": "US"},
                "intent_nl": "Approve hiring 3 engineers, increasing monthly burn from $180k to $240k",
                "context": {
                    "time_horizon": "long_term",
                    "objective": "alpha",
                    "constraints": ["max_12mo_runway"],
                },
                "metrics": {
                    "exposure": {"notional": 720000, "pct_aum": 33.3, "leverage_ratio": 1.0},
                    "custom": {
                        "current_burn": 180000,
                        "proposed_burn": 240000,
                        "runway_months_current": 18,
                        "runway_months_proposed": 13.5,
                    },
                },
                "flags": {"policy_flags": ["approaching_12mo_runway_threshold"]},
            },
        }


class JudgeRuling(BaseModel):
    """Judge ruling (pure judge v0.2)"""

    decision_id: str = Field(..., description="Decision identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Ruling timestamp")
    judge_version: str = Field(default="v0.2.0", description="Judge version")
    risk_matrix: RiskMatrix = Field(..., description="ATP 5-19 risk classification")
    numeric_overview: NumericOverview = Field(..., description="Key metrics overview")
    recommendation: Recommendation = Field(..., description="Judge recommendation")
    precedent_links: list[PrecedentLink] = Field(
        default_factory=list, description="Similar decisions",
    )
    explanation_nl: ExplanationNL = Field(..., description="Natural language explanation")
    audit_trail: AuditTrail = Field(..., description="Audit trail")

    class Config:
        json_schema_extra = {
            "example": {
                "decision_id": "burn_rate_increase_2025_11",
                "timestamp": "2025-11-17T14:35:00Z",
                "judge_version": "v0.2.0",
                "risk_matrix": {
                    "probability_class": "B",
                    "severity_class": "II",
                    "risk_level": "HIGH",
                    "rationale_summary": "33% burn increase reduces runway below safe threshold (13.5mo → approaching 12mo red zone)",
                },
                "numeric_overview": {
                    "key_metrics": {
                        "burn_increase_pct": 33.3,
                        "runway_months": 13.5,
                        "capital_at_risk": 720000,
                    },
                    "primary_risk_driver": "runway_compression",
                },
                "recommendation": {
                    "disposition": "MODIFY",
                    "required_controls": [
                        "Defer 1 hire to next quarter (reduce to +2 engineers)",
                        "Set milestone: If ARR growth <20% QoQ in Q1, freeze hiring",
                    ],
                    "time_boundaries": {
                        "re_review_if": "runway < 12 months",
                        "reassess_in_days": 30,
                    },
                },
                "explanation_nl": {
                    "short_summary": "This decision is HIGH risk (B-II). The 33% burn increase compresses runway to 13.5 months, approaching the critical 12-month threshold that signals fundraising urgency.",
                    "detail_bullets": [
                        "WHAT: Hiring 3 engineers increases monthly burn by $60k (33% increase)",
                        "WHY RISKY: Runway drops from 18mo to 13.5mo, approaching 12mo red zone",
                        "WHERE UNCERTAIN: ARR growth rate unclear; if <20% QoQ, burn increase unjustified",
                    ],
                },
                "audit_trail": {"input_hash": "sha256_placeholder", "overrides": []},
            },
        }
