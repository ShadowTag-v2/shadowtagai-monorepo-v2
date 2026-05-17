# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Pydantic schemas for Release Manager API.
"""

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field, field_validator
import semver

from app.models.release import DeploymentStatus, DeploymentStrategy, FeatureFlagStatus


# ==================== Release Schemas ====================


class ReleaseBase(BaseModel):
  """Base schema for release."""

  version: str = Field(..., description="Semantic version (e.g., 1.0.0)")
  name: str = Field(..., description="Release name")
  description: str | None = Field(None, description="Release description")
  changelog: str | None = Field(None, description="Release changelog")
  commit_hash: str | None = Field(None, description="Git commit hash")
  branch: str | None = Field(None, description="Git branch")
  tag: str | None = Field(None, description="Git tag")

  @field_validator("version")
  @classmethod
  def validate_version(cls, v: str) -> str:
    """Validate semantic versioning."""
    try:
      semver.VersionInfo.parse(v)
    except ValueError:
      raise ValueError(f"Invalid semantic version: {v}")
    return v


class ReleaseCreate(ReleaseBase):
  """Schema for creating a release."""

  created_by: str | None = None


class ReleaseUpdate(BaseModel):
  """Schema for updating a release."""

  name: str | None = None
  description: str | None = None
  changelog: str | None = None
  is_stable: bool | None = None


class ReleaseResponse(ReleaseBase):
  """Schema for release response."""

  id: int
  created_at: datetime
  released_at: datetime | None = None
  is_active: bool
  is_stable: bool
  created_by: str | None = None

  model_config = {"from_attributes": True}


# ==================== Deployment Schemas ====================


class DeploymentBase(BaseModel):
  """Base schema for deployment."""

  environment: str = Field(
    ..., description="Deployment environment (e.g., staging, production)"
  )
  strategy: DeploymentStrategy = Field(
    DeploymentStrategy.BLUE_GREEN, description="Deployment strategy"
  )
  configuration: dict[str, Any] | None = Field(
    None, description="Deployment configuration"
  )


class DeploymentCreate(DeploymentBase):
  """Schema for creating a deployment."""

  release_id: int = Field(..., description="Release ID to deploy")
  deployed_by: str | None = None


class DeploymentUpdate(BaseModel):
  """Schema for updating a deployment."""

  status: DeploymentStatus | None = None
  health_check_passed: bool | None = None
  logs: str | None = None
  error_message: str | None = None


class DeploymentResponse(DeploymentBase):
  """Schema for deployment response."""

  id: int
  release_id: int
  status: DeploymentStatus
  started_at: datetime | None = None
  completed_at: datetime | None = None
  deployed_by: str | None = None
  health_check_passed: bool
  rollback_deployment_id: int | None = None
  logs: str | None = None
  error_message: str | None = None
  release: ReleaseResponse | None = None

  model_config = {"from_attributes": True}


# ==================== Feature Flag Schemas ====================


class FeatureFlagBase(BaseModel):
  """Base schema for feature flag."""

  name: str = Field(..., description="Feature flag name")
  key: str = Field(..., description="Feature flag key (unique identifier)")
  description: str | None = Field(None, description="Feature flag description")
  status: FeatureFlagStatus = Field(
    FeatureFlagStatus.DISABLED, description="Feature flag status"
  )
  enabled: bool = Field(False, description="Whether feature is enabled")
  percentage: int = Field(0, ge=0, le=100, description="Percentage rollout (0-100)")
  targeting_rules: dict[str, Any] | None = Field(None, description="Targeting rules")
  environment: str | None = Field(None, description="Environment")
  release_id: int | None = Field(None, description="Associated release ID")

  @field_validator("key")
  @classmethod
  def validate_key(cls, v: str) -> str:
    """Validate feature flag key format."""
    if not v.replace("_", "").replace("-", "").isalnum():
      raise ValueError(
        "Key must contain only alphanumeric characters, hyphens, and underscores"
      )
    return v.lower()


class FeatureFlagCreate(FeatureFlagBase):
  """Schema for creating a feature flag."""

  created_by: str | None = None


class FeatureFlagUpdate(BaseModel):
  """Schema for updating a feature flag."""

  name: str | None = None
  description: str | None = None
  status: FeatureFlagStatus | None = None
  enabled: bool | None = None
  percentage: int | None = Field(None, ge=0, le=100)
  targeting_rules: dict[str, Any] | None = None
  environment: str | None = None
  release_id: int | None = None


class FeatureFlagResponse(FeatureFlagBase):
  """Schema for feature flag response."""

  id: int
  created_at: datetime
  updated_at: datetime
  created_by: str | None = None

  model_config = {"from_attributes": True}


class FeatureFlagEvaluation(BaseModel):
  """Schema for feature flag evaluation."""

  key: str
  enabled: bool
  percentage: int
  metadata: dict[str, Any] | None = None


# ==================== Rollback Schemas ====================


class RollbackRequest(BaseModel):
  """Schema for rollback request."""

  deployment_id: int = Field(..., description="Deployment ID to rollback")
  reason: str | None = Field(None, description="Rollback reason")
  force: bool = Field(False, description="Force rollback even if health checks fail")


class RollbackResponse(BaseModel):
  """Schema for rollback response."""

  success: bool
  rollback_deployment_id: int | None = None
  message: str
  previous_deployment: DeploymentResponse | None = None
  new_deployment: DeploymentResponse | None = None


# ==================== Health Check Schemas ====================


class HealthCheckResult(BaseModel):
  """Schema for health check result."""

  healthy: bool
  checks: dict[str, bool]
  message: str | None = None
  timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==================== Metrics Schemas ====================


class DeploymentMetricsResponse(BaseModel):
  """Schema for deployment metrics response."""

  id: int
  deployment_id: int
  deployment_duration: int | None = None
  health_check_duration: int | None = None
  cpu_usage: dict[str, Any] | None = None
  memory_usage: dict[str, Any] | None = None
  error_rate: dict[str, Any] | None = None
  requests_per_second: dict[str, Any] | None = None
  response_times: dict[str, Any] | None = None
  recorded_at: datetime

  model_config = {"from_attributes": True}


# ==================== List Responses ====================


class ReleaseListResponse(BaseModel):
  """Schema for paginated release list."""

  total: int
  items: list[ReleaseResponse]
  page: int
  page_size: int


class DeploymentListResponse(BaseModel):
  """Schema for paginated deployment list."""

  total: int
  items: list[DeploymentResponse]
  page: int
  page_size: int


class FeatureFlagListResponse(BaseModel):
  """Schema for paginated feature flag list."""

  total: int
  items: list[FeatureFlagResponse]
  page: int
  page_size: int
