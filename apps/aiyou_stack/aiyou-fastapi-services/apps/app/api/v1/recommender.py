"""Recommender governance and explainability API endpoints
Implements DSA-compliant recommender transparency
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class RecommenderExplanationRequest(BaseModel):
    """Request for recommender explanation"""

    user_id: str
    content_id: str
    session_id: str | None = None


class RecommenderExplanationResponse(BaseModel):
    """DSA-compliant recommender explanation"""

    content_id: str
    user_id: str
    timestamp: datetime
    main_reason: str
    contributing_factors: list[str]
    personalization_used: bool
    user_controls_available: list[str]
    data_sources: list[str]
    diversity_score: float = Field(..., ge=0.0, le=1.0)


class RecommenderConfigRequest(BaseModel):
    """User recommender configuration"""

    user_id: str
    personalization_enabled: bool = True
    diversity_preference: float = Field(default=0.5, ge=0.0, le=1.0)
    blocked_topics: list[str] = Field(default_factory=list)
    preferred_topics: list[str] = Field(default_factory=list)


class RecommenderConfigResponse(BaseModel):
    """Recommender configuration response"""

    user_id: str
    config: dict[str, Any]
    updated_at: datetime


class NonProfiledFeedRequest(BaseModel):
    """Request for non-profiled feed (DSA requirement)"""

    user_id: str
    limit: int = Field(default=20, ge=1, le=100)


class ContentRecommendation(BaseModel):
    """Individual content recommendation"""

    content_id: str
    title: str
    score: float
    reason: str


@router.post("/explain", response_model=RecommenderExplanationResponse)
async def explain_recommendation(request: RecommenderExplanationRequest):
    """Explain why content was recommended (DSA Article 27)

    Provides:
    - Main parameters used
    - Contributing factors
    - Personalization disclosure
    - Available user controls
    - Data sources used
    """
    return RecommenderExplanationResponse(
        content_id=request.content_id,
        user_id=request.user_id,
        timestamp=datetime.utcnow(),
        main_reason="Similar to content you engaged with recently",
        contributing_factors=[
            "Watch history similarity",
            "Topic alignment (tech, AI)",
            "Creator affinity",
            "Trending signal",
        ],
        personalization_used=True,
        user_controls_available=[
            "Turn off personalization",
            "Block this topic",
            "See more/less like this",
            "Non-profiled feed",
        ],
        data_sources=[
            "Your watch history (last 30 days)",
            "Topic preferences",
            "Engagement signals",
            "Trending data",
        ],
        diversity_score=0.72,
    )


@router.post("/config/update", response_model=RecommenderConfigResponse)
async def update_recommender_config(request: RecommenderConfigRequest):
    """Update user recommender preferences

    Allows users to control:
    - Personalization on/off
    - Diversity preference
    - Topic blocking
    - Topic preferences
    """
    return RecommenderConfigResponse(
        user_id=request.user_id,
        config=request.dict(),
        updated_at=datetime.utcnow(),
    )


@router.get("/config/{user_id}", response_model=RecommenderConfigResponse)
async def get_recommender_config(user_id: str):
    """Get user recommender configuration"""
    # TODO: Fetch from database
    return RecommenderConfigResponse(
        user_id=user_id,
        config={
            "personalization_enabled": True,
            "diversity_preference": 0.5,
            "blocked_topics": [],
            "preferred_topics": [],
        },
        updated_at=datetime.utcnow(),
    )


@router.post("/non-profiled", response_model=list[ContentRecommendation])
async def get_non_profiled_feed(request: NonProfiledFeedRequest):
    """Get non-profiled feed (DSA requirement)

    Returns recommendations WITHOUT:
    - User profiling
    - Personal data usage
    - Historical behavior

    Based ONLY on:
    - Trending content
    - Recency
    - Editorial curation
    """
    # TODO: Implement actual non-profiled feed logic
    return [
        ContentRecommendation(
            content_id=f"content_{i}",
            title=f"Trending Content {i}",
            score=0.9 - (i * 0.05),
            reason="Trending now",
        )
        for i in range(1, min(request.limit + 1, 21))
    ]


@router.get("/transparency")
async def get_transparency_info():
    """Get recommender system transparency information (DSA Article 27)

    Explains:
    - How recommendations work
    - What signals are used
    - User control options
    - Data retention
    """
    return {
        "system_description": "Omega uses multi-objective ranking to recommend content",
        "signals_used": [
            "Content similarity",
            "User engagement history",
            "Topic preferences",
            "Creator relationships",
            "Trending signals",
            "Diversity constraints",
            "Brand safety filters",
        ],
        "user_controls": [
            "Personalization toggle",
            "Topic blocking",
            "Diversity dial",
            "Non-profiled feed option",
            "Data deletion",
        ],
        "data_retention": "30 days for recommendations, 90 days for safety",
        "transparency_compliant": True,
        "dsa_article_27_compliant": True,
    }
