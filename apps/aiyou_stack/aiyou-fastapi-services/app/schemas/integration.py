"""Integration schemas"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.integration import IntegrationStatus, IntegrationType


class IntegrationBase(BaseModel):
    """Base integration schema"""

    name: str = Field(..., min_length=1, max_length=255)
    provider: str = Field(..., min_length=1, max_length=100)
    type: IntegrationType
    base_url: str | None = None
    api_version: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IntegrationCreate(IntegrationBase):
    """Integration creation schema"""

    max_retries: int = Field(default=3, ge=0, le=10)
    retry_backoff: int = Field(default=2, ge=1, le=10)
    timeout: int = Field(default=30, ge=1, le=300)


class IntegrationUpdate(BaseModel):
    """Integration update schema"""

    name: str | None = Field(None, min_length=1, max_length=255)
    status: IntegrationStatus | None = None
    config: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    max_retries: int | None = Field(None, ge=0, le=10)
    retry_backoff: int | None = Field(None, ge=1, le=10)
    timeout: int | None = Field(None, ge=1, le=300)


class IntegrationResponse(IntegrationBase):
    """Integration response schema"""

    id: int
    user_id: int
    status: IntegrationStatus
    max_retries: int
    retry_backoff: int
    timeout: int
    last_sync_at: datetime | None
    last_error: str | None
    error_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IntegrationCredentialCreate(BaseModel):
    """Integration credential creation schema"""

    access_token: str | None = None
    refresh_token: str | None = None
    api_key: str | None = None
    api_secret: str | None = None
    token_type: str | None = None
    scope: str | None = None
    expires_at: datetime | None = None
    extra_data: dict[str, Any] = Field(default_factory=dict)


class IntegrationCredentialUpdate(BaseModel):
    """Integration credential update schema"""

    access_token: str | None = None
    refresh_token: str | None = None
    api_key: str | None = None
    api_secret: str | None = None
    expires_at: datetime | None = None
    extra_data: dict[str, Any] | None = None


class IntegrationCredentialResponse(BaseModel):
    """Integration credential response schema (without sensitive data)"""

    id: int
    integration_id: int
    token_type: str | None
    scope: str | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IntegrationTestRequest(BaseModel):
    """Integration test request schema"""

    endpoint: str | None = None
    method: str = "GET"
    headers: dict[str, str] = Field(default_factory=dict)
    body: dict[str, Any] | None = None


class IntegrationTestResponse(BaseModel):
    """Integration test response schema"""

    success: bool
    status_code: int | None = None
    response: dict[str, Any] | None = None
    error: str | None = None
    duration_ms: int


class OAuthCallbackRequest(BaseModel):
    """OAuth callback request schema"""

    code: str
    state: str | None = None


class OAuthInitiateResponse(BaseModel):
    """OAuth initiate response schema"""

    authorization_url: str
    state: str
