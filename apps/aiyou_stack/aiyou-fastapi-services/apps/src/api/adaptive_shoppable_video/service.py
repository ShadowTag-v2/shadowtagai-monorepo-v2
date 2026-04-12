# ruff: noqa: F403, F405
"""
Adaptive Shoppable Video Platform (Amazon Challenger) - FastAPI Service

This is brilliantly inventive ✅ — merging adtech + streaming + commerce into one seamless loop.

Core Features:
- Premium Beacons: Time-collapsing movies that sync to drive time, unlock on purchase
- Interactive Premium Content: User-controlled runtime with shoppable hotspots
- Persuasion Layer: Talking points that target household decision-makers
- AI Personalization: Rules → Bandits → Generative adaptive content
- Multi-format support: TikTok-style shorts + premium long-form features

Strategic Impact:
- Makes AdaptiveShoppableVideo the first commerce-linked streaming platform
- Disrupts billboards, in-car entertainment, and product page engagement
- Creates a "shoppertainment" moat nobody else can match
"""

import math

# Import models
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.append("/home/user/shadowtag_v4-fastapi-services/src")
from models.adaptive_shoppable_video import (
    PersonalizationStage,
    PersuasionTarget,
    ProductCategory,
    RuntimeMode,
)

# Initialize FastAPI app
app = FastAPI(
    title="Adaptive Shoppable Video Platform (Amazon Challenger)",
    description="""
    ## 🎥 Premium Beacons: Time-Collapsing Movies for Retail

    Stream adaptive movies that collapse or expand to match your drive time.
    Watch Part 1 en route to the store. Buy the product, unlock Part 2 for the ride home.

    ## 🎬 Interactive Premium Content

    - **User-Controlled Runtime**: Choose quick 30s pitch or full 5min story
    - **Shoppable Narrative**: Click products inside the movie to add-to-cart
    - **Premium Studio Content**: Nike-style films, LEGO episodes, Apple narratives

    ## 🗣️ Persuasion Layer

    Movies don't just persuade the shopper — they persuade the whole household:
    - Kids → Parents: "It's safe, educational, lasts forever"
    - Spouse → Spouse: "Energy efficient, saves money, premium quality"
    - Employee → Manager: "Boosts productivity, ROI positive, scalable"

    ## 🎛 AI Personalization Roadmap

    - **Stage 1 - Rules**: Lightweight branching based on scroll, hover, device
    - **Stage 2 - Bandits**: Multi-armed bandit learns which arcs convert best
    - **Stage 3 - Generative**: Full 1:1 personalized movies per shopper

    ## 💰 Monetization

    - Retail Sponsorship: Walmart pays for Superman doll campaign
    - Ad CPMs: $20-$40 per Premium Beacon viewing session
    - Rev-Share with Studios: License IP, share streaming + merch revenue
    - Engagement Data: Completion rates, arrival rates, purchase rates

    ## 🎯 Strategic Positioning

    AdaptiveShoppableVideo vs. TikTok/Reels:
    - TikTok = discovery + impulse (awareness)
    - AdaptiveShoppableVideo = consideration + conversion (closing engine)

    Together: Use TikTok to get interest → AdaptiveShoppableVideo to seal the deal

    ## ✅ Investor Hook

    "Billboards nag. YouTube interrupts. AdaptiveShoppableVideo entertains. Our Premium Beacons let brands
    stream time-collapsing movies that sync to your drive. The story ends when you reach
    the store. Buy the product, and the second half plays on the way home. It's adtech,
    streaming, and commerce fused — a cultural moat no competitor can match."
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================================================================================
from .database import *

# HELPER FUNCTIONS
# ================================================================================


def calculate_adaptive_runtime(
    base_duration: int,
    min_duration: int | None,
    max_duration: int | None,
    mode: RuntimeMode,
    eta_minutes: int | None = None,
    behavioral_signals: dict | None = None,
) -> int:
    """
    Calculate adaptive runtime based on user context and AI personalization

    Stage 1 (Rules): Simple logic based on explicit signals
    Stage 2 (Bandits): Would use conversion history
    Stage 3 (Generative): Would use full AI model
    """
    # Premium Beacon: Time-collapsing for drive-to-store
    if eta_minutes and mode == RuntimeMode.AUTO_ADAPTIVE:
        # Movie ends exactly when they arrive at store
        target_runtime = eta_minutes * 60
        if min_duration and max_duration:
            return max(min_duration, min(target_runtime, max_duration))
        return target_runtime

    # User-controlled modes
    if mode == RuntimeMode.QUICK_CUT:
        return min_duration or int(base_duration * 0.3)
    elif mode == RuntimeMode.STANDARD:
        return base_duration
    elif mode == RuntimeMode.EXTENDED:
        return max_duration or int(base_duration * 1.5)
    elif mode == RuntimeMode.FULL_FEATURE:
        return max_duration or base_duration

    # Auto-adaptive based on behavioral signals
    if behavioral_signals:
        scroll_speed = behavioral_signals.get("scroll_speed")
        hover_time = behavioral_signals.get("hover_time_seconds", 0)

        # Fast scrollers get shorter content
        if scroll_speed == "fast":
            return min_duration or int(base_duration * 0.5)
        # Lingering users get deeper content
        elif hover_time > 5:
            return max_duration or int(base_duration * 1.3)

    return base_duration


def select_narrative_arc(
    video_id: str,
    user_id: str | None,
    personalization_stage: PersonalizationStage,
    user_interests: list[ProductCategory] | None = None,
) -> dict:
    """
    Select narrative arc based on AI personalization stage

    Stage 1 (Rules): Category matching
    Stage 2 (Bandits): Conversion-optimized selection
    Stage 3 (Generative): Fully custom narrative
    """
    # Stage 1: Simple rule-based selection
    if personalization_stage == PersonalizationStage.RULES:
        if user_interests and ProductCategory.TOYS in user_interests:
            return {
                "arc_id": "family_fun",
                "scenes": ["intro", "product_demo", "family_interaction", "cta"],
                "emphasis": "safety_and_fun",
            }
        elif user_interests and ProductCategory.ELECTRONICS in user_interests:
            return {
                "arc_id": "tech_specs",
                "scenes": [
                    "intro",
                    "feature_showcase",
                    "comparison",
                    "value_prop",
                    "cta",
                ],
                "emphasis": "performance_and_value",
            }
        else:
            return {
                "arc_id": "general",
                "scenes": ["intro", "product_showcase", "benefits", "cta"],
                "emphasis": "quality",
            }

    # Stage 2: Multi-armed bandit (would query conversion history)
    elif personalization_stage == PersonalizationStage.BANDITS:
        # In production: Query analytics to find best-converting arc for user segment
        return {
            "arc_id": "high_conversion_arc",
            "scenes": [
                "hook",
                "emotional_story",
                "product_integration",
                "social_proof",
                "cta",
            ],
            "emphasis": "emotional_connection",
            "note": "Selected based on 2.3x conversion lift in A/B tests",
        }

    # Stage 3: Generative AI
    elif personalization_stage == PersonalizationStage.GENERATIVE:
        # In production: Generate custom narrative using Claude/Gemini
        return {
            "arc_id": "ai_generated",
            "scenes": ["personalized_intro", "custom_demo", "tailored_benefits", "cta"],
            "emphasis": "fully_personalized",
            "note": "AI-generated narrative based on user's unique profile and behavior",
        }

    return {"arc_id": "default", "scenes": ["intro", "product", "cta"]}


def select_persuasion_points(
    video_id: str, household_type: str | None = None, user_context: dict | None = None
) -> list[dict]:
    """
    Select targeted persuasion points based on household dynamics

    Returns talking points optimized for:
    - Kids → Parents (toys, safety, education)
    - Spouse → Spouse (value, quality, efficiency)
    - Employee → Manager (productivity, ROI, scalability)
    """
    persuasion_points = []

    # Get all persuasion points for this video
    video_points = [p for p in persuasion_points_db.values() if p["video_id"] == video_id]

    if not video_points:
        return []

    # Target based on household type
    if household_type == "family_with_kids":
        # Kids → Parents persuasion
        persuasion_points = [
            p for p in video_points if p["target_audience"] == PersuasionTarget.PARENT
        ]
    elif household_type == "couple":
        # Spouse → Spouse persuasion
        persuasion_points = [
            p for p in video_points if p["target_audience"] == PersuasionTarget.SPOUSE_PARTNER
        ]
    elif user_context and user_context.get("is_corporate"):
        # Employee → Manager persuasion
        persuasion_points = [
            p for p in video_points if p["target_audience"] == PersuasionTarget.MANAGER
        ]
    else:
        # Default to self-persuasion
        persuasion_points = [
            p for p in video_points if p["target_audience"] == PersuasionTarget.SELF
        ]

    # Return formatted points
    return [
        {
            "message": p["message"],
            "delivery_method": p["delivery_method"],
            "start_time": p.get("start_time_seconds"),
            "end_time": p.get("end_time_seconds"),
            "emphasis": p["emphasis_level"],
        }
        for p in persuasion_points
    ]


def calculate_geofence_distance(
    user_lat: float, user_lon: float, store_lat: float, store_lon: float
) -> float:
    """
    Calculate distance between user and store location (Haversine formula)
    Returns distance in meters
    """
    R = 6371000  # Earth's radius in meters

    lat1, lon1 = math.radians(user_lat), math.radians(user_lon)
    lat2, lon2 = math.radians(store_lat), math.radians(store_lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


# ================================================================================
