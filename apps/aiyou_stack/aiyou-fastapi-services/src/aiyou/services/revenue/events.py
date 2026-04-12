"""
Revenue event definitions.

Defines the schema for all revenue-generating events across the platform.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EventType(StrEnum):
    """Types of revenue events."""

    # Content events (CineVerse)
    CONTENT_VIEW = "content.view"
    CONTENT_COMPLETE = "content.complete"
    CONTENT_PURCHASE = "content.purchase"

    # Subscription events
    SUBSCRIPTION_STARTED = "subscription.started"
    SUBSCRIPTION_RENEWED = "subscription.renewed"
    SUBSCRIPTION_UPGRADED = "subscription.upgraded"
    SUBSCRIPTION_CANCELED = "subscription.canceled"

    # Commerce events (AiU Digital Mall)
    PURCHASE_COMPLETED = "purchase.completed"
    PURCHASE_REFUNDED = "purchase.refunded"

    # Gaming events (GamePort)
    GAME_SESSION_START = "game.session.start"
    GAME_PURCHASE = "game.purchase"
    IN_APP_PURCHASE = "game.iap"

    # Infrastructure events
    GPU_ALLOCATION = "infra.gpu.allocation"
    API_USAGE = "infra.api.usage"
    STORAGE_USAGE = "infra.storage.usage"

    # Ad events
    AD_IMPRESSION = "ad.impression"
    AD_CLICK = "ad.click"
    AD_CONVERSION = "ad.conversion"


class ServiceType(StrEnum):
    """Platform services that generate revenue."""

    CINEVERSE = "cineverse"
    GAMEPORT = "gameport"
    COMMERCE = "commerce"
    INFRASTRUCTURE = "infrastructure"
    ADVERTISING = "advertising"


class RevenueEvent(BaseModel):
    """
    Revenue event model.

    Represents a single revenue-generating event in the platform.
    All events are streamed to BigQuery for analytics.
    """

    # Event identification
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: EventType
    service: ServiceType

    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_date: str = Field(default="")  # YYYY-MM-DD for partitioning

    # User context
    user_id: str | None = None
    session_id: str | None = None
    device_type: str | None = None  # mobile, desktop, vr, tv

    # Content/Product context
    content_id: str | None = None
    product_id: str | None = None
    sku: str | None = None

    # Revenue data
    revenue_cents: int = 0
    currency: str = "USD"
    payment_method: str | None = None  # stripe, apple_pay, google_pay

    # Revenue attribution
    creator_id: str | None = None  # For revenue share
    creator_share_cents: int = 0
    platform_share_cents: int = 0

    # Geographic context
    country_code: str | None = None
    region: str | None = None

    # Quality metrics (for streaming)
    quality_score: int | None = None  # 0-100
    completion_percentage: int | None = None

    # Custom properties
    properties: dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        # Auto-populate event_date from timestamp
        if not self.event_date:
            self.event_date = self.timestamp.strftime("%Y-%m-%d")

    def to_bigquery_row(self) -> dict[str, Any]:
        """Convert to BigQuery row format."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "service": self.service.value,
            "timestamp": self.timestamp.isoformat(),
            "event_date": self.event_date,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "device_type": self.device_type,
            "content_id": self.content_id,
            "product_id": self.product_id,
            "sku": self.sku,
            "revenue_cents": self.revenue_cents,
            "currency": self.currency,
            "payment_method": self.payment_method,
            "creator_id": self.creator_id,
            "creator_share_cents": self.creator_share_cents,
            "platform_share_cents": self.platform_share_cents,
            "country_code": self.country_code,
            "region": self.region,
            "quality_score": self.quality_score,
            "completion_percentage": self.completion_percentage,
            "properties": self.properties,
        }


# Pre-built event factories for common scenarios


def content_view_event(
    user_id: str,
    content_id: str,
    session_id: str,
    device_type: str = "desktop",
    country_code: str = None,
) -> RevenueEvent:
    """Create a content view event."""
    return RevenueEvent(
        event_type=EventType.CONTENT_VIEW,
        service=ServiceType.CINEVERSE,
        user_id=user_id,
        content_id=content_id,
        session_id=session_id,
        device_type=device_type,
        country_code=country_code,
    )


def content_complete_event(
    user_id: str,
    content_id: str,
    session_id: str,
    completion_percentage: int,
    quality_score: int = None,
) -> RevenueEvent:
    """Create a content completion event."""
    return RevenueEvent(
        event_type=EventType.CONTENT_COMPLETE,
        service=ServiceType.CINEVERSE,
        user_id=user_id,
        content_id=content_id,
        session_id=session_id,
        completion_percentage=completion_percentage,
        quality_score=quality_score,
    )


def subscription_event(
    event_type: EventType,
    user_id: str,
    revenue_cents: int,
    tier: str,
    payment_method: str = "stripe",
) -> RevenueEvent:
    """Create a subscription event."""
    return RevenueEvent(
        event_type=event_type,
        service=ServiceType.CINEVERSE,
        user_id=user_id,
        revenue_cents=revenue_cents,
        payment_method=payment_method,
        properties={"tier": tier},
    )


def purchase_event(
    user_id: str,
    product_id: str,
    revenue_cents: int,
    payment_method: str = "stripe",
    sku: str = None,
) -> RevenueEvent:
    """Create a purchase event."""
    return RevenueEvent(
        event_type=EventType.PURCHASE_COMPLETED,
        service=ServiceType.COMMERCE,
        user_id=user_id,
        product_id=product_id,
        revenue_cents=revenue_cents,
        payment_method=payment_method,
        sku=sku,
    )
