"""Multi-Tenant Database Models with Row-Level Security
"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
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


class LicenseTier(StrEnum):
    STARTER = "starter"  # $50K/year
    GROWTH = "growth"  # $250K/year
    ENTERPRISE = "enterprise"  # $500K/year
    UNLIMITED = "unlimited"  # $1M/year


class TenantStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CHURNED = "churned"


# SQLAlchemy ORM Models
class Tenant(Base):
    """Multi-tenant organization"""

    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)

    # License
    license_tier = Column(SQLEnum(LicenseTier), default=LicenseTier.STARTER)
    license_expires_at = Column(DateTime)
    annual_fee_cents = Column(Integer)  # Store in cents for precision

    # Status
    status = Column(SQLEnum(TenantStatus), default=TenantStatus.TRIAL)

    # Configuration (auto-configured by AI)
    industry = Column(String(100))
    company_size = Column(String(50))  # startup, smb, enterprise, mega
    tech_stack = Column(JSON)  # ["python", "kubernetes", "react", ...]
    regulatory_requirements = Column(JSON)  # ["HIPAA", "SOC2", "GDPR", ...]

    # AI Configuration Profile
    ai_config = Column(JSON)  # Auto-generated config based on profile

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="tenant")
    workspaces = relationship("Workspace", back_populates="tenant")
    intel_feeds = relationship("IntelFeed", back_populates="tenant")


class User(Base):
    """Tenant users with SSO support"""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)

    email = Column(String(255), nullable=False)
    name = Column(String(255))

    # Auth
    auth_provider = Column(String(50))  # oauth, saml, local
    external_id = Column(String(255))  # SSO provider ID

    # Role
    role = Column(String(50), default="member")  # admin, member, viewer

    # Status
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")


class Workspace(Base):
    """Isolated workspaces within a tenant"""

    __tablename__ = "workspaces"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Configuration
    config = Column(JSON)  # Workspace-specific AI config

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="workspaces")


class IntelFeed(Base):
    """Intel updates from Nightly Pipeline for tenant"""

    __tablename__ = "intel_feeds"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)

    # Intel metadata
    feed_type = Column(String(50))  # tech_update, framework_release, security_alert, market_trend
    source = Column(String(255))
    title = Column(String(500))
    summary = Column(Text)

    # AI-generated recommendations
    recommendations = Column(JSON)  # Actions based on tenant profile
    relevance_score = Column(Integer)  # 0-100 relevance to tenant

    # ShadowTag watermark
    shadowtag_signature = Column(String(512))

    # Status
    is_read = Column(Boolean, default=False)
    is_actioned = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="intel_feeds")


# Pydantic Models for API
class TenantCreate(BaseModel):
    name: str
    slug: str
    industry: str | None = None
    company_size: str | None = None
    tech_stack: list[str] | None = None
    regulatory_requirements: list[str] | None = None


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    license_tier: LicenseTier
    status: TenantStatus
    industry: str | None
    company_size: str | None
    tech_stack: list[str] | None
    ai_config: dict[str, Any] | None
    created_at: datetime

    class Config:
        from_attributes = True


class LicenseTierLimits(BaseModel):
    """License tier feature matrix"""

    tier: LicenseTier
    annual_fee_usd: int
    max_workspaces: int
    max_users: int
    intel_refresh_hours: int
    api_rate_limit: int
    dedicated_support: bool
    custom_integrations: bool
    sla_uptime: float


# License tier configuration
LICENSE_TIERS: dict[LicenseTier, LicenseTierLimits] = {
    LicenseTier.STARTER: LicenseTierLimits(
        tier=LicenseTier.STARTER,
        annual_fee_usd=50000,
        max_workspaces=1,
        max_users=5,
        intel_refresh_hours=24,
        api_rate_limit=100,
        dedicated_support=False,
        custom_integrations=False,
        sla_uptime=99.5,
    ),
    LicenseTier.GROWTH: LicenseTierLimits(
        tier=LicenseTier.GROWTH,
        annual_fee_usd=250000,
        max_workspaces=5,
        max_users=25,
        intel_refresh_hours=12,
        api_rate_limit=500,
        dedicated_support=False,
        custom_integrations=True,
        sla_uptime=99.9,
    ),
    LicenseTier.ENTERPRISE: LicenseTierLimits(
        tier=LicenseTier.ENTERPRISE,
        annual_fee_usd=500000,
        max_workspaces=-1,  # unlimited
        max_users=100,
        intel_refresh_hours=6,
        api_rate_limit=2000,
        dedicated_support=True,
        custom_integrations=True,
        sla_uptime=99.95,
    ),
    LicenseTier.UNLIMITED: LicenseTierLimits(
        tier=LicenseTier.UNLIMITED,
        annual_fee_usd=1000000,
        max_workspaces=-1,  # unlimited
        max_users=-1,  # unlimited
        intel_refresh_hours=1,
        api_rate_limit=-1,  # unlimited
        dedicated_support=True,
        custom_integrations=True,
        sla_uptime=99.99,
    ),
}
