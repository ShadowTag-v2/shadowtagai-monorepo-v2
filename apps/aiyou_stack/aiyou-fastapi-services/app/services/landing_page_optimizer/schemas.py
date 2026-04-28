# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Pydantic models and schemas for Landing Page Optimizer"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class FocusArea(StrEnum):
    """Focus areas for landing page optimization"""

    HEADLINES = "headlines"
    CTA = "cta"
    SOCIAL_PROOF = "social_proof"
    COPY = "copy"
    FORMS = "forms"
    LAYOUT = "layout"
    VALUE_PROPOSITION = "value_proposition"
    TRUST_SIGNALS = "trust_signals"
    ALL = "all"


class Priority(StrEnum):
    """Priority levels for recommendations"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OptimizePageRequest(BaseModel):
    """Request to optimize a landing page"""

    page_content: str = Field(
        ...,
        description="HTML or markdown content of the landing page",
        min_length=10,
        max_length=50000,
    )
    focus_areas: list[FocusArea] | None = Field(
        default=[FocusArea.ALL],
        description="Specific areas to focus on for optimization",
    )
    current_conversion_rate: float | None = Field(
        default=None,
        description="Current conversion rate as percentage (0-100)",
        ge=0,
        le=100,
    )
    target_conversion_rate: float | None = Field(
        default=None,
        description="Target conversion rate to achieve (0-100)",
        ge=0,
        le=100,
    )
    page_url: HttpUrl | None = Field(
        default=None,
        description="URL of the landing page (for context)",
    )
    target_audience: str | None = Field(
        default=None,
        description="Description of target audience",
        max_length=500,
    )
    product_service: str | None = Field(
        default=None,
        description="Description of product or service being offered",
        max_length=1000,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "page_content": "<h1>Welcome to Our App</h1><p>Sign up now to get started!</p><button>Sign Up</button>",
                "focus_areas": ["headlines", "cta"],
                "current_conversion_rate": 2.5,
                "target_conversion_rate": 5.0,
                "target_audience": "Small business owners looking to improve their online presence",
                "product_service": "Website builder platform",
            },
        }


class Recommendation(BaseModel):
    """Individual optimization recommendation"""

    title: str = Field(..., description="Title of the recommendation")
    description: str = Field(
        ...,
        description="Detailed description of the issue and recommendation",
    )
    category: FocusArea = Field(..., description="Category this recommendation belongs to")
    priority: Priority = Field(..., description="Priority level for implementation")
    expected_impact: str = Field(..., description="Expected impact on conversions")
    implementation_steps: list[str] = Field(
        default_factory=list,
        description="Step-by-step implementation guide",
    )
    before_example: str | None = Field(default=None, description="Example of current state")
    after_example: str | None = Field(default=None, description="Example of improved state")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Improve Primary Headline",
                "description": "The current headline is too generic and doesn't communicate clear value",
                "category": "headlines",
                "priority": "high",
                "expected_impact": "Could improve conversion rate by 15-25%",
                "implementation_steps": [
                    "Replace generic headline with specific benefit",
                    "Include numbers or measurable outcomes",
                    "Test A/B variants",
                ],
                "before_example": "Welcome to Our App",
                "after_example": "Build Your Professional Website in 10 Minutes",
            },
        }


class HeadlineVariation(BaseModel):
    """Headline variation suggestion"""

    text: str = Field(..., description="Headline text")
    reasoning: str = Field(..., description="Why this headline works")
    target_emotion: str = Field(..., description="Target emotion this headline appeals to")


class CTAVariation(BaseModel):
    """Call-to-action variation suggestion"""

    text: str = Field(..., description="CTA button text")
    color_suggestion: str | None = Field(default=None, description="Suggested color")
    placement: str = Field(..., description="Suggested placement on page")
    reasoning: str = Field(..., description="Why this CTA works")


class SocialProofSuggestion(BaseModel):
    """Social proof element suggestion"""

    type: str = Field(..., description="Type of social proof (testimonial, stats, logos, etc.)")
    content: str = Field(..., description="Suggested content")
    placement: str = Field(..., description="Where to place this element")


class OptimizationAnalysis(BaseModel):
    """Detailed analysis of the landing page"""

    overall_score: float = Field(
        ...,
        description="Overall optimization score (0-100)",
        ge=0,
        le=100,
    )
    key_strengths: list[str] = Field(
        default_factory=list,
        description="Key strengths of current page",
    )
    key_weaknesses: list[str] = Field(default_factory=list, description="Key weaknesses to address")
    recommendations: list[Recommendation] = Field(
        default_factory=list,
        description="Detailed recommendations",
    )
    headline_variations: list[HeadlineVariation] | None = Field(
        default=None,
        description="Alternative headline suggestions",
    )
    cta_variations: list[CTAVariation] | None = Field(
        default=None,
        description="Alternative CTA suggestions",
    )
    social_proof_suggestions: list[SocialProofSuggestion] | None = Field(
        default=None,
        description="Social proof element suggestions",
    )
    estimated_conversion_lift: str | None = Field(
        default=None,
        description="Estimated conversion rate improvement if recommendations implemented",
    )


class OptimizePageResponse(BaseModel):
    """Response from landing page optimization"""

    status: str = Field(default="success", description="Response status")
    analysis: OptimizationAnalysis = Field(..., description="Detailed analysis and recommendations")
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata about the analysis",
    )
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of analysis")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "analysis": {
                    "overall_score": 65,
                    "key_strengths": ["Clear visual hierarchy", "Mobile responsive design"],
                    "key_weaknesses": [
                        "Weak value proposition",
                        "Generic CTA text",
                        "Missing social proof",
                    ],
                    "recommendations": [],
                    "estimated_conversion_lift": "20-35%",
                },
                "metadata": {"focus_areas": ["headlines", "cta"], "processing_time_ms": 2500},
                "timestamp": "2024-01-15T10:30:00Z",
            },
        }


class GenerateHeadlinesRequest(BaseModel):
    """Request to generate headline variations"""

    product_service: str = Field(..., description="Product or service description")
    target_audience: str = Field(..., description="Target audience description")
    key_benefit: str = Field(..., description="Primary benefit or value proposition")
    tone: str | None = Field(
        default="professional",
        description="Desired tone (professional, casual, urgent, playful, etc.)",
    )
    count: int = Field(default=5, ge=1, le=20, description="Number of variations to generate")


class GenerateHeadlinesResponse(BaseModel):
    """Response with generated headline variations"""

    status: str = Field(default="success")
    headlines: list[HeadlineVariation] = Field(..., description="Generated headline variations")
    timestamp: datetime = Field(default_factory=datetime.now)


class GenerateCTARequest(BaseModel):
    """Request to generate CTA variations"""

    action_type: str = Field(..., description="Type of action (signup, purchase, download, etc.)")
    product_service: str = Field(..., description="Product or service description")
    urgency_level: str | None = Field(
        default="medium",
        description="Level of urgency (low, medium, high)",
    )
    count: int = Field(default=5, ge=1, le=20, description="Number of variations to generate")


class GenerateCTAResponse(BaseModel):
    """Response with generated CTA variations"""

    status: str = Field(default="success")
    ctas: list[CTAVariation] = Field(..., description="Generated CTA variations")
    timestamp: datetime = Field(default_factory=datetime.now)


class GenerateSocialProofRequest(BaseModel):
    """Request to generate social proof suggestions"""

    product_service: str = Field(..., description="Product or service description")
    existing_data: dict | None = Field(
        default=None,
        description="Existing data (number of users, ratings, etc.)",
    )
    proof_types: list[str] | None = Field(
        default=["testimonials", "statistics", "trust_badges"],
        description="Types of social proof to generate",
    )


class GenerateSocialProofResponse(BaseModel):
    """Response with social proof suggestions"""

    status: str = Field(default="success")
    suggestions: list[SocialProofSuggestion] = Field(..., description="Social proof suggestions")
    timestamp: datetime = Field(default_factory=datetime.now)
