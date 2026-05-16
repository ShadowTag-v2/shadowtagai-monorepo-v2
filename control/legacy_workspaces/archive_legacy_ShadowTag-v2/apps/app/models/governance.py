# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Governance models and schemas
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk level classification"""

    UNACCEPTABLE = "unacceptable"
    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"


class ComplianceFramework(str, Enum):
    """Compliance frameworks"""

    EU_AI_ACT = "eu_ai_act"
    DSA_VLOP = "dsa_vlop"
    NIST_RMF = "nist_rmf"
    ISO_42001 = "iso_42001"
    GDPR = "gdpr"
    COPPA = "coppa"


class GovernanceAssessmentRequest(BaseModel):
    """Request for governance assessment"""

    content_type: str = Field(..., description="Type of content being assessed")
    content_id: str | None = Field(None, description="Unique content identifier")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    user_age: int | None = Field(None, description="User age for COPPA compliance")
    is_ai_generated: bool = Field(default=False, description="Whether content is AI-generated")
    frameworks: list[ComplianceFramework] = Field(
        default=[ComplianceFramework.EU_AI_ACT, ComplianceFramework.NIST_RMF],
        description="Frameworks to assess against",
    )


class ControlAssessment(BaseModel):
    """Individual control assessment"""

    control_id: str
    control_name: str
    status: str  # "compliant", "non-compliant", "partial", "not_applicable"
    evidence: str | None = None
    remediation: str | None = None


class GovernanceAssessmentResponse(BaseModel):
    """Response from governance assessment"""

    assessment_id: str
    timestamp: datetime
    risk_level: RiskLevel
    compliance_score: float = Field(..., ge=0.0, le=1.0)
    frameworks_assessed: list[ComplianceFramework]
    controls: list[ControlAssessment]
    recommendations: list[str]
    requires_human_review: bool
    transparency_notice: str | None = None
    residual_risks: list[str] = Field(default_factory=list)


class EUAIActAssessment(BaseModel):
    """EU AI Act specific assessment"""

    risk_classification: RiskLevel
    transparency_requirements: list[str]
    human_oversight_required: bool
    data_governance_compliant: bool
    technical_documentation_complete: bool
    conformity_assessment_required: bool


class NISTRMFAssessment(BaseModel):
    """NIST AI RMF assessment"""

    govern_score: float = Field(..., ge=0.0, le=1.0)
    map_score: float = Field(..., ge=0.0, le=1.0)
    measure_score: float = Field(..., ge=0.0, le=1.0)
    manage_score: float = Field(..., ge=0.0, le=1.0)
    overall_maturity: str  # "initial", "developing", "defined", "managed", "optimizing"
    gaps: list[str]


class ISO42001Assessment(BaseModel):
    """ISO/IEC 42001 AIMS assessment"""

    context_of_organization: float = Field(..., ge=0.0, le=1.0)
    leadership: float = Field(..., ge=0.0, le=1.0)
    planning: float = Field(..., ge=0.0, le=1.0)
    support: float = Field(..., ge=0.0, le=1.0)
    operation: float = Field(..., ge=0.0, le=1.0)
    performance_evaluation: float = Field(..., ge=0.0, le=1.0)
    improvement: float = Field(..., ge=0.0, le=1.0)
    certification_ready: bool
