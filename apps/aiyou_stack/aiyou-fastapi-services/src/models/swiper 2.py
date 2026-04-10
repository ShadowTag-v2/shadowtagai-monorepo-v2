"""
Swiper Adaptive Shoppable Video Platform - Database Models

This module implements the core database models for the Swiper platform:
- Premium Beacons: Time-collapsing movies for retail
- Interactive Premium Content: User-controlled runtime
- Shoppable Narratives: In-video product purchasing
- Persuasion Layer: Family/household purchase influence
- AI Personalization: Adaptive content based on user signals
"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, validator
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# ================================================================================
# ENUMS
# ================================================================================


class VideoFormat(StrEnum):
    """Video format types"""

    SHORT_FORM = "short_form"  # TikTok/Reels style (15-60s)
    MEDIUM_FORM = "medium_form"  # Product demos (3-5min)
    LONG_FORM = "long_form"  # Premium beacons (90-120min)
    ADAPTIVE = "adaptive"  # Time-collapsing content


class RuntimeMode(StrEnum):
    """User-controlled runtime options"""

    QUICK_CUT = "quick_cut"  # 30s pitch
    STANDARD = "standard"  # 2-3min
    EXTENDED = "extended"  # 5-7min
    FULL_FEATURE = "full_feature"  # 90+ min (premium beacons)
    AUTO_ADAPTIVE = "auto_adaptive"  # AI-controlled based on context


class PersonalizationStage(StrEnum):
    """AI personalization maturity levels"""

    RULES = "rules"  # Stage 1: Simple rule-based branching
    BANDITS = "bandits"  # Stage 2: Multi-armed bandit learning
    GENERATIVE = "generative"  # Stage 3: Full AI generation


class PersuasionTarget(StrEnum):
    """Household persuasion targets"""

    SELF = "self"  # Direct buyer
    SPOUSE_PARTNER = "spouse_partner"  # Partner approval
    PARENT = "parent"  # Kids → parents
    MANAGER = "manager"  # Employee → corporate buyer
    COLLEAGUE = "colleague"  # Peer recommendation


class ProductCategory(StrEnum):
    """Shoppable product categories"""

    TOYS = "toys"
    ELECTRONICS = "electronics"
    HOME_GOODS = "home_goods"
    FASHION = "fashion"
    BEAUTY = "beauty"
    SPORTS = "sports"
    AUTOMOTIVE = "automotive"
    FOOD_BEVERAGE = "food_beverage"
    B2B_SUPPLIES = "b2b_supplies"


class BeaconType(StrEnum):
    """Premium Beacon types"""

    DRIVE_TO_STORE = "drive_to_store"  # En route to physical retail
    ONLINE_HOLD = "online_hold"  # Keep user on product page
    POST_PURCHASE = "post_purchase"  # Unlock content after buy
    LOCATION_TRIGGERED = "location_triggered"  # Geofence activation


class InteractionType(StrEnum):
    """User interaction types"""

    VIEW = "view"
    SWIPE = "swipe"
    CLICK_PRODUCT = "click_product"
    ADD_TO_CART = "add_to_cart"
    PURCHASE = "purchase"
    SHARE = "share"
    RUNTIME_CHANGE = "runtime_change"
    SEEK = "seek"
    PAUSE = "pause"


# ================================================================================
# DATABASE MODELS
# ================================================================================


class Video(Base):
    """
    Core video entity for Swiper platform
    Supports adaptive runtime, shoppable overlays, and multi-format content
    """

    __tablename__ = "videos"

    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)

    # Video metadata
    format = Column(SQLEnum(VideoFormat), nullable=False, index=True)
    base_duration_seconds = Column(Integer, nullable=False)  # Original length
    min_duration_seconds = Column(Integer)  # Minimum compressed length
    max_duration_seconds = Column(Integer)  # Maximum extended length

    # Storage and CDN
    gcs_bucket = Column(String(255), nullable=False)
    gcs_path = Column(String(1024), nullable=False)
    cdn_url = Column(String(1024), nullable=False)
    thumbnail_url = Column(String(1024))
    hls_manifest_url = Column(String(1024))  # Adaptive streaming

    # AI and personalization
    personalization_stage = Column(
        SQLEnum(PersonalizationStage), default=PersonalizationStage.RULES
    )
    available_runtimes = Column(JSON)  # List of supported runtime modes
    narrative_arcs = Column(JSON)  # Story branch definitions

    # Shoppable features
    is_shoppable = Column(Boolean, default=True)
    products_count = Column(Integer, default=0)
    avg_product_price = Column(Float)

    # Premium Beacon settings
    is_premium_beacon = Column(Boolean, default=False)
    beacon_type = Column(SQLEnum(BeaconType), nullable=True)
    location_radius_meters = Column(Integer)  # Geofence radius
    retailer_id = Column(String(36), ForeignKey("retailers.id"))

    # Performance metrics
    total_views = Column(Integer, default=0)
    total_conversions = Column(Integer, default=0)
    avg_watch_time_seconds = Column(Float)
    conversion_rate = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, index=True)

    # Relationships
    products = relationship("ProductOverlay", back_populates="video")
    interactions = relationship("UserInteraction", back_populates="video")
    persuasion_points = relationship("PersuasionPoint", back_populates="video")
    analytics = relationship("VideoAnalytics", back_populates="video")

    __table_args__ = (
        Index("idx_video_format_published", "format", "published_at"),
        Index("idx_video_beacon_retailer", "is_premium_beacon", "retailer_id"),
    )


class Product(Base):
    """
    Shoppable products linked to videos
    Supports multi-retailer, affiliate links, and dynamic pricing
    """

    __tablename__ = "products"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(SQLEnum(ProductCategory), nullable=False, index=True)

    # Pricing
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    discount_percentage = Column(Float, default=0.0)

    # Retailer integration
    retailer_id = Column(String(36), ForeignKey("retailers.id"))
    retailer_product_id = Column(String(255))  # External SKU
    buy_url = Column(String(1024), nullable=False)  # Direct purchase link
    affiliate_url = Column(String(1024))  # Affiliate tracking link

    # Product media
    image_url = Column(String(1024))
    thumbnail_url = Column(String(1024))

    # Inventory
    in_stock = Column(Boolean, default=True)
    stock_quantity = Column(Integer)

    # Performance
    total_clicks = Column(Integer, default=0)
    total_purchases = Column(Integer, default=0)
    click_through_rate = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    overlays = relationship("ProductOverlay", back_populates="product")

    __table_args__ = (
        Index("idx_product_category_price", "category", "price"),
        Index("idx_product_retailer_stock", "retailer_id", "in_stock"),
    )


class ProductOverlay(Base):
    """
    Time-based product overlays within videos
    Defines when/where products appear and how they're presented
    """

    __tablename__ = "product_overlays"

    id = Column(String(36), primary_key=True)
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)

    # Timing
    start_time_seconds = Column(Float, nullable=False)
    end_time_seconds = Column(Float, nullable=False)

    # Visual presentation
    position_x = Column(Float)  # % from left (0-100)
    position_y = Column(Float)  # % from top (0-100)
    width = Column(Float)  # % of video width
    height = Column(Float)  # % of video height

    # Interactivity
    is_clickable = Column(Boolean, default=True)
    hotspot_shape = Column(String(50))  # circle, rectangle, polygon
    hotspot_coordinates = Column(JSON)  # Detailed clickable area

    # Call-to-action
    cta_text = Column(String(100))  # e.g., "Tap to add"
    cta_style = Column(JSON)  # Color, animation, etc.

    # Performance
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    click_rate = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="products")
    product = relationship("Product", back_populates="overlays")

    __table_args__ = (Index("idx_overlay_video_time", "video_id", "start_time_seconds"),)


class PersuasionPoint(Base):
    """
    Persuasion layer: Talking points embedded in narrative
    Targets different household decision-makers (kids → parents, spouses, etc.)
    """

    __tablename__ = "persuasion_points"

    id = Column(String(36), primary_key=True)
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=False, index=True)

    # Targeting
    target_audience = Column(SQLEnum(PersuasionTarget), nullable=False, index=True)

    # Content
    message = Column(Text, nullable=False)  # The persuasive talking point
    context = Column(Text)  # When/why to show this
    narrative_integration = Column(Text)  # How it's woven into story

    # Presentation timing
    start_time_seconds = Column(Float)
    end_time_seconds = Column(Float)

    # Delivery method
    delivery_method = Column(String(50))  # dialogue, text_overlay, voiceover, end_card
    emphasis_level = Column(String(20))  # subtle, moderate, explicit

    # Examples for different targets
    # Kids → Parents: "It's safe", "It lasts forever", "Educational value"
    # Spouse: "Energy efficient", "Saves money", "Premium quality"
    # Manager: "Boosts productivity", "ROI positive", "Scalable"

    # Performance tracking
    impressions = Column(Integer, default=0)
    conversion_lift = Column(Float)  # % increase in purchases when shown

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="persuasion_points")

    __table_args__ = (Index("idx_persuasion_video_target", "video_id", "target_audience"),)


class User(Base):
    """
    User profiles for personalization and tracking
    """

    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, index=True)
    name = Column(String(255))

    # Demographics (for personalization)
    age_range = Column(String(20))  # 18-24, 25-34, etc.
    household_type = Column(String(50))  # single, couple, family_with_kids, etc.

    # Preferences
    preferred_runtime = Column(SQLEnum(RuntimeMode), default=RuntimeMode.STANDARD)
    interests = Column(JSON)  # List of ProductCategory values

    # Behavior patterns
    avg_watch_time_seconds = Column(Float)
    total_purchases = Column(Integer, default=0)
    lifetime_value = Column(Float, default=0.0)

    # Personalization profile
    personalization_data = Column(JSON)  # AI-learned preferences

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interactions = relationship("UserInteraction", back_populates="user")

    __table_args__ = (Index("idx_user_household_interests", "household_type"),)


class UserInteraction(Base):
    """
    Granular tracking of all user interactions with videos
    Powers AI personalization and analytics
    """

    __tablename__ = "user_interactions"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=False, index=True)

    # Interaction details
    interaction_type = Column(SQLEnum(InteractionType), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Context
    video_time_seconds = Column(Float)  # Where in video did this occur
    runtime_mode = Column(SQLEnum(RuntimeMode))  # Which version they watched

    # Product interaction
    product_id = Column(String(36), ForeignKey("products.id"), nullable=True, index=True)

    # Session context
    device_type = Column(String(50))  # mobile, tablet, desktop
    location_lat = Column(Float)
    location_lon = Column(Float)
    is_premium_beacon_session = Column(Boolean, default=False)

    # Behavioral signals
    scroll_depth = Column(Float)  # For online product pages
    hover_time_seconds = Column(Float)
    came_from_url = Column(String(1024))

    # Revenue tracking
    purchase_amount = Column(Float)
    currency = Column(String(3))

    # Metadata
    metadata = Column(JSON)  # Additional context

    # Relationships
    user = relationship("User", back_populates="interactions")
    video = relationship("Video", back_populates="interactions")

    __table_args__ = (
        Index("idx_interaction_user_timestamp", "user_id", "timestamp"),
        Index("idx_interaction_video_type", "video_id", "interaction_type"),
        Index("idx_interaction_beacon", "is_premium_beacon_session", "timestamp"),
    )


class Retailer(Base):
    """
    Retail partners sponsoring Premium Beacons and shoppable content
    """

    __tablename__ = "retailers"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, index=True)

    # Store details
    website_url = Column(String(1024))
    api_key = Column(String(255))  # For inventory sync

    # Location (for Premium Beacons)
    store_locations = Column(JSON)  # Array of {lat, lon, address, radius}

    # Business terms
    revenue_share_percentage = Column(Float)
    monthly_ad_spend = Column(Float)

    # Performance
    total_videos_sponsored = Column(Integer, default=0)
    total_conversions = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    videos = relationship("Video", backref="retailer")
    products = relationship("Product", backref="retailer")


class VideoAnalytics(Base):
    """
    Time-series analytics for video performance
    Tracks engagement, conversions, and AI optimization metrics
    """

    __tablename__ = "video_analytics"

    id = Column(String(36), primary_key=True)
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=False, index=True)

    # Time bucket
    timestamp = Column(DateTime, nullable=False, index=True)
    time_bucket = Column(String(20))  # hourly, daily, weekly

    # Engagement metrics
    views = Column(Integer, default=0)
    unique_viewers = Column(Integer, default=0)
    avg_watch_time_seconds = Column(Float)
    completion_rate = Column(Float)  # % who watched to end

    # Runtime distribution
    runtime_mode_breakdown = Column(JSON)  # {quick_cut: 30%, standard: 50%, etc.}

    # Conversion metrics
    product_clicks = Column(Integer, default=0)
    add_to_carts = Column(Integer, default=0)
    purchases = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)

    # Personalization performance
    personalization_stage = Column(SQLEnum(PersonalizationStage))
    arc_performance = Column(JSON)  # Which narrative arcs converted best
    persuasion_effectiveness = Column(JSON)  # Conversion lift by target audience

    # Premium Beacon specific
    drive_to_store_rate = Column(Float)  # % who actually arrived at store
    post_purchase_unlock_rate = Column(Float)  # % who bought to unlock Part 2

    # A/B test results
    test_variant = Column(String(50))
    control_vs_test_lift = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="analytics")

    __table_args__ = (
        Index("idx_analytics_video_timestamp", "video_id", "timestamp"),
        Index("idx_analytics_bucket", "time_bucket", "timestamp"),
    )


# ================================================================================
# PYDANTIC MODELS (API Request/Response)
# ================================================================================


class VideoCreate(BaseModel):
    """Request model for creating a new video"""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    format: VideoFormat
    base_duration_seconds: int = Field(..., gt=0)
    min_duration_seconds: int | None = None
    max_duration_seconds: int | None = None
    gcs_bucket: str
    gcs_path: str
    cdn_url: str
    thumbnail_url: str | None = None
    is_shoppable: bool = True
    is_premium_beacon: bool = False
    beacon_type: BeaconType | None = None
    retailer_id: str | None = None
    available_runtimes: list[RuntimeMode] = [RuntimeMode.STANDARD]

    @validator("min_duration_seconds")
    def validate_min_duration(cls, v, values):
        if v and "base_duration_seconds" in values and v > values["base_duration_seconds"]:
            raise ValueError("min_duration must be <= base_duration")
        return v


class ProductCreate(BaseModel):
    """Request model for creating a shoppable product"""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category: ProductCategory
    price: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    retailer_id: str
    buy_url: str
    image_url: str | None = None
    in_stock: bool = True


class ProductOverlayCreate(BaseModel):
    """Request model for adding product overlay to video"""

    video_id: str
    product_id: str
    start_time_seconds: float = Field(..., ge=0)
    end_time_seconds: float = Field(..., gt=0)
    position_x: float = Field(..., ge=0, le=100)
    position_y: float = Field(..., ge=0, le=100)
    width: float = Field(default=20, ge=1, le=50)
    height: float = Field(default=20, ge=1, le=50)
    cta_text: str = Field(default="Tap to shop")
    is_clickable: bool = True

    @validator("end_time_seconds")
    def validate_times(cls, v, values):
        if "start_time_seconds" in values and v <= values["start_time_seconds"]:
            raise ValueError("end_time must be > start_time")
        return v


class PersuasionPointCreate(BaseModel):
    """Request model for adding persuasion talking points"""

    video_id: str
    target_audience: PersuasionTarget
    message: str = Field(..., min_length=10)
    context: str | None = None
    narrative_integration: str | None = None
    start_time_seconds: float | None = None
    end_time_seconds: float | None = None
    delivery_method: str = Field(default="dialogue")
    emphasis_level: str = Field(default="subtle")


class VideoResponse(BaseModel):
    """Response model for video details"""

    id: str
    title: str
    description: str | None
    format: VideoFormat
    base_duration_seconds: int
    cdn_url: str
    thumbnail_url: str | None
    is_shoppable: bool
    is_premium_beacon: bool
    products_count: int
    total_views: int
    total_conversions: int
    conversion_rate: float | None
    created_at: datetime
    published_at: datetime | None

    class Config:
        from_attributes = True


class AdaptiveVideoRequest(BaseModel):
    """Request for adaptive video playback"""

    video_id: str
    user_id: str | None = None
    runtime_mode: RuntimeMode = RuntimeMode.AUTO_ADAPTIVE

    # Context signals for personalization
    device_type: str | None = None
    location_lat: float | None = None
    location_lon: float | None = None
    eta_minutes: int | None = None  # For Premium Beacons

    # Behavioral signals
    came_from_url: str | None = None
    scroll_speed: str | None = None  # fast, medium, slow
    hover_time_seconds: float | None = None

    # User preferences
    interests: list[ProductCategory] | None = None
    household_type: str | None = None


class AdaptiveVideoResponse(BaseModel):
    """Response with personalized video configuration"""

    video_id: str
    playback_url: str
    runtime_seconds: int
    selected_runtime_mode: RuntimeMode

    # Personalized narrative arc
    narrative_arc: dict[str, Any]  # Scene sequence, branch choices

    # Shoppable products (time-ordered)
    products: list[dict[str, Any]]

    # Persuasion points (targeted to user)
    persuasion_points: list[dict[str, Any]]

    # Premium Beacon specific
    is_beacon_session: bool = False
    unlock_condition: str | None = None  # e.g., "Purchase product to unlock Part 2"

    # Tracking
    session_id: str
    personalization_stage: PersonalizationStage


class InteractionCreate(BaseModel):
    """Request to log user interaction"""

    user_id: str | None = None
    video_id: str
    interaction_type: InteractionType
    video_time_seconds: float | None = None
    runtime_mode: RuntimeMode | None = None
    product_id: str | None = None
    device_type: str | None = None
    location_lat: float | None = None
    location_lon: float | None = None
    purchase_amount: float | None = None
    metadata: dict[str, Any] | None = None


class AnalyticsSummary(BaseModel):
    """Analytics summary for a video"""

    video_id: str
    total_views: int
    unique_viewers: int
    avg_watch_time_seconds: float
    completion_rate: float
    total_conversions: int
    total_revenue: float
    conversion_rate: float

    # Runtime breakdown
    runtime_mode_distribution: dict[RuntimeMode, int]

    # Top products
    top_products: list[dict[str, Any]]

    # Persuasion effectiveness
    persuasion_lift_by_target: dict[PersuasionTarget, float]

    # Premium Beacon metrics
    drive_to_store_rate: float | None = None
    post_purchase_unlock_rate: float | None = None
