"""
ActiveShield Modular Compliance Framework (MCF v1.0) - Data Models

Core Principle: "Users select which laws apply to them. ActiveShield assembles
the exact compliance modules needed — nothing more, nothing less."

Compliance-as-Documentation™ - evidence that defends you.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

# ============================================================================
# JURISDICTION & REGULATION ENUMS
# ============================================================================


class Jurisdiction(StrEnum):
    """Geographic jurisdictions for compliance selection"""

    US = "us"
    EU = "eu"
    UK = "uk"
    APAC = "apac"
    GLOBAL = "global"


class RegulationId(StrEnum):
    """Supported regulation module identifiers"""

    # EU Regulations
    EU_AI_ACT = "eu_ai_act"
    GDPR = "gdpr"
    DSA = "dsa"

    # US Regulations
    CA_SB_243 = "ca_sb_243"
    HIPAA = "hipaa"
    COPPA = "coppa"

    # Standards
    NIST_RMF = "nist_rmf"
    ISO_42001 = "iso_42001"


class RiskTier(StrEnum):
    """EU AI Act risk classification tiers"""

    UNACCEPTABLE = "unacceptable"  # Banned
    HIGH = "high"  # Strict requirements
    LIMITED = "limited"  # Transparency obligations
    MINIMAL = "minimal"  # No specific requirements


class ComplianceStatus(StrEnum):
    """Status of compliance for a single control or module"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    NOT_APPLICABLE = "not_applicable"
    PENDING_REVIEW = "pending_review"


class PricingTier(StrEnum):
    """Subscription pricing tiers"""

    FREE = "free"  # 1 regulation, limited API calls
    PRO = "pro"  # Base + add-on regulations
    ENTERPRISE = "enterprise"  # Unlimited + dedicated advisor


# ============================================================================
# MODULE METADATA MODELS
# ============================================================================


class ModuleMetadata(BaseModel):
    """Metadata describing a compliance regulation module"""

    id: RegulationId
    name: str
    short_name: str
    version: str = "1.0.0"
    jurisdiction: Jurisdiction
    description: str
    effective_date: datetime | None = None
    articles: list[str] = Field(default_factory=list)
    official_url: str | None = None
    pricing_addon_usd: float = 50.0  # Monthly add-on price


class ValidationRule(BaseModel):
    """A single validation rule within a compliance module"""

    rule_id: str
    name: str
    description: str
    category: str
    severity: str = "medium"  # low, medium, high, critical
    auto_check: bool = True  # Can be automatically validated
    requires_evidence: bool = False
    remediation_guidance: str = ""


class ControlDefinition(BaseModel):
    """Definition of a compliance control/requirement"""

    control_id: str
    name: str
    description: str
    article_ref: str | None = None
    validation_rules: list[ValidationRule] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)


# ============================================================================
# ASSESSMENT REQUEST/RESPONSE MODELS
# ============================================================================


class ComplianceBlueprintRequest(BaseModel):
    """Request to generate a compliance blueprint based on user selections"""

    jurisdictions: list[Jurisdiction] = Field(
        default=[Jurisdiction.US], description="Selected geographic jurisdictions"
    )
    regulations: list[RegulationId] = Field(
        ..., description="Selected regulation modules to enforce"
    )
    organization_type: str | None = Field(
        None, description="Type of organization (startup, enterprise, government)"
    )
    ai_system_type: str | None = Field(None, description="Type of AI system being assessed")
    handles_minors: bool = Field(
        default=False, description="Whether the system handles data from minors"
    )
    handles_health_data: bool = Field(
        default=False, description="Whether the system handles health/PHI data"
    )


class ComplianceBlueprintResponse(BaseModel):
    """Generated compliance blueprint from selected modules"""

    blueprint_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    selected_modules: list[ModuleMetadata]
    total_controls: int
    estimated_monthly_cost_usd: float
    api_endpoints: dict[str, str]  # endpoint -> description
    sdk_config: dict[str, Any]
    checklist_url: str | None = None


class AssessmentInput(BaseModel):
    """Input for compliance assessment"""

    content_type: str = Field(..., description="Type of content being assessed")
    content_id: str | None = Field(None, description="Unique identifier")
    content: str | None = Field(None, description="Content to assess (if applicable)")
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Context flags
    is_ai_generated: bool = False
    user_age: int | None = None
    contains_pii: bool = False
    contains_phi: bool = False
    is_high_risk_decision: bool = False

    # Selected modules for assessment
    modules: list[RegulationId] = Field(
        default=[RegulationId.EU_AI_ACT], description="Modules to assess against"
    )


class ControlResult(BaseModel):
    """Result of assessing a single control"""

    control_id: str
    control_name: str
    module_id: RegulationId
    status: ComplianceStatus
    score: float = Field(..., ge=0.0, le=1.0)
    evidence: str | None = None
    findings: list[str] = Field(default_factory=list)
    remediation: str | None = None
    assessed_at: datetime = Field(default_factory=datetime.utcnow)


class ModuleResult(BaseModel):
    """Result of assessing against a single compliance module"""

    module_id: RegulationId
    module_name: str
    status: ComplianceStatus
    compliance_score: float = Field(..., ge=0.0, le=1.0)
    controls_assessed: int
    controls_compliant: int
    controls_non_compliant: int
    controls_partial: int
    control_results: list[ControlResult]
    risk_tier: RiskTier | None = None
    recommendations: list[str] = Field(default_factory=list)
    requires_human_review: bool = False


class ComplianceAssessmentResult(BaseModel):
    """Complete compliance assessment result across all selected modules"""

    assessment_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Overall status
    overall_status: ComplianceStatus
    overall_score: float = Field(..., ge=0.0, le=1.0)

    # Module breakdown
    modules_assessed: list[ModuleResult]

    # Aggregate stats
    total_controls: int
    total_compliant: int
    total_non_compliant: int

    # Actionable outputs
    critical_findings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    requires_human_review: bool = False

    # ShadowTag audit proof
    audit_hash: str | None = None
    audit_url: str | None = None

    # Transparency notice (for end users)
    transparency_notice: str | None = None


# ============================================================================
# POST-GENERATION VALIDATION (GPT Store Pattern)
# ============================================================================


class ValidationRequest(BaseModel):
    """Request for post-generation compliance validation"""

    response_text: str = Field(..., description="LLM response to validate")
    context: str | None = Field(None, description="Original prompt context")
    modules: list[RegulationId] = Field(
        default=[RegulationId.GDPR, RegulationId.EU_AI_ACT],
        description="Modules to validate against",
    )
    user_metadata: dict[str, Any] = Field(default_factory=dict)


class ValidationViolation(BaseModel):
    """A detected compliance violation in generated content"""

    violation_id: str = Field(default_factory=lambda: str(uuid4()))
    module_id: RegulationId
    rule_id: str
    severity: str  # low, medium, high, critical
    description: str
    location: str | None = None  # Where in the response
    suggested_fix: str | None = None
    article_reference: str | None = None


class ValidationResult(BaseModel):
    """Result of post-generation validation"""

    validation_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    is_compliant: bool
    violations: list[ValidationViolation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    # Remediated content (if violations were auto-fixed)
    original_text: str
    remediated_text: str | None = None
    was_modified: bool = False

    # Audit
    audit_hash: str | None = None
    modules_checked: list[RegulationId]


# ============================================================================
# EVIDENCE & AUDIT MODELS
# ============================================================================


class EvidenceArtifact(BaseModel):
    """An evidence artifact for compliance documentation"""

    artifact_id: str = Field(default_factory=lambda: str(uuid4()))
    artifact_type: str  # document, log, screenshot, attestation
    name: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    storage_url: str | None = None
    sha256_hash: str | None = None
    linked_controls: list[str] = Field(default_factory=list)


class ComplianceDossier(BaseModel):
    """Complete compliance dossier (CE-style for EU AI Act)"""

    dossier_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Organization info
    organization_name: str
    system_name: str
    system_description: str

    # Module coverage
    modules: list[RegulationId]

    # Assessment summary
    latest_assessment: ComplianceAssessmentResult | None = None

    # Evidence collection
    artifacts: list[EvidenceArtifact] = Field(default_factory=list)

    # Attestation
    attestation_date: datetime | None = None
    attestation_signatory: str | None = None
    attestation_signature_hash: str | None = None

    # ShadowTag proof chain
    shadowtag_chain: list[str] = Field(default_factory=list)


class AuditLogEntry(BaseModel):
    """Single entry in the compliance audit log"""

    entry_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str  # assessment, validation, evidence_upload, attestation
    actor: str  # system, user_id, api_key_id
    module_id: RegulationId | None = None
    details: dict[str, Any] = Field(default_factory=dict)

    # Immutability
    previous_hash: str | None = None
    entry_hash: str | None = None


# ============================================================================
# SUBSCRIPTION & USAGE MODELS
# ============================================================================


class SubscriptionPlan(BaseModel):
    """User subscription plan configuration"""

    plan_id: str = Field(default_factory=lambda: str(uuid4()))
    tier: PricingTier
    base_price_usd: float

    # Included modules
    included_modules: list[RegulationId] = Field(default_factory=list)
    addon_modules: list[RegulationId] = Field(default_factory=list)

    # Usage limits
    monthly_api_calls: int = 50000
    monthly_assessments: int = 1000

    # Features
    sdk_access: bool = True
    audit_trail_access: bool = True
    dedicated_advisor: bool = False


class UsageMetrics(BaseModel):
    """API and assessment usage metrics"""

    period_start: datetime
    period_end: datetime

    api_calls_used: int = 0
    api_calls_limit: int = 50000

    assessments_used: int = 0
    assessments_limit: int = 1000

    violations_detected: int = 0
    auto_remediations: int = 0

    cost_per_inference_usd: float = 0.005
    overage_charges_usd: float = 0.0
