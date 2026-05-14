# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class HubSpotContact(BaseModel):
    """Structured contact content for HubSpot."""

    token: str = Field(description="Verification token that MUST appear in at least one property (e.g., email).")
    email: EmailStr
    firstname: str
    lastname: str
    phone: str | None = None
    company: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    notes: str | None = None  # not posted to HubSpot; useful context
