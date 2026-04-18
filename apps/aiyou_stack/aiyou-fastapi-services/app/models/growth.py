"""Growth Engineering Data Models

Pydantic models for growth engineering requests and responses.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AnalysisType(StrEnum):
    """Types of growth analysis"""

    USER_HOOKS = "user_hooks"
    VIRAL_LOOP = "viral_loop"
    AB_TEST = "ab_test"
    GROWTH_METRICS = "growth_metrics"
    ENGAGEMENT_FEATURE = "engagement_feature"
    ANALYTICS = "analytics"
    REFERRAL = "referral"
    GENERAL = "general"


class UserHookAnalysisRequest(BaseModel):
    """Request model for user hook analysis"""

    app_name: str = Field(..., description="Name of the application")
    user_flows: list[dict[str, Any]] = Field(..., description="User flow data")
    current_features: list[str] = Field(..., description="Current features list")
    metrics: dict[str, Any] | None = Field(None, description="Current metrics data")
    goals: list[str] | None = Field(None, description="Specific goals for analysis")

    class Config:
        json_schema_extra = {
            "example": {
                "app_name": "MyApp",
                "user_flows": [
                    {"step": "signup", "conversion_rate": 0.65},
                    {"step": "first_action", "conversion_rate": 0.45},
                ],
                "current_features": ["profile", "sharing", "notifications"],
                "metrics": {"dau": 1000, "retention_d7": 0.30},
                "goals": ["improve_activation", "increase_retention"],
            },
        }


class ViralLoopRequest(BaseModel):
    """Request model for viral loop design"""

    product_name: str = Field(..., description="Product name")
    value_proposition: str = Field(..., description="Core value proposition")
    target_audience: str = Field(..., description="Target audience description")
    current_users: int | None = Field(None, description="Current user count")
    sharing_incentive: str | None = Field(None, description="Proposed sharing incentive")
    constraints: list[str] | None = Field(None, description="Technical or business constraints")

    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "CollabTool",
                "value_proposition": "Team collaboration made simple",
                "target_audience": "Remote teams and startups",
                "current_users": 5000,
                "sharing_incentive": "Extra storage for referrals",
                "constraints": ["budget_limited", "mobile_first"],
            },
        }


class ABTestRequest(BaseModel):
    """Request model for A/B test design"""

    experiment_name: str = Field(..., description="Name of the experiment")
    hypothesis: str = Field(..., description="Test hypothesis")
    variants: list[dict[str, Any]] = Field(..., description="Test variants")
    primary_metric: str = Field(..., description="Primary metric to measure")
    secondary_metrics: list[str] | None = Field(None, description="Secondary metrics")
    expected_effect_size: float | None = Field(None, description="Expected effect size")
    traffic_allocation: dict[str, float] | None = Field(None, description="Traffic split")

    class Config:
        json_schema_extra = {
            "example": {
                "experiment_name": "Onboarding_Flow_V2",
                "hypothesis": "Simplified onboarding increases activation by 15%",
                "variants": [
                    {"name": "control", "description": "Current 5-step flow"},
                    {"name": "treatment", "description": "New 3-step flow"},
                ],
                "primary_metric": "activation_rate",
                "secondary_metrics": ["time_to_first_action", "completion_rate"],
                "expected_effect_size": 0.15,
                "traffic_allocation": {"control": 0.5, "treatment": 0.5},
            },
        }


class GrowthMetricsRequest(BaseModel):
    """Request model for growth metrics analysis"""

    metrics: dict[str, Any] = Field(..., description="Current metrics data")
    time_period: str = Field(..., description="Time period for analysis")
    goals: list[str] | None = Field(None, description="Growth goals")
    benchmarks: dict[str, float] | None = Field(None, description="Industry benchmarks")

    class Config:
        json_schema_extra = {
            "example": {
                "metrics": {
                    "signups": 1500,
                    "activated_users": 800,
                    "dau": 600,
                    "retention_d7": 0.35,
                    "viral_coefficient": 0.4,
                },
                "time_period": "last_30_days",
                "goals": ["reach_1000_dau", "improve_retention"],
                "benchmarks": {"retention_d7": 0.40, "viral_coefficient": 0.6},
            },
        }


class EngagementFeatureRequest(BaseModel):
    """Request model for engagement feature design"""

    feature_type: str = Field(
        ...,
        description="Type of feature (gamification, notifications, etc.)",
    )
    objective: str = Field(..., description="Feature objective")
    target_users: str = Field(..., description="Target user segment")
    constraints: list[str] | None = Field(None, description="Design constraints")
    existing_features: list[str] | None = Field(
        None,
        description="Existing features to integrate with",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "feature_type": "gamification",
                "objective": "Increase daily engagement by 25%",
                "target_users": "Active users with 7+ day streak",
                "constraints": ["mobile_friendly", "low_development_cost"],
                "existing_features": ["profile", "achievements", "leaderboard"],
            },
        }


class AnalyticsTrackingRequest(BaseModel):
    """Request model for analytics implementation"""

    events_to_track: list[dict[str, Any]] = Field(..., description="Events to track")
    metrics_needed: list[str] = Field(..., description="Metrics to calculate")
    platform: str = Field(..., description="Platform (web, mobile, both)")
    tools: list[str] | None = Field(None, description="Analytics tools to use")
    compliance_requirements: list[str] | None = Field(None, description="Privacy/compliance needs")

    class Config:
        json_schema_extra = {
            "example": {
                "events_to_track": [
                    {"name": "user_signup", "properties": ["source", "device"]},
                    {"name": "feature_used", "properties": ["feature_name", "duration"]},
                ],
                "metrics_needed": ["dau", "retention", "funnel_conversion"],
                "platform": "web",
                "tools": ["mixpanel", "amplitude"],
                "compliance_requirements": ["gdpr", "ccpa"],
            },
        }


class ReferralOptimizationRequest(BaseModel):
    """Request model for referral system optimization"""

    referral_metrics: dict[str, Any] = Field(..., description="Current referral metrics")
    referral_flow: list[str] = Field(..., description="Steps in referral flow")
    incentives: dict[str, Any] = Field(..., description="Current incentive structure")
    issues: list[str] | None = Field(None, description="Known issues or concerns")

    class Config:
        json_schema_extra = {
            "example": {
                "referral_metrics": {
                    "invites_sent": 1000,
                    "invites_clicked": 300,
                    "signups_from_referrals": 100,
                    "referrer_conversion": 0.25,
                },
                "referral_flow": ["share_button", "invite_modal", "share_link", "friend_signup"],
                "incentives": {"referrer": "10 credits", "referee": "5 credits"},
                "issues": ["low_click_rate", "high_dropoff_at_signup"],
            },
        }


class GeneralGrowthQuery(BaseModel):
    """Request model for general growth queries"""

    query: str = Field(..., description="Growth engineering question")
    context: dict[str, Any] | None = Field(None, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "How can I improve my product's viral coefficient?",
                "context": {
                    "current_k_factor": 0.3,
                    "product_type": "social_app",
                    "stage": "early_growth",
                },
            },
        }


class AgentResponse(BaseModel):
    """Standard response model for agent operations"""

    success: bool = Field(..., description="Whether the operation succeeded")
    timestamp: str = Field(..., description="Response timestamp")
    analysis_type: str = Field(..., description="Type of analysis performed")
    results: list[Any] = Field(..., description="Analysis results")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class AgentMetadata(BaseModel):
    """Agent metadata model"""

    name: str
    category: str
    description: str
    version: str
    capabilities: list[str]


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: str
    agent: str
    version: str
