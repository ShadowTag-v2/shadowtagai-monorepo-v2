# ruff: noqa: F403, F405
"""Adaptive Shoppable Video Platform (Amazon Challenger) - FastAPI Service

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

# Import models
import sys
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

sys.path.append("/home/user/shadowtag_v4-fastapi-services/src")
from models.adaptive_shoppable_video import (
    AdaptiveVideoRequest,
    AdaptiveVideoResponse,
    AnalyticsSummary,
    BeaconType,
    InteractionCreate,
    InteractionType,
    PersonalizationStage,
    PersuasionPointCreate,
    PersuasionTarget,
    ProductCategory,
    ProductCreate,
    ProductOverlayCreate,
    RuntimeMode,
    VideoCreate,
    VideoFormat,
    VideoResponse,
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
from .service import *

# API ENDPOINTS
# ================================================================================


@app.get("/")
async def root():
    """API root - AdaptiveShoppableVideo platform overview"""
    return {
        "service": "Adaptive Shoppable Video Platform (Amazon Challenger)",
        "tagline": "Billboards nag. YouTube interrupts. AdaptiveShoppableVideo entertains.",
        "version": "1.0.0",
        "features": [
            "Premium Beacons: Time-collapsing movies for drive-to-store",
            "Interactive Content: User-controlled runtime + shoppable hotspots",
            "Persuasion Layer: Household decision-maker targeting",
            "AI Personalization: Rules → Bandits → Generative",
            "Multi-format: TikTok shorts + premium features",
        ],
        "docs": "/docs",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "platform": "AdaptiveShoppableVideo",
        "videos_count": len(videos_db),
        "products_count": len(products_db),
        "total_interactions": len(interactions_db),
    }


# ================================================================================
# VIDEO MANAGEMENT
# ================================================================================


@app.post("/videos", response_model=VideoResponse, status_code=201)
async def create_video(video: VideoCreate):
    """Create a new video with adaptive shoppable features

    Supports:
    - Multiple formats (short-form, long-form, adaptive)
    - Premium Beacons for location-based experiences
    - Flexible runtime modes
    - Shoppable product integration
    """
    video_id = str(uuid.uuid4())

    video_data = {
        "id": video_id,
        **video.dict(),
        "products_count": 0,
        "total_views": 0,
        "total_conversions": 0,
        "conversion_rate": 0.0,
        "created_at": datetime.utcnow(),
        "published_at": datetime.utcnow(),
        "personalization_stage": PersonalizationStage.RULES,
        "avg_watch_time_seconds": 0.0,
    }

    videos_db[video_id] = video_data

    return VideoResponse(**video_data)


@app.get("/videos", response_model=list[VideoResponse])
async def list_videos(
    format: VideoFormat | None = None,
    is_premium_beacon: bool | None = None,
    retailer_id: str | None = None,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
):
    """List videos with filtering options

    Filter by:
    - Format (short_form, long_form, adaptive, etc.)
    - Premium Beacon status
    - Retailer sponsorship
    """
    filtered_videos = list(videos_db.values())

    if format:
        filtered_videos = [v for v in filtered_videos if v["format"] == format]
    if is_premium_beacon is not None:
        filtered_videos = [
            v for v in filtered_videos if v["is_premium_beacon"] == is_premium_beacon
        ]
    if retailer_id:
        filtered_videos = [v for v in filtered_videos if v.get("retailer_id") == retailer_id]

    # Sort by created_at descending
    filtered_videos.sort(key=lambda x: x["created_at"], reverse=True)

    # Pagination
    paginated = filtered_videos[offset : offset + limit]

    return [VideoResponse(**v) for v in paginated]


@app.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str):
    """Get video details by ID"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoResponse(**videos_db[video_id])


# ================================================================================
# ADAPTIVE PLAYBACK - Core Innovation
# ================================================================================


@app.post("/videos/play", response_model=AdaptiveVideoResponse)
async def get_adaptive_playback(request: AdaptiveVideoRequest):
    """🎬 CORE FEATURE: Adaptive Shoppable Video Playback

    This endpoint powers AdaptiveShoppableVideo's three major innovations:

    1. **Premium Beacons (Time-Collapsing)**:
       - If user provides ETA, video runtime auto-adjusts to match drive time
       - Story ends exactly when they arrive at store
       - Buy product → unlock Part 2 for ride home

    2. **Interactive Premium Content**:
       - User chooses runtime (quick_cut, standard, extended, full_feature)
       - Shoppable products appear at optimal times
       - Click-to-cart inside the movie

    3. **Persuasion Layer**:
       - Selects talking points based on household type
       - Kids → Parents: "It's safe, educational"
       - Spouse → Spouse: "Energy efficient, premium quality"
       - Employee → Manager: "Boosts productivity, ROI positive"

    4. **AI Personalization**:
       - Stage 1 (Rules): Device type, scroll speed, hover time
       - Stage 2 (Bandits): Conversion-optimized arc selection
       - Stage 3 (Generative): Fully custom narratives per user
    """
    # Validate video exists
    if request.video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")

    video = videos_db[request.video_id]

    # Get user context
    user_context = {}
    household_type = request.household_type
    user_interests = request.interests

    if request.user_id and request.user_id in users_db:
        user = users_db[request.user_id]
        household_type = user.get("household_type", household_type)
        user_interests = user.get("interests", user_interests)

    # Calculate adaptive runtime
    behavioral_signals = {
        "scroll_speed": request.scroll_speed,
        "hover_time_seconds": request.hover_time_seconds,
    }

    runtime_seconds = calculate_adaptive_runtime(
        base_duration=video["base_duration_seconds"],
        min_duration=video.get("min_duration_seconds"),
        max_duration=video.get("max_duration_seconds"),
        mode=request.runtime_mode,
        eta_minutes=request.eta_minutes,
        behavioral_signals=behavioral_signals,
    )

    # Select narrative arc (AI personalization)
    narrative_arc = select_narrative_arc(
        video_id=request.video_id,
        user_id=request.user_id,
        personalization_stage=video["personalization_stage"],
        user_interests=user_interests,
    )

    # Get shoppable products (time-ordered)
    video_products = [p for p in product_overlays_db.values() if p["video_id"] == request.video_id]
    video_products.sort(key=lambda x: x["start_time_seconds"])

    products_list = []
    for overlay in video_products:
        product = products_db.get(overlay["product_id"])
        if product:
            products_list.append(
                {
                    "product_id": product["id"],
                    "name": product["name"],
                    "price": product["price"],
                    "currency": product["currency"],
                    "buy_url": product["buy_url"],
                    "start_time": overlay["start_time_seconds"],
                    "end_time": overlay["end_time_seconds"],
                    "position": {
                        "x": overlay["position_x"],
                        "y": overlay["position_y"],
                        "width": overlay["width"],
                        "height": overlay["height"],
                    },
                    "cta_text": overlay["cta_text"],
                },
            )

    # Select persuasion points (household targeting)
    persuasion_points = select_persuasion_points(
        video_id=request.video_id,
        household_type=household_type,
        user_context=user_context,
    )

    # Premium Beacon logic
    is_beacon_session = False
    unlock_condition = None

    if video["is_premium_beacon"]:
        is_beacon_session = True

        # Check if user is near store (geofence)
        if request.location_lat and request.location_lon and video.get("retailer_id"):
            retailer = retailers_db.get(video["retailer_id"])
            if retailer and retailer.get("store_locations"):
                # Check nearest store location
                for location in retailer["store_locations"]:
                    distance = calculate_geofence_distance(
                        request.location_lat,
                        request.location_lon,
                        location["lat"],
                        location["lon"],
                    )
                    if distance <= video.get("location_radius_meters", 5000):
                        unlock_condition = f"You're {int(distance)}m from the store. Watch Part 1 on your way. Buy the product to unlock Part 2 for the ride home!"
                        break

        if video["beacon_type"] == BeaconType.POST_PURCHASE:
            unlock_condition = "Purchase any featured product to unlock the full movie!"

    # Generate session ID for tracking
    session_id = str(uuid.uuid4())

    # Log interaction
    interactions_db.append(
        {
            "id": str(uuid.uuid4()),
            "user_id": request.user_id,
            "video_id": request.video_id,
            "interaction_type": InteractionType.VIEW,
            "timestamp": datetime.utcnow(),
            "runtime_mode": request.runtime_mode,
            "device_type": request.device_type,
            "location_lat": request.location_lat,
            "location_lon": request.location_lon,
            "is_premium_beacon_session": is_beacon_session,
            "session_id": session_id,
            "metadata": {
                "eta_minutes": request.eta_minutes,
                "came_from_url": request.came_from_url,
                "behavioral_signals": behavioral_signals,
            },
        },
    )

    # Update video view count
    videos_db[request.video_id]["total_views"] += 1

    return AdaptiveVideoResponse(
        video_id=request.video_id,
        playback_url=video["cdn_url"],
        runtime_seconds=runtime_seconds,
        selected_runtime_mode=request.runtime_mode,
        narrative_arc=narrative_arc,
        products=products_list,
        persuasion_points=persuasion_points,
        is_beacon_session=is_beacon_session,
        unlock_condition=unlock_condition,
        session_id=session_id,
        personalization_stage=video["personalization_stage"],
    )


# ================================================================================
# PRODUCT MANAGEMENT
# ================================================================================


@app.post("/products", status_code=201)
async def create_product(product: ProductCreate):
    """Create a shoppable product"""
    product_id = str(uuid.uuid4())

    product_data = {
        "id": product_id,
        **product.dict(),
        "total_clicks": 0,
        "total_purchases": 0,
        "click_through_rate": 0.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    products_db[product_id] = product_data
    return product_data


@app.get("/products")
async def list_products(
    category: ProductCategory | None = None,
    retailer_id: str | None = None,
    in_stock: bool | None = None,
    limit: int = Query(default=20, le=100),
):
    """List shoppable products"""
    filtered = list(products_db.values())

    if category:
        filtered = [p for p in filtered if p["category"] == category]
    if retailer_id:
        filtered = [p for p in filtered if p["retailer_id"] == retailer_id]
    if in_stock is not None:
        filtered = [p for p in filtered if p["in_stock"] == in_stock]

    return filtered[:limit]


@app.post("/products/overlays", status_code=201)
async def create_product_overlay(overlay: ProductOverlayCreate):
    """Add shoppable product overlay to video

    Creates clickable hotspot that appears during specific time window
    Users can tap to add-to-cart without leaving the video
    """
    # Validate video and product exist
    if overlay.video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    if overlay.product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")

    overlay_id = str(uuid.uuid4())

    overlay_data = {
        "id": overlay_id,
        **overlay.dict(),
        "clicks": 0,
        "conversions": 0,
        "click_rate": 0.0,
        "created_at": datetime.utcnow(),
    }

    product_overlays_db[overlay_id] = overlay_data

    # Update video product count
    videos_db[overlay.video_id]["products_count"] += 1

    return overlay_data


# ================================================================================
# PERSUASION LAYER
# ================================================================================


@app.post("/persuasion-points", status_code=201)
async def create_persuasion_point(point: PersuasionPointCreate):
    """🗣️ Add persuasion talking points to video

    Persuasion Layer Innovation:
    Most ads only persuade the individual. AdaptiveShoppableVideo persuades the household.

    Target audiences:
    - PARENT: Kids → Parents ("It's safe, educational, lasts forever")
    - SPOUSE_PARTNER: Spouse → Spouse ("Energy efficient, saves money, premium quality")
    - MANAGER: Employee → Manager ("Boosts productivity, ROI positive, scalable")
    - COLLEAGUE: Peer recommendations
    - SELF: Direct buyer persuasion

    Example:
    A toy video includes kid-friendly dialogue that emphasizes safety and durability.
    Kids repeat these points to parents, becoming the persuasion messenger.

    Strategic Impact:
    - Eliminates friction in family/household purchases (>70% of retail)
    - Higher conversion rates for high-consideration items
    - Unique moat: Only AdaptiveShoppableVideo targets the full decision chain

    """
    if point.video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")

    point_id = str(uuid.uuid4())

    point_data = {
        "id": point_id,
        **point.dict(),
        "impressions": 0,
        "conversion_lift": 0.0,
        "created_at": datetime.utcnow(),
    }

    persuasion_points_db[point_id] = point_data
    return point_data


@app.get("/persuasion-points")
async def list_persuasion_points(
    video_id: str | None = None, target_audience: PersuasionTarget | None = None,
):
    """List persuasion points with optional filters"""
    filtered = list(persuasion_points_db.values())

    if video_id:
        filtered = [p for p in filtered if p["video_id"] == video_id]
    if target_audience:
        filtered = [p for p in filtered if p["target_audience"] == target_audience]

    return filtered


# ================================================================================
# USER INTERACTIONS & TRACKING
# ================================================================================


@app.post("/interactions", status_code=201)
async def log_interaction(interaction: InteractionCreate):
    """Log user interaction (view, click, purchase, etc.)

    Powers AI personalization by capturing:
    - Behavioral signals (scroll, hover, seek, pause)
    - Product engagement (clicks, add-to-cart, purchases)
    - Location context (for Premium Beacons)
    - Runtime preferences

    This data feeds into:
    - Stage 2 (Bandits): Learning which arcs convert
    - Stage 3 (Generative): Full personalization models
    """
    interaction_id = str(uuid.uuid4())

    interaction_data = {
        "id": interaction_id,
        **interaction.dict(),
        "timestamp": datetime.utcnow(),
    }

    interactions_db.append(interaction_data)

    # Update relevant counters
    if interaction.interaction_type == InteractionType.PURCHASE:
        if interaction.video_id in videos_db:
            videos_db[interaction.video_id]["total_conversions"] += 1
        if interaction.product_id and interaction.product_id in products_db:
            products_db[interaction.product_id]["total_purchases"] += 1

    elif interaction.interaction_type == InteractionType.CLICK_PRODUCT:
        if interaction.product_id and interaction.product_id in products_db:
            products_db[interaction.product_id]["total_clicks"] += 1

    return {"interaction_id": interaction_id, "status": "logged"}


@app.get("/interactions")
async def get_interactions(
    video_id: str | None = None,
    user_id: str | None = None,
    interaction_type: InteractionType | None = None,
    limit: int = Query(default=100, le=1000),
):
    """Query user interactions"""
    filtered = list(interactions_db)

    if video_id:
        filtered = [i for i in filtered if i["video_id"] == video_id]
    if user_id:
        filtered = [i for i in filtered if i["user_id"] == user_id]
    if interaction_type:
        filtered = [i for i in filtered if i["interaction_type"] == interaction_type]

    # Sort by timestamp descending
    filtered.sort(key=lambda x: x["timestamp"], reverse=True)

    return filtered[:limit]


# ================================================================================
# ANALYTICS & METRICS
# ================================================================================


@app.get("/analytics/videos/{video_id}", response_model=AnalyticsSummary)
async def get_video_analytics(video_id: str):
    """Get comprehensive analytics for a video

    Metrics include:
    - Engagement: Views, completion rate, watch time
    - Conversion: Purchases, revenue, conversion rate
    - Personalization: Runtime mode distribution
    - Persuasion: Effectiveness by target audience
    - Premium Beacon: Drive-to-store rate, unlock rate
    """
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")

    video = videos_db[video_id]

    # Get all interactions for this video
    video_interactions = [i for i in interactions_db if i["video_id"] == video_id]

    # Calculate metrics
    total_views = len(
        [i for i in video_interactions if i["interaction_type"] == InteractionType.VIEW],
    )
    unique_viewers = len(set(i["user_id"] for i in video_interactions if i.get("user_id")))

    total_purchases = len(
        [i for i in video_interactions if i["interaction_type"] == InteractionType.PURCHASE],
    )
    total_revenue = sum(
        i.get("purchase_amount", 0)
        for i in video_interactions
        if i["interaction_type"] == InteractionType.PURCHASE
    )

    conversion_rate = (total_purchases / total_views * 100) if total_views > 0 else 0.0

    # Runtime mode distribution
    runtime_modes = [i.get("runtime_mode") for i in video_interactions if i.get("runtime_mode")]
    runtime_distribution = {}
    for mode in RuntimeMode:
        count = runtime_modes.count(mode)
        if count > 0:
            runtime_distribution[mode] = count

    # Top products
    product_clicks = {}
    for interaction in video_interactions:
        if interaction["interaction_type"] == InteractionType.CLICK_PRODUCT and interaction.get(
            "product_id",
        ):
            product_id = interaction["product_id"]
            product_clicks[product_id] = product_clicks.get(product_id, 0) + 1

    top_products = []
    for product_id, clicks in sorted(product_clicks.items(), key=lambda x: x[1], reverse=True)[:5]:
        if product_id in products_db:
            product = products_db[product_id]
            top_products.append(
                {
                    "product_id": product_id,
                    "name": product["name"],
                    "clicks": clicks,
                    "price": product["price"],
                },
            )

    # Persuasion effectiveness (mock - would need A/B test data)
    persuasion_lift = {}
    for target in PersuasionTarget:
        # In production: Calculate conversion lift when persuasion points shown vs. not shown
        persuasion_lift[target] = 0.0

    # Premium Beacon metrics
    beacon_interactions = [i for i in video_interactions if i.get("is_premium_beacon_session")]
    drive_to_store_rate = None
    post_purchase_unlock_rate = None

    if video["is_premium_beacon"] and beacon_interactions:
        # Mock calculations (would need actual store arrival tracking)
        drive_to_store_rate = 0.75  # 75% arrival rate
        if video["beacon_type"] == BeaconType.POST_PURCHASE:
            post_purchase_unlock_rate = 0.40  # 40% unlock rate

    return AnalyticsSummary(
        video_id=video_id,
        total_views=total_views,
        unique_viewers=unique_viewers,
        avg_watch_time_seconds=video.get("avg_watch_time_seconds", 0.0),
        completion_rate=0.65,  # Mock - would calculate from actual playback data
        total_conversions=total_purchases,
        total_revenue=total_revenue,
        conversion_rate=conversion_rate,
        runtime_mode_distribution=runtime_distribution,
        top_products=top_products,
        persuasion_lift_by_target=persuasion_lift,
        drive_to_store_rate=drive_to_store_rate,
        post_purchase_unlock_rate=post_purchase_unlock_rate,
    )


@app.get("/analytics/dashboard")
async def get_platform_analytics():
    """Platform-wide analytics dashboard

    Shows overall AdaptiveShoppableVideo performance across all videos and retailers
    """
    total_videos = len(videos_db)
    total_products = len(products_db)
    total_views = sum(v["total_views"] for v in videos_db.values())
    total_conversions = sum(v["total_conversions"] for v in videos_db.values())

    total_revenue = sum(
        i.get("purchase_amount", 0)
        for i in interactions_db
        if i["interaction_type"] == InteractionType.PURCHASE
    )

    avg_conversion_rate = (total_conversions / total_views * 100) if total_views > 0 else 0.0

    # Premium Beacon stats
    beacon_videos = [v for v in videos_db.values() if v["is_premium_beacon"]]
    beacon_interactions = [i for i in interactions_db if i.get("is_premium_beacon_session")]

    # Format breakdown
    format_distribution = {}
    for video_format in VideoFormat:
        count = len([v for v in videos_db.values() if v["format"] == video_format])
        if count > 0:
            format_distribution[video_format] = count

    return {
        "platform": "AdaptiveShoppableVideo Adaptive Shoppable Video",
        "timestamp": datetime.utcnow().isoformat(),
        "overview": {
            "total_videos": total_videos,
            "total_products": total_products,
            "total_views": total_views,
            "total_conversions": total_conversions,
            "total_revenue_usd": round(total_revenue, 2),
            "avg_conversion_rate_pct": round(avg_conversion_rate, 2),
        },
        "premium_beacons": {
            "total_beacon_videos": len(beacon_videos),
            "total_beacon_sessions": len(beacon_interactions),
            "avg_beacon_session_length_min": 45,  # Mock
        },
        "format_distribution": format_distribution,
        "personalization": {
            "rules_stage_videos": len(
                [
                    v
                    for v in videos_db.values()
                    if v["personalization_stage"] == PersonalizationStage.RULES
                ],
            ),
            "bandits_stage_videos": len(
                [
                    v
                    for v in videos_db.values()
                    if v["personalization_stage"] == PersonalizationStage.BANDITS
                ],
            ),
            "generative_stage_videos": len(
                [
                    v
                    for v in videos_db.values()
                    if v["personalization_stage"] == PersonalizationStage.GENERATIVE
                ],
            ),
        },
        "top_categories": [
            {
                "category": cat,
                "products": len([p for p in products_db.values() if p["category"] == cat]),
            }
            for cat in ProductCategory
            if len([p for p in products_db.values() if p["category"] == cat]) > 0
        ],
    }


# ================================================================================
# RETAILER MANAGEMENT
# ================================================================================


@app.post("/retailers", status_code=201)
async def create_retailer(
    name: str,
    website_url: str | None = None,
    store_locations: list[dict] | None = None,
    revenue_share_percentage: float = 10.0,
):
    """Register a retail partner for Premium Beacons

    Retailers sponsor location-based content and shoppable videos
    """
    retailer_id = str(uuid.uuid4())

    retailer_data = {
        "id": retailer_id,
        "name": name,
        "website_url": website_url,
        "store_locations": store_locations or [],
        "revenue_share_percentage": revenue_share_percentage,
        "monthly_ad_spend": 0.0,
        "total_videos_sponsored": 0,
        "total_conversions": 0,
        "total_revenue": 0.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    retailers_db[retailer_id] = retailer_data
    return retailer_data


@app.get("/retailers")
async def list_retailers():
    """List all retail partners"""
    return list(retailers_db.values())


@app.get("/retailers/{retailer_id}/performance")
async def get_retailer_performance(retailer_id: str):
    """Get performance metrics for a specific retailer"""
    if retailer_id not in retailers_db:
        raise HTTPException(status_code=404, detail="Retailer not found")

    retailer = retailers_db[retailer_id]

    # Get all videos for this retailer
    retailer_videos = [v for v in videos_db.values() if v.get("retailer_id") == retailer_id]

    total_views = sum(v["total_views"] for v in retailer_videos)
    total_conversions = sum(v["total_conversions"] for v in retailer_videos)

    # Calculate revenue from interactions
    retailer_revenue = sum(
        i.get("purchase_amount", 0)
        for i in interactions_db
        if i["interaction_type"] == InteractionType.PURCHASE
        and i["video_id"] in [v["id"] for v in retailer_videos]
    )

    return {
        "retailer_id": retailer_id,
        "name": retailer["name"],
        "videos_sponsored": len(retailer_videos),
        "total_views": total_views,
        "total_conversions": total_conversions,
        "total_revenue_usd": round(retailer_revenue, 2),
        "conversion_rate_pct": round(
            (total_conversions / total_views * 100) if total_views > 0 else 0.0, 2,
        ),
        "revenue_share_pct": retailer["revenue_share_percentage"],
        "retailer_payout_usd": round(
            retailer_revenue * (retailer["revenue_share_percentage"] / 100), 2,
        ),
    }


# ================================================================================
# STARTUP EVENT
# ================================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize platform with demo data
    """
    print("🎥 Adaptive Shoppable Video Platform (Amazon Challenger) starting...")
    print("✅ Billboards nag. YouTube interrupts. AdaptiveShoppableVideo entertains.")

    # Create demo retailer (Walmart)
    walmart_id = str(uuid.uuid4())
    retailers_db[walmart_id] = {
        "id": walmart_id,
        "name": "Walmart",
        "website_url": "https://walmart.com",
        "store_locations": [
            {
                "lat": 37.7749,
                "lon": -122.4194,
                "address": "San Francisco, CA",
                "radius": 5000,
            },
            {
                "lat": 34.0522,
                "lon": -118.2437,
                "address": "Los Angeles, CA",
                "radius": 5000,
            },
        ],
        "revenue_share_percentage": 15.0,
        "monthly_ad_spend": 50000.0,
        "total_videos_sponsored": 0,
        "total_conversions": 0,
        "total_revenue": 0.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    # Create demo Premium Beacon video (Superman doll movie)
    superman_video_id = str(uuid.uuid4())
    videos_db[superman_video_id] = {
        "id": superman_video_id,
        "title": "Superman: The Adventure Begins - Part 1",
        "description": "A time-collapsing superhero adventure. Watch Part 1 on your way to Walmart. Buy the Superman doll to unlock Part 2 for the ride home!",
        "format": VideoFormat.LONG_FORM,
        "base_duration_seconds": 5400,  # 90 minutes
        "min_duration_seconds": 1800,  # 30 minutes (compressed)
        "max_duration_seconds": 7200,  # 120 minutes (extended)
        "gcs_bucket": "adaptive_shoppable_video-videos",
        "gcs_path": "premium-beacons/superman-adventure-part1.mp4",
        "cdn_url": "https://cdn.adaptive_shoppable_video.com/videos/superman-adventure-part1/manifest.m3u8",
        "thumbnail_url": "https://cdn.adaptive_shoppable_video.com/thumbnails/superman-adventure.jpg",
        "hls_manifest_url": "https://cdn.adaptive_shoppable_video.com/videos/superman-adventure-part1/manifest.m3u8",
        "personalization_stage": PersonalizationStage.BANDITS,
        "available_runtimes": [RuntimeMode.AUTO_ADAPTIVE, RuntimeMode.FULL_FEATURE],
        "is_shoppable": True,
        "is_premium_beacon": True,
        "beacon_type": BeaconType.DRIVE_TO_STORE,
        "location_radius_meters": 5000,
        "retailer_id": walmart_id,
        "products_count": 1,
        "total_views": 0,
        "total_conversions": 0,
        "conversion_rate": 0.0,
        "avg_watch_time_seconds": 0.0,
        "created_at": datetime.utcnow(),
        "published_at": datetime.utcnow(),
    }

    # Create Superman product
    superman_product_id = str(uuid.uuid4())
    products_db[superman_product_id] = {
        "id": superman_product_id,
        "name": "Superman Action Figure - Collectible Edition",
        "description": "Official DC Comics Superman action figure. As seen in the movie!",
        "category": ProductCategory.TOYS,
        "price": 29.99,
        "currency": "USD",
        "discount_percentage": 10.0,
        "retailer_id": walmart_id,
        "retailer_product_id": "DC-SUPERMAN-001",
        "buy_url": "https://walmart.com/products/superman-action-figure",
        "image_url": "https://cdn.adaptive_shoppable_video.com/products/superman-figure.jpg",
        "in_stock": True,
        "stock_quantity": 500,
        "total_clicks": 0,
        "total_purchases": 0,
        "click_through_rate": 0.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    # Create product overlay
    overlay_id = str(uuid.uuid4())
    product_overlays_db[overlay_id] = {
        "id": overlay_id,
        "video_id": superman_video_id,
        "product_id": superman_product_id,
        "start_time_seconds": 4500.0,  # Appears at 75 minutes
        "end_time_seconds": 5400.0,  # Until end
        "position_x": 80.0,
        "position_y": 80.0,
        "width": 15.0,
        "height": 15.0,
        "is_clickable": True,
        "cta_text": "Get your Superman!",
        "clicks": 0,
        "conversions": 0,
        "click_rate": 0.0,
        "created_at": datetime.utcnow(),
    }

    # Create persuasion points (Kids → Parents)
    persuasion_1_id = str(uuid.uuid4())
    persuasion_points_db[persuasion_1_id] = {
        "id": persuasion_1_id,
        "video_id": superman_video_id,
        "target_audience": PersuasionTarget.PARENT,
        "message": "This Superman figure is made from safe, durable materials that last for years of play!",
        "context": "Target parents concerned about toy safety and longevity",
        "narrative_integration": "Character dialogue emphasizes durability during action scene",
        "start_time_seconds": 2700.0,
        "end_time_seconds": 2715.0,
        "delivery_method": "dialogue",
        "emphasis_level": "subtle",
        "impressions": 0,
        "conversion_lift": 0.0,
        "created_at": datetime.utcnow(),
    }

    persuasion_2_id = str(uuid.uuid4())
    persuasion_points_db[persuasion_2_id] = {
        "id": persuasion_2_id,
        "video_id": superman_video_id,
        "target_audience": PersuasionTarget.PARENT,
        "message": "Educational play that inspires heroism and builds imagination",
        "context": "Target parents looking for developmental value",
        "narrative_integration": "Narrator mentions educational benefits",
        "start_time_seconds": 4200.0,
        "end_time_seconds": 4210.0,
        "delivery_method": "voiceover",
        "emphasis_level": "moderate",
        "impressions": 0,
        "conversion_lift": 0.0,
        "created_at": datetime.utcnow(),
    }

    print(f"✅ Created demo Premium Beacon: '{videos_db[superman_video_id]['title']}'")
    print(f"✅ Retailer: Walmart (ID: {walmart_id})")
    print(f"✅ Product: Superman Action Figure (${products_db[superman_product_id]['price']})")
    print("✅ Persuasion Layer: 2 parent-targeted talking points")
    print("🚀 AdaptiveShoppableVideo platform ready!")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
