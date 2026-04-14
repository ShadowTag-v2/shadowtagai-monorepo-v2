"""Pydantic models for API request/response schemas"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AnalysisType(StrEnum):
    """Types of market analysis"""

    COMPETITIVE = "competitive_analysis"
    FEATURE_COMPARISON = "feature_comparison"
    SWOT = "swot_analysis"
    GAP = "gap_analysis"
    DIFFERENTIATION = "differentiation"
    QUICK = "quick_analysis"


class AgentRequest(BaseModel):
    """Base request model for agent interactions"""

    prompt: str = Field(..., description="User prompt or question")
    context: dict[str, Any] | None = Field(
        default={}, description="Additional context for the request",
    )
    stream: bool = Field(default=False, description="Whether to stream the response")


class MarketAnalysisRequest(BaseModel):
    """Request model for market analysis"""

    prompt: str = Field(
        ...,
        description="Analysis request description",
        example="Compare our product features to top 3 competitors",
    )
    product: str | None = Field(None, description="Your product name", example="AcmeSaaS")
    competitors: list[str] | None = Field(
        None,
        description="List of competitor names",
        example=["CompetitorA", "CompetitorB", "CompetitorC"],
    )
    features: list[str] | None = Field(
        None,
        description="List of features to analyze",
        example=["API Access", "Real-time Analytics", "Custom Reports"],
    )
    analysis_type: AnalysisType | None = Field(
        default=AnalysisType.COMPETITIVE, description="Type of analysis to perform",
    )


class FeatureItem(BaseModel):
    """Feature with metadata"""

    name: str = Field(..., description="Feature name")
    description: str | None = Field(None, description="Feature description")
    impact: str | None = Field(None, description="Impact level: high, medium, low")
    effort: str | None = Field(None, description="Effort level: high, medium, low")
    status: str | None = Field(None, description="Current status: planned, in-development, shipped")


class CompetitorAnalysisRequest(BaseModel):
    """Structured competitor analysis request"""

    product: str = Field(..., description="Your product name")
    competitors: list[str] = Field(..., description="List of competitors to analyze", min_length=1)
    features: list[str] = Field(..., description="Features to compare", min_length=1)


class FeaturePrioritizationRequest(BaseModel):
    """Request for feature prioritization"""

    features: list[FeatureItem] = Field(
        ..., description="List of features to prioritize", min_length=1,
    )
    criteria: dict[str, float] | None = Field(
        default=None, description="Custom prioritization criteria weights",
    )


class AgentResponse(BaseModel):
    """Base response model for agent interactions"""

    agent: str = Field(..., description="Agent name")
    status: str = Field(..., description="Response status")
    analysis: str | None = Field(None, description="Analysis text")
    error: str | None = Field(None, description="Error message if failed")


class MarketAnalysisResponse(BaseModel):
    """Response model for market analysis"""

    agent: str = Field(..., description="Agent name")
    analysis: str = Field(..., description="Analysis result")
    model: str = Field(..., description="AI model used")
    prompt_tokens: int = Field(..., description="Input tokens used")
    completion_tokens: int = Field(..., description="Output tokens used")
    status: str = Field(..., description="Request status")
    structured_insights: dict[str, Any] | None = Field(None, description="Structured analysis data")


class CompetitorAnalysisResponse(BaseModel):
    """Structured competitor analysis response"""

    feature_matrix: dict[str, Any] = Field(..., description="Feature comparison matrix")
    coverage_statistics: dict[str, Any] = Field(..., description="Feature coverage stats")
    gap_analysis: dict[str, Any] = Field(..., description="Feature gap analysis")
    recommendations: list[str] = Field(..., description="Strategic recommendations")


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Service health status")
    agent: str | None = Field(None, description="Agent name")
    version: str | None = Field(None, description="Agent version")
    capabilities: list[str] | None = Field(None, description="Agent capabilities")


class AgentInfo(BaseModel):
    """Agent information response"""

    name: str = Field(..., description="Agent name")
    version: str = Field(..., description="Agent version")
    description: str = Field(..., description="Agent description")
    capabilities: list[str] = Field(..., description="Agent capabilities")
    use_cases: list[str] = Field(..., description="Common use cases")
    analysis_types: list[str] = Field(..., description="Supported analysis types")
