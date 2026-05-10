"""Tokable Gesture Streaming Platform API
FastAPI endpoints for silent gesture-based streaming with AI interpretation

Part of PNKLN Core Stack™ - Revenue-focused creator economy platform
Target: $2.5M seed, 500k MAU, $2M+ ARR
"""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

# Initialize FastAPI app


# ============================================================================
# Enums
# ============================================================================


class StreamMode(StrEnum):
    """Streaming modes"""

    PRIVATE = "private"  # Practice mode
    CHARADES = "charades"  # Game mode
    PUBLIC = "public"  # Public streaming
    TOURNAMENT = "tournament"  # Competition mode


class StreamStatus(StrEnum):
    """Stream lifecycle status"""

    PENDING = "pending"
    LIVE = "live"
    PAUSED = "paused"
    ENDED = "ended"
    MINTING_NFT = "minting_nft"


class GestureType(StrEnum):
    """Recognized gesture categories"""

    DANCE = "dance"
    HAND_SIGN = "hand_sign"
    FACIAL_EXPRESSION = "facial_expression"
    BODY_POSE = "body_pose"
    COMBO = "combo"


class EmotionalState(StrEnum):
    """Real-time emotional inference"""

    HAPPY = "happy"
    CONFUSED = "confused"
    EXCITED = "excited"
    FOCUSED = "focused"
    PLAYFUL = "playful"
    NEUTRAL = "neutral"


class RevenueType(StrEnum):
    """Revenue stream types"""

    TIP = "tip"
    NFT_SALE = "nft_sale"
    SUBSCRIPTION = "subscription"
    BRAND_SPONSORSHIP = "brand_sponsorship"
    TOURNAMENT_PRIZE = "tournament_prize"


class UserRole(StrEnum):
    """Platform roles"""

    CREATOR = "creator"
    FAN = "fan"
    SPONSOR = "sponsor"
    ADMIN = "admin"


# ============================================================================
# Core Models
# ============================================================================


class User(BaseModel):
    """Platform user"""

    id: str = Field(..., description="User ID")
    username: str = Field(..., min_length=3, max_length=30)
    role: UserRole
    avatar_url: str | None = None
    bio: str | None = Field(None, max_length=500)
    verified: bool = Field(default=False)
    created_at: datetime

    # Creator stats
    follower_count: int = Field(default=0, ge=0)
    total_streams: int = Field(default=0, ge=0)
    total_revenue_usd: Decimal = Field(default=Decimal("0.00"), ge=0)
    leaderboard_rank: int | None = None

    # Subscription info
    is_pro: bool = Field(default=False)
    pro_expires_at: datetime | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "user_abc123",
                "username": "silentdancer_pro",
                "role": "creator",
                "avatar_url": "https://cdn.tokable.ai/avatars/abc123.png",
                "bio": "Movement artist | No words needed 💃",
                "verified": True,
                "created_at": "2025-10-01T00:00:00Z",
                "follower_count": 12450,
                "total_streams": 87,
                "total_revenue_usd": "1247.50",
                "leaderboard_rank": 42,
                "is_pro": True,
                "pro_expires_at": "2026-01-01T00:00:00Z",
            },
        }
    )


class GestureFrame(BaseModel):
    """Single frame of gesture data"""

    timestamp: float = Field(..., description="Milliseconds from stream start")
    gesture_type: GestureType
    confidence: float = Field(..., ge=0, le=1)
    emotion: EmotionalState
    emotion_confidence: float = Field(..., ge=0, le=1)
    keypoints: dict[str, dict] = Field(default_factory=dict, description="Body/hand keypoints")

    # AI interpretation
    interpreted_text: str | None = None
    generated_art_url: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "timestamp": 12450.5,
                "gesture_type": "dance",
                "confidence": 0.92,
                "emotion": "playful",
                "emotion_confidence": 0.87,
                "keypoints": {
                    "left_hand": {"x": 0.45, "y": 0.32},
                    "right_hand": {"x": 0.55, "y": 0.38},
                },
                "interpreted_text": "Spinning with joy!",
                "generated_art_url": "https://cdn.tokable.ai/frames/frame_12450.png",
            },
        }
    )


class Stream(BaseModel):
    """Active or completed streaming session"""

    id: str = Field(..., description="Stream ID")
    creator_id: str
    creator_username: str

    title: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)

    mode: StreamMode
    status: StreamStatus

    # Timing
    scheduled_start: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    duration_seconds: int | None = Field(None, ge=0)

    # Engagement
    current_viewers: int = Field(default=0, ge=0)
    peak_viewers: int = Field(default=0, ge=0)
    total_views: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)

    # Revenue
    tips_total_usd: Decimal = Field(default=Decimal("0.00"), ge=0)
    tips_count: int = Field(default=0, ge=0)

    # NFT
    nft_minted: bool = Field(default=False)
    nft_token_id: str | None = None
    nft_sale_price_usd: Decimal | None = None

    # AI assets
    frames_generated: int = Field(default=0, ge=0)
    highlight_clips: list[str] = Field(default_factory=list)

    # Metadata
    tags: list[str] = Field(default_factory=list)
    thumbnail_url: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "stream_xyz789",
                "creator_id": "user_abc123",
                "creator_username": "silentdancer_pro",
                "title": "Silent Sunday Vibes 🌊",
                "description": "Pure movement, pure AI art",
                "mode": "public",
                "status": "live",
                "scheduled_start": "2025-11-17T18:00:00Z",
                "started_at": "2025-11-17T18:02:15Z",
                "ended_at": None,
                "duration_seconds": 1847,
                "current_viewers": 234,
                "peak_viewers": 312,
                "total_views": 1247,
                "likes": 187,
                "tips_total_usd": "47.50",
                "tips_count": 23,
                "nft_minted": False,
                "nft_token_id": None,
                "nft_sale_price_usd": None,
                "frames_generated": 1847,
                "highlight_clips": [],
                "tags": ["dance", "abstract", "chill"],
                "thumbnail_url": "https://cdn.tokable.ai/thumbs/stream_xyz789.jpg",
            },
        }
    )


class NFT(BaseModel):
    """Minted NFT from completed stream"""

    id: str
    stream_id: str
    creator_id: str

    token_id: str = Field(..., description="Blockchain token ID")
    contract_address: str
    blockchain: str = Field(default="polygon", description="polygon, ethereum, etc.")

    title: str
    description: str
    media_url: str = Field(..., description="IPFS or CDN URL to final video/art")
    thumbnail_url: str

    # Pricing
    mint_price_usd: Decimal
    current_price_usd: Decimal | None = None
    royalty_percentage: float = Field(default=10.0, ge=0, le=50)

    # Sales
    is_listed: bool = Field(default=True)
    sold: bool = Field(default=False)
    sold_at: datetime | None = None
    sold_price_usd: Decimal | None = None
    buyer_id: str | None = None

    # Metadata
    minted_at: datetime
    stream_duration_seconds: int
    total_frames: int
    emotion_summary: dict[str, float] = Field(default_factory=dict)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "nft_def456",
                "stream_id": "stream_xyz789",
                "creator_id": "user_abc123",
                "token_id": "0x1a2b3c4d5e6f",
                "contract_address": "0xTOKABLE_CONTRACT",
                "blockchain": "polygon",
                "title": "Silent Sunday Vibes 🌊 - Nov 17",
                "description": "30 minutes of pure gesture art generation",
                "media_url": "ipfs://QmXXXXXXXX",
                "thumbnail_url": "https://cdn.tokable.ai/nft/nft_def456_thumb.jpg",
                "mint_price_usd": "25.00",
                "current_price_usd": "25.00",
                "royalty_percentage": 10.0,
                "is_listed": True,
                "sold": False,
                "sold_at": None,
                "sold_price_usd": None,
                "buyer_id": None,
                "minted_at": "2025-11-17T18:45:00Z",
                "stream_duration_seconds": 1847,
                "total_frames": 1847,
                "emotion_summary": {
                    "playful": 0.45,
                    "excited": 0.30,
                    "happy": 0.20,
                    "neutral": 0.05,
                },
            },
        }
    )


class Tournament(BaseModel):
    """Creator competition/tournament"""

    id: str
    title: str
    description: str

    # Timing
    registration_start: datetime
    registration_end: datetime
    tournament_start: datetime
    tournament_end: datetime

    # Rules
    mode: StreamMode = Field(default=StreamMode.TOURNAMENT)
    min_duration_seconds: int = Field(default=600, ge=60)
    max_participants: int = Field(default=100, ge=2)

    # Prize pool
    prize_pool_usd: Decimal = Field(..., ge=0)
    prize_distribution: dict[str, Decimal] = Field(
        default_factory=lambda: {
            "1st": Decimal("50.00"),
            "2nd": Decimal("30.00"),
            "3rd": Decimal("20.00"),
        },
    )

    # Participation
    participants: list[str] = Field(default_factory=list)
    current_leaderboard: list[dict] = Field(default_factory=list)

    # Status
    is_active: bool = Field(default=True)
    completed: bool = Field(default=False)
    winners: list[str] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "tourn_nov_week3",
                "title": "Tokable Championship - Week 3",
                "description": "Best silent performance wins $500!",
                "registration_start": "2025-11-15T00:00:00Z",
                "registration_end": "2025-11-17T23:59:59Z",
                "tournament_start": "2025-11-18T00:00:00Z",
                "tournament_end": "2025-11-24T23:59:59Z",
                "mode": "tournament",
                "min_duration_seconds": 600,
                "max_participants": 100,
                "prize_pool_usd": "500.00",
                "prize_distribution": {
                    "1st": "250.00",
                    "2nd": "150.00",
                    "3rd": "100.00",
                },
                "participants": ["user_abc123", "user_xyz789"],
                "current_leaderboard": [
                    {"user_id": "user_abc123", "score": 9450, "rank": 1},
                    {"user_id": "user_xyz789", "score": 8720, "rank": 2},
                ],
                "is_active": True,
                "completed": False,
                "winners": [],
            },
        }
    )


class RevenueEvent(BaseModel):
    """Revenue tracking event"""

    id: str
    user_id: str
    revenue_type: RevenueType
    amount_usd: Decimal = Field(..., ge=0)

    # Context
    stream_id: str | None = None
    nft_id: str | None = None
    tournament_id: str | None = None

    # Platform cut
    platform_fee_usd: Decimal = Field(..., ge=0)
    creator_payout_usd: Decimal = Field(..., ge=0)

    # Payment
    processed: bool = Field(default=False)
    processed_at: datetime | None = None

    timestamp: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "rev_abc123",
                "user_id": "user_abc123",
                "revenue_type": "tip",
                "amount_usd": "5.00",
                "stream_id": "stream_xyz789",
                "nft_id": None,
                "tournament_id": None,
                "platform_fee_usd": "1.00",
                "creator_payout_usd": "4.00",
                "processed": True,
                "processed_at": "2025-11-17T18:30:00Z",
                "timestamp": "2025-11-17T18:29:45Z",
            },
        }
    )


# ============================================================================
# Request/Response Models
# ============================================================================


class CreateStreamRequest(BaseModel):
    """Request to create new stream"""

    title: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    mode: StreamMode
    scheduled_start: datetime | None = None
    tags: list[str] = Field(default_factory=list, max_items=10)
    enable_subtitles: bool = Field(default=False, description="Pre-loaded subtitle script")
    subtitle_script: str | None = Field(None, max_length=5000)


class StartStreamRequest(BaseModel):
    """Request to start live streaming"""

    stream_id: str


class EndStreamRequest(BaseModel):
    """Request to end stream"""

    stream_id: str
    mint_nft: bool = Field(default=True, description="Mint NFT after stream")
    nft_price_usd: Decimal | None = Field(None, ge=0.01)


class SendTipRequest(BaseModel):
    """Fan tipping creator"""

    stream_id: str
    amount_usd: Decimal = Field(..., ge=1.00, le=1000.00)
    message: str | None = Field(None, max_length=200)


class ListNFTRequest(BaseModel):
    """List NFT for sale"""

    nft_id: str
    price_usd: Decimal = Field(..., ge=0.01)


class BuyNFTRequest(BaseModel):
    """Purchase NFT"""

    nft_id: str


class LeaderboardResponse(BaseModel):
    """Creator leaderboard"""

    period: str = Field(..., description="daily, weekly, monthly, all-time")
    top_creators: list[dict]
    updated_at: datetime


class MetricsResponse(BaseModel):
    """Platform metrics"""

    # User metrics
    total_users: int
    total_creators: int
    total_fans: int

    # Streaming metrics
    active_streams: int
    total_streams_today: int
    total_streams_all_time: int

    # Revenue metrics
    revenue_today_usd: Decimal
    revenue_month_usd: Decimal
    revenue_all_time_usd: Decimal
    avg_tip_usd: Decimal

    # NFT metrics
    nfts_minted_total: int
    nfts_sold_total: int
    nft_sales_volume_usd: Decimal

    # Engagement
    avg_stream_duration_minutes: float
    avg_viewers_per_stream: float

    timestamp: datetime


# ============================================================================
