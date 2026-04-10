"""
FinJudge API Key Management System
Handles key generation, validation, and rate limiting for freemium model
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from enum import Enum, StrEnum

from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class TierLevel(StrEnum):
    """Subscription tiers"""

    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class APIKey(Base):
    """API key model with usage tracking"""

    __tablename__ = "api_keys"

    id = Column(String(64), primary_key=True)  # Hashed key
    key_prefix = Column(String(16), nullable=False, index=True)  # fj_xxx for display
    email = Column(String(255), nullable=False, index=True)
    organization = Column(String(255), nullable=True)

    tier = Column(SQLEnum(TierLevel), nullable=False, default=TierLevel.FREE)

    # Rate limiting
    monthly_limit = Column(Integer, nullable=False, default=1000)
    current_month_usage = Column(Integer, nullable=False, default=0)
    usage_reset_date = Column(DateTime, nullable=False)

    # Key management
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Billing
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)


class UsageRecord(Base):
    """Detailed usage tracking for analytics"""

    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key_id = Column(String(64), nullable=False, index=True)

    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    endpoint = Column(String(100), nullable=False)

    # Request details
    decision_id = Column(String(100), nullable=True)
    risk_level = Column(String(20), nullable=True)
    disposition = Column(String(20), nullable=True)

    # Performance
    latency_ms = Column(Integer, nullable=True)

    # Billing
    billable = Column(Boolean, nullable=False, default=True)


class APIKeyManager:
    """API key generation and validation"""

    # Tier configurations
    TIER_CONFIGS = {
        TierLevel.FREE: {
            "monthly_limit": 1000,
            "price": 0,
            "features": ["basic_judge", "audit_trail", "email_support"],
        },
        TierLevel.PRO: {
            "monthly_limit": 10000,
            "price": 99,
            "features": ["basic_judge", "audit_trail", "priority_support", "analytics_dashboard"],
        },
        TierLevel.BUSINESS: {
            "monthly_limit": 100000,
            "price": 499,
            "features": ["all_pro", "custom_risk_frameworks", "sla_99_9", "dedicated_support"],
        },
        TierLevel.ENTERPRISE: {
            "monthly_limit": None,  # Unlimited
            "price": 2499,
            "features": ["all_business", "on_prem_option", "custom_integrations", "csm"],
        },
    }

    def __init__(self, db_url: str = "postgresql://REDACTED_USER:REDACTED_PASS@staticmethod
    def _hash_key(plaintext_key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(plaintext_key.encode()).hexdigest()

    @staticmethod
    def _next_month_start() -> datetime:
        """Calculate next month's start date for usage reset"""
        now = datetime.utcnow()
        if now.month == 12:
            return datetime(now.year + 1, 1, 1)
        else:
            return datetime(now.year, now.month + 1, 1)


# ============================================================================
# FastAPI Middleware for API Key Authentication
# ============================================================================

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class APIKeyAuth(HTTPBearer):
    """FastAPI dependency for API key authentication"""

    def __init__(self, key_manager: APIKeyManager):
        super().__init__()
        self.key_manager = key_manager

    async def __call__(self, request: Request) -> APIKey:
        """Validate API key from request"""
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

        plaintext_key = credentials.credentials

        is_valid, api_key, error = self.key_manager.validate_key(plaintext_key)

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED
                if not api_key
                else status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error or "Invalid API key",
            )

        # Attach API key to request state
        request.state.api_key = api_key

        return api_key
