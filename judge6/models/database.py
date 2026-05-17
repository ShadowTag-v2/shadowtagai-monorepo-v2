# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Judge #6 Database Models
ATP 5-19 Risk Management API for AI
"""

from sqlalchemy import (
  Column,
  String,
  Integer,
  Float,
  Boolean,
  DateTime,
  ForeignKey,
  Text,
  Enum as SQLEnum,
  JSON,
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone
import enum


Base = declarative_base()


class SubscriptionTier(str, enum.Enum):
  """Pricing tiers"""

  FREE = "free"
  STARTER = "starter"
  PROFESSIONAL = "professional"
  ENTERPRISE = "enterprise"


class RiskLevel(str, enum.Enum):
  """ATP 5-19 Risk Levels"""

  CATASTROPHIC = "catastrophic"
  CRITICAL = "critical"
  MODERATE = "moderate"
  LOW = "low"
  NEGLIGIBLE = "negligible"


class User(Base):
  """Customer accounts"""

  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)
  email = Column(String(255), unique=True, index=True, nullable=False)
  hashed_password = Column(String(255), nullable=False)
  full_name = Column(String(255))
  company = Column(String(255))

  # Subscription
  tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
  stripe_customer_id = Column(String(255), unique=True, index=True)
  stripe_subscription_id = Column(String(255), unique=True, index=True)

  # Limits (denormalized for performance)
  monthly_request_limit = Column(Integer, default=1000)  # Free tier default
  current_month_usage = Column(Integer, default=0)

  # Status
  is_active = Column(Boolean, default=True)
  is_verified = Column(Boolean, default=False)

  # Timestamps
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
  updated_at = Column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc),
  )

  # Relationships
  api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
  policies = relationship("Policy", back_populates="user", cascade="all, delete-orphan")
  audit_logs = relationship(
    "AuditLog", back_populates="user", cascade="all, delete-orphan"
  )


class APIKey(Base):
  """API keys for authentication"""

  __tablename__ = "api_keys"

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
  key_hash = Column(String(255), unique=True, index=True, nullable=False)
  key_prefix = Column(String(10), nullable=False)  # First 8 chars for display
  name = Column(String(255), nullable=False)  # User-friendly name

  # Permissions
  is_active = Column(Boolean, default=True)
  scopes = Column(JSON, default=list)  # Future: ["judge:read", "judge:write"]

  # Usage stats
  last_used_at = Column(DateTime, nullable=True)
  total_requests = Column(Integer, default=0)

  # Timestamps
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
  expires_at = Column(DateTime, nullable=True)  # Optional expiration

  # Relationships
  user = relationship("User", back_populates="api_keys")


class Policy(Base):
  """Custom policies uploaded by users"""

  __tablename__ = "policies"

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

  name = Column(String(255), nullable=False)
  description = Column(Text)

  # ATP 5-19 Structure
  purpose = Column(Text, nullable=False)  # What is the intent?
  reasons = Column(JSON, nullable=False)  # Why is it allowed/denied?
  brakes = Column(JSON, nullable=False)  # What are the hard stops?

  # Policy content (YAML or JSON)
  content = Column(JSON, nullable=False)

  # Status
  is_active = Column(Boolean, default=True)
  version = Column(Integer, default=1)

  # Timestamps
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
  updated_at = Column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc),
  )

  # Relationships
  user = relationship("User", back_populates="policies")


class AuditLog(Base):
  """Audit trail for compliance"""

  __tablename__ = "audit_logs"

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

  # Request metadata
  request_id = Column(String(36), unique=True, index=True, nullable=False)
  api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False)

  # Input
  prompt = Column(Text, nullable=False)
  context = Column(JSON)  # Additional context provided

  # 3-Layer Decisions
  layer1_decision = Column(SQLEnum(RiskLevel))  # Gemini
  layer1_confidence = Column(Float)
  layer1_reasoning = Column(Text)

  layer2_decision = Column(SQLEnum(RiskLevel))  # PyTorch
  layer2_confidence = Column(Float)
  layer2_reasoning = Column(Text)

  layer3_decision = Column(Boolean)  # Rules engine (PASS/FAIL)
  layer3_violated_rules = Column(JSON)  # Which rules triggered

  # Final Decision
  final_risk_level = Column(SQLEnum(RiskLevel), nullable=False)
  final_allowed = Column(Boolean, nullable=False)
  final_reasoning = Column(Text, nullable=False)

  # Performance
  latency_ms = Column(Integer)  # Total processing time
  layer1_latency_ms = Column(Integer)
  layer2_latency_ms = Column(Integer)
  layer3_latency_ms = Column(Integer)

  # Metadata
  ip_address = Column(String(45))
  user_agent = Column(Text)

  # Timestamp
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

  # Relationships
  user = relationship("User", back_populates="audit_logs")


class UsageMetrics(Base):
  """Aggregated usage metrics for billing and analytics"""

  __tablename__ = "usage_metrics"

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

  # Time period
  year = Column(Integer, nullable=False)
  month = Column(Integer, nullable=False)

  # Usage
  total_requests = Column(Integer, default=0)
  allowed_requests = Column(Integer, default=0)
  denied_requests = Column(Integer, default=0)

  # Risk breakdown
  catastrophic_count = Column(Integer, default=0)
  critical_count = Column(Integer, default=0)
  moderate_count = Column(Integer, default=0)
  low_count = Column(Integer, default=0)
  negligible_count = Column(Integer, default=0)

  # Performance
  avg_latency_ms = Column(Float)
  p99_latency_ms = Column(Integer)

  # Billing
  overage_requests = Column(Integer, default=0)  # Requests beyond plan limit
  overage_charge_cents = Column(Integer, default=0)

  # Timestamps
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
  updated_at = Column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc),
  )

  # Unique constraint on user + time period
  __table_args__ = ({"sqlite_autoincrement": True},)


class Webhook(Base):
  """Webhook configurations for policy violations"""

  __tablename__ = "webhooks"

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

  url = Column(String(512), nullable=False)
  secret = Column(String(255))  # HMAC signature secret

  # Triggers
  trigger_on_denial = Column(Boolean, default=True)
  trigger_on_risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.CRITICAL)

  # Status
  is_active = Column(Boolean, default=True)
  last_triggered_at = Column(DateTime)
  total_triggers = Column(Integer, default=0)

  # Timestamps
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

  # Relationships
  user = relationship("User")
