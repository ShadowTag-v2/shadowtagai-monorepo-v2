# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
California AI Regulations Compliance Models
============================================
Pydantic models for the NS-JR-Cor (Neural System / Judgment Rule / Core)
compliance framework implementing California's AI chatbot regulations.

Key Regulations Covered:
- SB 1047: AI Safety and Security Act
- AB 2930: Automated Decision Tools
- AB 3030: AI Healthcare Restrictions
- AI Chatbot Minor Protection Laws

Reference: Governor Newsom's AI chatbot safety legislation (2024-2025)
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# =============================================================================
# Enumerations
# =============================================================================


class CARegulationType(str, Enum):
    """California AI regulation types requiring compliance"""

    SELF_HARM_DETECTION = "self_harm_detection"  # Detect/respond to self-harm statements
    AI_DISCLOSURE = "ai_disclosure"  # Disclose artificial nature
    BREAK_REMINDER = "break_reminder"  # Break reminders for minors
    EXPLICIT_CONTENT = "explicit_content"  # Block explicit imagery to minors
    MEDICAL_IMPERSONATION = "medical_impersonation"  # No impersonating medical professionals
    MINOR_PROTECTION = "minor_protection"  # General minor protections
    REAL_WORLD_HARM = "real_world_harm"  # Liability for real-world harm
    DATA_PRIVACY = "data_privacy"  # CPRA data privacy
    ALGORITHMIC_TRANSPARENCY = "algorithmic_transparency"


class UserAgeCategory(str, Enum):
    """User age categories for tiered protection levels"""

    UNDER_13 = "under_13"  # Maximum protection (COPPA + CA)
    TEEN_13_17 = "teen_13_17"  # Minor protection
    ADULT = "adult"  # Standard protections
    UNKNOWN = "unknown"  # Default to maximum protection


class ComplianceAction(str, Enum):
    """Actions the compliance engine can mandate"""

    PASS = "pass"  # Content is compliant, allow through
    BLOCK = "block"  # Block content entirely
    WARN = "warn"  # Allow with warning
    DISCLOSE = "disclose"  # Require AI disclosure
    REMIND = "remind"  # Send break reminder
    RESPOND_WITH_RESOURCES = "respond_with_resources"  # Self-harm response
    REQUIRE_PARENTAL_CONSENT = "require_parental_consent"
    FLAG_FOR_REVIEW = "flag_for_review"  # Human review required


class ViolationSeverity(str, Enum):
    """Severity levels for compliance violations"""

    INFO = "info"  # Informational, no action needed
    LOW = "low"  # Minor issue, warning only
    MEDIUM = "medium"  # Significant issue, may require action
    HIGH = "high"  # Serious violation, action required
    CRITICAL = "critical"  # Immediate blocking required


class RiskTier(int, Enum):
    """Risk tier classification (1-5)"""

    TIER_1_MINIMAL = 1
    TIER_2_LOW = 2
    TIER_3_MODERATE = 3
    TIER_4_HIGH = 4
    TIER_5_CRITICAL = 5


class ContentType(str, Enum):
    """Types of content being assessed"""

    TEXT_MESSAGE = "text_message"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MIXED_MEDIA = "mixed_media"


# =============================================================================
# Detection Signals (NS Layer Output)
# =============================================================================


class DetectionSignal(BaseModel):
    """Single detection signal from NS layer"""

    signal_type: str = Field(..., description="Type of signal detected")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    evidence: str = Field(default="", description="Supporting evidence/excerpt")
    detector: str = Field(..., description="Which detector identified this signal")
    metadata: dict[str, Any] = Field(default_factory=dict)


class SelfHarmSignal(DetectionSignal):
    """Self-harm detection signal"""

    signal_type: str = "self_harm"
    severity_level: ViolationSeverity = ViolationSeverity.CRITICAL
    crisis_indicators: list[str] = Field(default_factory=list)
    recommended_resources: list[str] = Field(default_factory=lambda: ["988 Suicide & Crisis Lifeline", "Crisis Text Line"])


class ExplicitContentSignal(DetectionSignal):
    """Explicit content detection signal"""

    signal_type: str = "explicit_content"
    content_categories: list[str] = Field(default_factory=list)
    image_hash: str | None = None


class MedicalClaimSignal(DetectionSignal):
    """Medical claim/impersonation detection signal"""

    signal_type: str = "medical_claim"
    claim_type: str = Field(default="", description="Type of medical claim")
    impersonation_detected: bool = False


class NSDetectionOutput(BaseModel):
    """Complete output from NS (Neural System) detection layer"""

    content_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    signals: list[DetectionSignal] = Field(default_factory=list)
    self_harm_signals: list[SelfHarmSignal] = Field(default_factory=list)
    explicit_content_signals: list[ExplicitContentSignal] = Field(default_factory=list)
    medical_claim_signals: list[MedicalClaimSignal] = Field(default_factory=list)
    overall_risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    processing_time_ms: float = Field(default=0.0)
    cache_hit: bool = Field(default=False)

    @property
    def has_critical_signals(self) -> bool:
        """Check if any critical signals detected"""
        return len(self.self_harm_signals) > 0 or any(s.confidence > 0.8 for s in self.explicit_content_signals)


# =============================================================================
# Policy Evaluation (JR Layer Output)
# =============================================================================


class PolicyViolation(BaseModel):
    """Single policy violation identified by JR layer"""

    violation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    regulation_type: CARegulationType
    rule_id: str = Field(..., description="Specific rule ID (e.g., CA_SELF_HARM_001)")
    description: str
    severity: ViolationSeverity
    evidence: str = Field(default="")
    remediation: str = Field(default="")
    reference: str = Field(default="", description="Legal reference")


class PolicyEvaluation(BaseModel):
    """Single policy evaluation result"""

    policy_id: str
    policy_name: str
    passed: bool
    violations: list[PolicyViolation] = Field(default_factory=list)
    required_action: ComplianceAction = ComplianceAction.PASS
    notes: str = Field(default="")


class JRPolicyOutput(BaseModel):
    """Complete output from JR (Judgment Rule) policy engine"""

    content_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_age_category: UserAgeCategory
    evaluations: list[PolicyEvaluation] = Field(default_factory=list)
    all_violations: list[PolicyViolation] = Field(default_factory=list)
    go_decision: bool = Field(..., description="Binary go/no-go decision")
    risk_tier: RiskTier = Field(default=RiskTier.TIER_1_MINIMAL)
    required_actions: list[ComplianceAction] = Field(default_factory=list)
    human_review_required: bool = Field(default=False)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reasoning: str = Field(default="")
    processing_time_ms: float = Field(default=0.0)

    @property
    def is_compliant(self) -> bool:
        """Check if content is compliant"""
        return self.go_decision and len(self.all_violations) == 0


# =============================================================================
# Core Orchestration (Cor Layer Output)
# =============================================================================


class ComplianceAttestation(BaseModel):
    """Compliance attestation certificate"""

    attestation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    valid_until: datetime
    content_hash: str
    compliance_status: str = Field(default="compliant")
    frameworks_assessed: list[str] = Field(default_factory=lambda: ["CA_AI_CHATBOT_REGULATIONS"])
    signature: str | None = None  # ShadowTag cryptographic signature


class AuditTrailEntry(BaseModel):
    """Single audit trail entry"""

    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    stage: str = Field(..., description="NS, JR, or Cor")
    action: str
    input_hash: str
    output_hash: str
    latency_ms: float
    metadata: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# API Request/Response Models
# =============================================================================


class CaliforniaAIAssessmentRequest(BaseModel):
    """Request for California AI compliance assessment"""

    content: str = Field(..., min_length=1, max_length=50000, description="Content to assess")
    content_type: ContentType = Field(default=ContentType.TEXT_MESSAGE)
    content_id: str | None = Field(None, description="External content identifier")

    # User context
    user_id: str | None = Field(None, description="User identifier")
    user_age: int | None = Field(None, ge=0, le=150, description="User age if known")
    user_age_category: UserAgeCategory | None = Field(None)

    # Platform context
    platform_id: str = Field(default="default", description="Platform identifier")
    session_id: str | None = Field(None, description="Session identifier for tracking")
    session_duration_minutes: int | None = Field(None, ge=0, description="Session duration")

    # Assessment options
    include_attestation: bool = Field(default=False, description="Include compliance certificate")
    strict_mode: bool = Field(default=True, description="Strict enforcement mode")
    frameworks: list[str] = Field(
        default_factory=lambda: ["CA_AI_CHATBOT"],
        description="Compliance frameworks to assess",
    )

    # Media attachments
    media_urls: list[str] = Field(default_factory=list, description="URLs of media to assess")
    media_base64: list[str] = Field(default_factory=list, description="Base64 encoded media")

    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)

    def get_age_category(self) -> UserAgeCategory:
        """Determine user age category"""
        if self.user_age_category:
            return self.user_age_category
        if self.user_age is None:
            return UserAgeCategory.UNKNOWN
        if self.user_age < 13:
            return UserAgeCategory.UNDER_13
        elif self.user_age < 18:
            return UserAgeCategory.TEEN_13_17
        else:
            return UserAgeCategory.ADULT


class CaliforniaAIAssessmentResult(BaseModel):
    """Complete California AI compliance assessment result"""

    # Identifiers
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    request_id: str | None = None

    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Compliance decision
    is_compliant: bool = Field(..., description="Overall compliance status")
    go_decision: bool = Field(..., description="Binary go/no-go for content")
    compliance_score: float = Field(..., ge=0.0, le=1.0, description="0-1 compliance score")
    risk_tier: RiskTier

    # Violations
    violations: list[PolicyViolation] = Field(default_factory=list)
    violation_count: int = Field(default=0)

    # Required actions
    required_actions: list[ComplianceAction] = Field(default_factory=list)
    action_details: dict[str, Any] = Field(default_factory=dict)

    # Self-harm specific (if applicable)
    self_harm_detected: bool = Field(default=False)
    crisis_resources: list[str] = Field(default_factory=list)

    # Disclosure requirements
    disclosure_required: bool = Field(default=True)
    disclosure_text: str = Field(default="This content is generated by an AI system.")

    # Break reminder (for minors)
    break_reminder_due: bool = Field(default=False)
    break_reminder_text: str | None = None

    # Layer outputs (for debugging/audit)
    ns_output: NSDetectionOutput | None = None
    jr_output: JRPolicyOutput | None = None

    # Attestation
    attestation: ComplianceAttestation | None = None

    # Audit trail
    audit_trail: list[AuditTrailEntry] = Field(default_factory=list)

    # Performance metrics
    total_latency_ms: float = Field(default=0.0)
    cache_hit: bool = Field(default=False)

    # Human review
    requires_human_review: bool = Field(default=False)
    human_review_reason: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "assessment_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "content_id": "msg-12345",
                "is_compliant": True,
                "go_decision": True,
                "compliance_score": 0.95,
                "risk_tier": 1,
                "violations": [],
                "required_actions": ["disclose"],
                "disclosure_required": True,
                "disclosure_text": "This content is generated by an AI system.",
                "total_latency_ms": 45.2,
                "cache_hit": True,
            }
        }


class BatchAssessmentRequest(BaseModel):
    """Batch assessment request for multiple content items"""

    items: list[CaliforniaAIAssessmentRequest] = Field(..., min_length=1, max_length=100, description="Content items to assess")
    parallel: bool = Field(default=True, description="Process items in parallel")
    fail_fast: bool = Field(default=False, description="Stop on first failure")


class BatchAssessmentResult(BaseModel):
    """Batch assessment result"""

    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_items: int
    compliant_items: int
    non_compliant_items: int
    error_items: int = Field(default=0)
    results: list[CaliforniaAIAssessmentResult]
    overall_compliance_rate: float = Field(..., ge=0.0, le=1.0)
    total_latency_ms: float


class ComplianceReportRequest(BaseModel):
    """Request for compliance report"""

    start_date: datetime
    end_date: datetime
    platform_id: str | None = None
    include_violations: bool = Field(default=True)
    include_audit_trail: bool = Field(default=False)
    format: str = Field(default="json", description="json, csv, or pdf")


class ComplianceReport(BaseModel):
    """Compliance report"""

    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    period_start: datetime
    period_end: datetime

    # Summary statistics
    total_assessments: int
    compliant_count: int
    non_compliant_count: int
    compliance_rate: float

    # Breakdown by regulation
    violations_by_regulation: dict[str, int] = Field(default_factory=dict)

    # Breakdown by severity
    violations_by_severity: dict[str, int] = Field(default_factory=dict)

    # User demographics
    assessments_by_age_category: dict[str, int] = Field(default_factory=dict)

    # Top violations
    top_violations: list[dict[str, Any]] = Field(default_factory=list)

    # Recommendations
    recommendations: list[str] = Field(default_factory=list)


# =============================================================================
# Usage/Billing Models
# =============================================================================


class UsageMetrics(BaseModel):
    """Usage metrics for billing"""

    period_start: datetime
    period_end: datetime
    platform_id: str

    # Volume metrics
    total_assessments: int
    cached_assessments: int
    api_calls_google: int
    api_calls_hive: int
    api_calls_gemini: int

    # Cost metrics
    estimated_cost_usd: float
    cost_per_assessment: float


class UsageTier(str, Enum):
    """Usage/billing tiers"""

    FREE = "free"  # 1K assessments/month
    STARTER = "starter"  # 10K assessments/month
    GROWTH = "growth"  # 100K assessments/month
    ENTERPRISE = "enterprise"  # Unlimited
