# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Webhook schemas"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.webhook import WebhookEventStatus, WebhookStatus


class WebhookBase(BaseModel):
    """Base webhook schema"""

    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., min_length=1, max_length=500)
    events: list[str] = Field(default_factory=list)
    headers: dict[str, str] = Field(default_factory=dict)


class WebhookCreate(WebhookBase):
    """Webhook creation schema"""

    integration_id: int | None = None
    secret: str | None = None
    max_retries: int = Field(default=5, ge=0, le=10)
    retry_delay: int = Field(default=5, ge=1, le=300)
    timeout: int = Field(default=30, ge=1, le=300)


class WebhookUpdate(BaseModel):
    """Webhook update schema"""

    name: str | None = Field(None, min_length=1, max_length=255)
    url: str | None = Field(None, min_length=1, max_length=500)
    status: WebhookStatus | None = None
    events: list[str] | None = None
    headers: dict[str, str] | None = None
    max_retries: int | None = Field(None, ge=0, le=10)
    retry_delay: int | None = Field(None, ge=1, le=300)
    timeout: int | None = Field(None, ge=1, le=300)


class WebhookResponse(WebhookBase):
    """Webhook response schema"""

    id: int
    user_id: int
    integration_id: int | None
    status: WebhookStatus
    max_retries: int
    retry_delay: int
    timeout: int
    is_verified: bool
    total_events: int
    failed_events: int
    last_triggered_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WebhookEventCreate(BaseModel):
    """Webhook event creation schema"""

    event_type: str = Field(..., min_length=1, max_length=100)
    payload: dict[str, Any]


class WebhookEventResponse(BaseModel):
    """Webhook event response schema"""

    id: int
    webhook_id: int
    event_type: str
    payload: dict[str, Any]
    status: WebhookEventStatus
    retry_count: int
    next_retry_at: datetime | None
    last_error: str | None
    created_at: datetime
    processed_at: datetime | None

    model_config = {"from_attributes": True}


class WebhookDeliveryResponse(BaseModel):
    """Webhook delivery response schema"""

    id: int
    event_id: int
    request_headers: dict[str, Any]
    request_body: dict[str, Any]
    response_status: int | None
    response_headers: dict[str, Any]
    response_body: str | None
    duration_ms: int | None
    success: bool
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class WebhookTestRequest(BaseModel):
    """Webhook test request schema"""

    payload: dict[str, Any] = Field(default_factory=dict)


class WebhookTestResponse(BaseModel):
    """Webhook test response schema"""

    success: bool
    status_code: int | None = None
    response: str | None = None
    error: str | None = None
    duration_ms: int
