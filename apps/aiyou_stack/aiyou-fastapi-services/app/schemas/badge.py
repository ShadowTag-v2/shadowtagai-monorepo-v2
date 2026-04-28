# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Badge schemas for API validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BadgeResponse(BaseModel):
    """Badge response schema."""

    id: int
    name: str
    slug: str
    description: str
    category: str
    tier: str
    icon_url: str | None = None
    is_secret: bool
    total_awarded: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBadgeResponse(BaseModel):
    """User badge response schema."""

    id: int
    user_id: int
    badge_id: int
    awarded_at: datetime
    is_featured: bool
    badge: BadgeResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class BadgeListResponse(BaseModel):
    """Badge list response."""

    items: list[BadgeResponse]
    total: int
