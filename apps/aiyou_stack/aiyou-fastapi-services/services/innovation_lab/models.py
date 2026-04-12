"""
Innovation Lab Service - Data Models
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class InnovationType(StrEnum):
    """Types of innovation requests"""

    IDEATION = "ideation"
    PROTOTYPE = "prototype"
    TECH_EVALUATION = "tech_evaluation"
    EXPERIMENT = "experiment"
    FUTURE_TECH = "future_tech"
    CRAZY_IDEAS = "crazy_ideas"


class TechDomain(StrEnum):
    """Technology domains for innovation"""

    AI_ML = "ai_ml"
    BLOCKCHAIN = "blockchain"
    QUANTUM = "quantum"
    IOT = "iot"
    AR_VR = "ar_vr"
    EDGE_COMPUTING = "edge_computing"
    BIOTECH = "biotech"
    ROBOTICS = "robotics"
    GENERAL = "general"


class InnovationRequest(BaseModel):
    """Request model for innovation endpoints"""

    prompt: str = Field(..., description="The innovation challenge or question", min_length=10)
    innovation_type: InnovationType = Field(
        default=InnovationType.IDEATION, description="Type of innovation exploration"
    )
    tech_domain: TechDomain | None = Field(
        default=TechDomain.GENERAL, description="Primary technology domain"
    )
    context: str | None = Field(None, description="Additional context or constraints")
    max_ideas: int = Field(
        default=5, ge=1, le=10, description="Maximum number of ideas to generate"
    )
    risk_tolerance: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Risk tolerance (0=safe, 1=crazy)"
    )


class IdeaMetrics(BaseModel):
    """Metrics for evaluating an idea"""

    innovation_score: float = Field(ge=0.0, le=1.0, description="How innovative (0-1)")
    feasibility_score: float = Field(ge=0.0, le=1.0, description="How feasible (0-1)")
    impact_score: float = Field(ge=0.0, le=1.0, description="Potential impact (0-1)")
    risk_level: float = Field(ge=0.0, le=1.0, description="Risk level (0-1)")


class InnovationIdea(BaseModel):
    """A single innovation idea"""

    title: str = Field(..., description="Brief title for the idea")
    description: str = Field(..., description="Detailed description")
    key_features: list[str] = Field(
        default_factory=list, description="Key features or capabilities"
    )
    tech_stack: list[str] = Field(default_factory=list, description="Technologies involved")
    metrics: IdeaMetrics = Field(..., description="Evaluation metrics")
    next_steps: list[str] = Field(default_factory=list, description="Suggested next steps")


class InnovationResponse(BaseModel):
    """Response model for innovation endpoints"""

    request_type: InnovationType
    summary: str = Field(..., description="Executive summary of the analysis")
    ideas: list[InnovationIdea] = Field(default_factory=list, description="Generated ideas")
    key_insights: list[str] = Field(default_factory=list, description="Key insights discovered")
    recommended_experiments: list[str] = Field(
        default_factory=list, description="Recommended experiments to validate ideas"
    )
    tech_trends: list[str] = Field(
        default_factory=list, description="Relevant emerging tech trends"
    )
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in analysis")


class PrototypeRequest(BaseModel):
    """Request for rapid prototype design"""

    concept: str = Field(..., description="The concept to prototype", min_length=10)
    tech_domain: TechDomain = Field(default=TechDomain.GENERAL)
    constraints: list[str] | None = Field(default_factory=list, description="Design constraints")
    timeline: str | None = Field(default="2 weeks", description="Expected timeline")


class PrototypeDesign(BaseModel):
    """Prototype design output"""

    concept: str
    architecture: str = Field(..., description="High-level architecture")
    components: list[str] = Field(default_factory=list, description="Key components")
    tech_stack: list[str] = Field(default_factory=list)
    implementation_phases: list[str] = Field(default_factory=list)
    estimated_effort: str = Field(..., description="Estimated effort")
    risks: list[str] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)


class TechEvaluationRequest(BaseModel):
    """Request for evaluating emerging technology"""

    technology: str = Field(..., description="Technology to evaluate")
    use_case: str | None = Field(None, description="Specific use case to evaluate")
    comparison_with: list[str] | None = Field(
        default_factory=list, description="Technologies to compare against"
    )


class TechEvaluationResponse(BaseModel):
    """Technology evaluation output"""

    technology: str
    maturity_level: str = Field(..., description="Technology maturity level")
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    threats: list[str] = Field(default_factory=list)
    adoption_readiness: float = Field(ge=0.0, le=1.0)
    recommended_use_cases: list[str] = Field(default_factory=list)
    learning_resources: list[str] = Field(default_factory=list)


class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str
    service: str
    version: str
    innovation_ready: bool
