"""Pydantic models for Gemini AI analysis."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AnalysisType(StrEnum):
    """Types of Gemini analysis."""

    INGESTION_LAYER = "ingestion_layer"
    JUDGE_SIX = "judge_six"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    COVERAGE_ANALYSIS = "coverage_analysis"
    COMPLIANCE_AUDIT = "compliance_audit"
    CUSTOM = "custom"


class ConfidenceLevel(StrEnum):
    """Confidence levels for analysis."""

    HIGH = "high"  # >= 70%
    MEDIUM = "medium"  # 60-70%
    LOW = "low"  # < 60%


class AnalysisSection(BaseModel):
    """A section of the analysis report."""

    section_name: str = Field(..., description="Name of the section")
    content: str = Field(..., description="Section content")
    confidence: float = Field(..., description="Confidence score (0-1)")
    key_findings: list[str] = Field(default_factory=list, description="Key findings")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")


class GeminiAnalysisRequest(BaseModel):
    """Request for Gemini analysis."""

    analysis_type: AnalysisType = Field(..., description="Type of analysis to perform")
    target: str = Field(..., description="Target system/component to analyze")
    context: str | None = Field(None, description="Additional context")

    # Data sources for analysis
    architecture_specs: str | None = Field(None, description="Architecture specifications")
    metrics_data: dict | None = Field(None, description="Metrics data")
    documentation: str | None = Field(None, description="System documentation")

    # Analysis parameters
    confidence_threshold: float = Field(default=0.6, description="Minimum confidence (0-1)")
    include_recommendations: bool = Field(default=True, description="Include recommendations")
    detailed_analysis: bool = Field(default=True, description="Detailed vs summary analysis")


class GeminiAnalysisResponse(BaseModel):
    """Response from Gemini analysis."""

    analysis_id: str = Field(..., description="Unique analysis ID")
    analysis_type: AnalysisType = Field(..., description="Type of analysis performed")
    target: str = Field(..., description="Target system/component")

    # Analysis results
    overall_confidence: float = Field(..., description="Overall confidence score (0-1)")
    confidence_level: ConfidenceLevel = Field(..., description="Confidence level")

    sections: list[AnalysisSection] = Field(..., description="Analysis sections")

    # Summary
    executive_summary: str = Field(..., description="Executive summary")
    key_findings: list[str] = Field(default_factory=list, description="Key findings")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")
    risks: list[str] = Field(default_factory=list, description="Identified risks")

    # Metadata
    model_used: str = Field(
        default="gemini-3.1-flash-lite-preview", description="Gemini model used"
    )
    tokens_used: int | None = Field(None, description="Tokens consumed")
    analysis_time_seconds: float = Field(..., description="Analysis duration")

    created_at: datetime = Field(default_factory=datetime.utcnow)


class IngestionLayerAnalysis(BaseModel):
    """Specialized analysis for ingestion layer."""

    # Architecture Analysis
    architecture_type: str = Field(..., description="E.g., 'GKE CronJob Multi-Container'")
    architecture_strengths: list[str] = Field(default_factory=list)
    architecture_weaknesses: list[str] = Field(default_factory=list)

    # Key Metrics Analysis
    daily_items_analysis: str | None = None
    source_diversity_analysis: str | None = None
    cost_efficiency_analysis: str | None = None

    # Quality Gates
    quality_gate_status: dict[str, bool] = Field(default_factory=dict)
    quality_recommendations: list[str] = Field(default_factory=list)

    # Ethical Compliance
    ethical_compliance_score: float = Field(..., description="Compliance score (0-1)")
    compliance_findings: list[str] = Field(default_factory=list)

    # Multi-Source Coverage
    coverage_score: float = Field(..., description="Coverage diversity score (0-1)")
    coverage_gaps: list[str] = Field(default_factory=list)

    # Tier Classification
    tier_distribution_optimal: bool = Field(..., description="Is tier distribution optimal?")
    tier_recommendations: list[str] = Field(default_factory=list)

    # AM Briefing Effectiveness
    briefing_effectiveness_score: float | None = Field(None, description="Effectiveness (0-1)")
    briefing_recommendations: list[str] = Field(default_factory=list)

    # Integration Analysis
    integration_status: str = Field(..., description="Integration health")
    integration_issues: list[str] = Field(default_factory=list)

    # Cost Model
    monthly_cost_estimate: float = Field(..., description="Estimated monthly cost (USD)")
    cost_optimization_recommendations: list[str] = Field(default_factory=list)

    # Overall Assessment
    production_readiness: str = Field(..., description="Production readiness assessment")
    critical_blockers: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class ComparisonAnalysisRequest(BaseModel):
    """Request to compare two systems (e.g., Judge #6 vs Ingestion Layer)."""

    system_a_name: str
    system_a_specs: str
    system_b_name: str
    system_b_specs: str
    comparison_aspects: list[str] = Field(
        default_factory=lambda: [
            "Architecture",
            "Key Metrics",
            "Integration",
            "Unique Features",
            "Cost Model",
            "Quality Focus",
        ],
    )


class ComparisonAnalysisResponse(BaseModel):
    """Response from comparison analysis."""

    analysis_id: str
    system_a_name: str
    system_b_name: str

    comparisons: dict[str, dict[str, str]] = Field(
        ...,
        description="Aspect -> {system_a: value, system_b: value, analysis: text}",
    )

    synergies: list[str] = Field(default_factory=list, description="Identified synergies")
    conflicts: list[str] = Field(default_factory=list, description="Identified conflicts")
    integration_recommendations: list[str] = Field(default_factory=list)

    overall_assessment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PromptTemplate(BaseModel):
    """Template for Gemini prompts."""

    template_id: str
    name: str
    description: str
    analysis_type: AnalysisType
    template: str = Field(..., description="Prompt template with {placeholders}")
    required_placeholders: list[str] = Field(default_factory=list)
    example_output: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
