# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Judge #6 HITL System - Core Models
Binary enforcement decision models with ATP 5-19 risk integration
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, ConfigDict

from src.risk_matrix import RiskLevel, RiskAssessment


class JudgeDecision(str, Enum):
    """Binary judge decision"""

    ALLOW = "ALLOW"
    BLOCK = "BLOCK"


class ApprovalGate(str, Enum):
    """Human-in-the-loop approval gate"""

    AUTO = "auto"  # Automated approval (low risk)
    CFO = "cfo"  # CFO approval required
    FINANCE_DIR = "finance_director"  # Finance Director approval
    DEPT_HEAD = "department_head"  # Department Head approval
    SENIOR_EXEC = "senior_executive"  # Senior Executive approval
    C_SUITE = "c_suite"  # C-Suite approval
    BOARD = "board"  # Board of Directors approval
    ESCALATE = "escalate"  # Escalate to higher authority


class JudgeType(str, Enum):
    """Judge vertical types"""

    FIN = "FinJudge"  # Financial transactions
    CASE = "CaseJudge"  # Legal case assessment
    LAW = "LawJudge"  # Legal compliance
    FRAUD = "FraudJudge"  # Fraud detection


class JudgeRequest(BaseModel):
    """Judge evaluation request"""

    request_id: str = Field(..., description="Unique request identifier")
    judge_type: JudgeType = Field(..., description="Judge vertical to use")
    action_type: str = Field(..., description="Action being evaluated")
    context: dict[str, Any] = Field(..., description="Action context and parameters")
    urgency: str = Field(default="normal", description="Request urgency: low, normal, high, critical")
    requested_by: str = Field(..., description="User/system requesting the action")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Request timestamp")


class JudgeResponse(BaseModel):
    """Judge evaluation response"""

    request_id: str = Field(..., description="Original request ID")
    decision: JudgeDecision = Field(..., description="Binary ALLOW/BLOCK decision")
    risk_assessment: RiskAssessment = Field(..., description="ATP 5-19 risk assessment")
    approval_gate: ApprovalGate = Field(..., description="Required approval gate")
    reasoning: str = Field(..., description="Decision reasoning (human-readable)")
    semantic_trail: str = Field(..., description="Compressed audit trail")
    latency_ms: float = Field(..., description="Processing latency (milliseconds)")
    judge_type: JudgeType = Field(..., description="Judge vertical used")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    next_steps: list[str] = Field(default_factory=list, description="Required next steps")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Response timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "request_id": "req_20251117_fin_001",
                "decision": "BLOCK",
                "risk_assessment": {
                    "probability": "B",
                    "severity": "II",
                    "risk_level": "high",
                    "rationale": "Wire transfer >$50K to new vendor without purchase order",
                    "mitigations": ["Verify vendor with external database", "Require dual approval"],
                    "residual_risk": "medium",
                    "requires_approval": True,
                    "approval_authority": "CFO",
                },
                "approval_gate": "cfo",
                "reasoning": "High-value wire transfer to unverified vendor requires CFO approval per SOP-C",
                "semantic_trail": "50K_wire→new_vendor→no_PO→high_risk→CFO_gate",
                "latency_ms": 42.3,
                "judge_type": "FinJudge",
                "metadata": {"vendor_id": "VND-12345", "amount_usd": 50000, "destination_country": "Unknown"},
                "next_steps": ["Route to CFO approval queue", "Verify vendor via D&B lookup", "Request supporting documentation from requester"],
                "timestamp": "2025-11-17T14:30:00Z",
            }
        }
    )


class AuditTrail(BaseModel):
    """Immutable semantic-compressed audit trail"""

    trail_id: str = Field(..., description="Unique trail identifier")
    request_id: str = Field(..., description="Related request ID")
    judge_type: JudgeType = Field(..., description="Judge vertical")
    decision: JudgeDecision = Field(..., description="Final decision")
    risk_level: RiskLevel = Field(..., description="Risk level")
    semantic_summary: str = Field(..., description="Compressed semantic summary")
    full_context: dict[str, Any] = Field(..., description="Complete context (encrypted)")
    approval_chain: list[dict[str, Any]] = Field(default_factory=list, description="Approval history")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Trail creation time")
    retention_days: int = Field(default=2555, description="Retention period (7 years default)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "trail_id": "trail_20251117_fin_001",
                "request_id": "req_20251117_fin_001",
                "judge_type": "FinJudge",
                "decision": "ALLOW",
                "risk_level": "medium",
                "semantic_summary": "50K_wire→verified_vendor→PO_123456→CFO_approved→executed",
                "full_context": {"encrypted": True, "key_id": "key_20251117"},
                "approval_chain": [
                    {
                        "approver": "john.doe@company.com",
                        "role": "CFO",
                        "decision": "APPROVE",
                        "timestamp": "2025-11-17T14:45:00Z",
                        "notes": "Vendor verified, PO in place, approved",
                    }
                ],
                "timestamp": "2025-11-17T14:30:00Z",
                "retention_days": 2555,
            }
        }
    )


class PerformanceMetrics(BaseModel):
    """Judge performance metrics"""

    judge_type: JudgeType = Field(..., description="Judge vertical")
    period_start: datetime = Field(..., description="Metrics period start")
    period_end: datetime = Field(..., description="Metrics period end")
    total_requests: int = Field(..., description="Total requests evaluated")
    decisions_allow: int = Field(..., description="ALLOW decisions")
    decisions_block: int = Field(..., description="BLOCK decisions")
    avg_latency_ms: float = Field(..., description="Average latency (milliseconds)")
    p50_latency_ms: float = Field(..., description="p50 latency")
    p99_latency_ms: float = Field(..., description="p99 latency")
    risk_distribution: dict[str, int] = Field(..., description="Risk level distribution")
    approval_rate: float = Field(..., description="Human approval rate (0-1)")
    false_positive_rate: float | None = Field(None, description="False positive rate (if known)")


__all__ = [
    "JudgeDecision",
    "ApprovalGate",
    "JudgeType",
    "JudgeRequest",
    "JudgeResponse",
    "AuditTrail",
    "PerformanceMetrics",
]
