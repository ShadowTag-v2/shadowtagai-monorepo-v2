# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Database models for Release Manager.
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, JSON, Index
from sqlalchemy.orm import relationship

from app.database.session import Base


class DeploymentStatus(str, PyEnum):
    """Deployment status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    ROLLING_BACK = "rolling_back"


class DeploymentStrategy(str, PyEnum):
    """Deployment strategy enumeration."""

    BLUE_GREEN = "blue_green"
    ROLLING = "rolling"
    CANARY = "canary"
    RECREATE = "recreate"


class FeatureFlagStatus(str, PyEnum):
    """Feature flag status enumeration."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    PERCENTAGE = "percentage"


class Release(Base):
    """Release model for version management."""

    __tablename__ = "releases"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    changelog = Column(Text, nullable=True)

    # Git information
    commit_hash = Column(String(40), nullable=True)
    branch = Column(String(255), nullable=True)
    tag = Column(String(255), nullable=True)

    # Release metadata
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    released_at = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=False)
    is_stable = Column(Boolean, default=False)

    # Relationships
    deployments = relationship("Deployment", back_populates="release", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_release_version", "version"),
        Index("idx_release_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Release(version={self.version}, name={self.name})>"


class Deployment(Base):
    """Deployment model for tracking deployments."""

    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    release_id = Column(Integer, ForeignKey("releases.id"), nullable=False)

    # Deployment information
    environment = Column(String(50), nullable=False, index=True)
    strategy = Column(Enum(DeploymentStrategy), nullable=False)
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.PENDING, nullable=False)

    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Deployment metadata
    deployed_by = Column(String(255), nullable=True)
    configuration = Column(JSON, nullable=True)

    # Health and rollback
    health_check_passed = Column(Boolean, default=False)
    rollback_deployment_id = Column(Integer, ForeignKey("deployments.id"), nullable=True)

    # Logs and errors
    logs = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    release = relationship("Release", back_populates="deployments")
    rollback_deployment = relationship("Deployment", remote_side=[id], foreign_keys=[rollback_deployment_id])

    __table_args__ = (
        Index("idx_deployment_release", "release_id"),
        Index("idx_deployment_environment", "environment"),
        Index("idx_deployment_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Deployment(id={self.id}, release_id={self.release_id}, status={self.status})>"


class FeatureFlag(Base):
    """Feature flag model for feature toggle management."""

    __tablename__ = "feature_flags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Status
    status = Column(Enum(FeatureFlagStatus), default=FeatureFlagStatus.DISABLED, nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)

    # Percentage rollout
    percentage = Column(Integer, default=0)  # 0-100

    # Targeting
    targeting_rules = Column(JSON, nullable=True)  # User segments, conditions, etc.

    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(String(255), nullable=True)

    # Environment specific
    environment = Column(String(50), nullable=True)

    # Associated release (optional)
    release_id = Column(Integer, ForeignKey("releases.id"), nullable=True)
    release = relationship("Release")

    __table_args__ = (
        Index("idx_feature_flag_key", "key"),
        Index("idx_feature_flag_status", "status"),
        Index("idx_feature_flag_enabled", "enabled"),
    )

    def __repr__(self) -> str:
        return f"<FeatureFlag(key={self.key}, status={self.status})>"


class DeploymentMetrics(Base):
    """Deployment metrics for monitoring and analytics."""

    __tablename__ = "deployment_metrics"

    id = Column(Integer, primary_key=True, index=True)
    deployment_id = Column(Integer, ForeignKey("deployments.id"), nullable=False)

    # Timing metrics
    deployment_duration = Column(Integer, nullable=True)  # seconds
    health_check_duration = Column(Integer, nullable=True)  # seconds

    # Performance metrics
    cpu_usage = Column(JSON, nullable=True)
    memory_usage = Column(JSON, nullable=True)
    error_rate = Column(JSON, nullable=True)

    # Traffic metrics
    requests_per_second = Column(JSON, nullable=True)
    response_times = Column(JSON, nullable=True)

    # Timestamp
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    deployment = relationship("Deployment")

    __table_args__ = (
        Index("idx_metrics_deployment", "deployment_id"),
        Index("idx_metrics_recorded_at", "recorded_at"),
    )

    def __repr__(self) -> str:
        return f"<DeploymentMetrics(deployment_id={self.deployment_id})>"
