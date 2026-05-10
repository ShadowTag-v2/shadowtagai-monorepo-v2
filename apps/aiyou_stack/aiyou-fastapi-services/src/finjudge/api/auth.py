# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""FinJudge API auth — authentication helpers for FinJudge endpoints."""

from __future__ import annotations

import enum
import hashlib
import secrets
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

_Base = declarative_base()


class TierLevel(enum.StrEnum):
    """Subscription tier levels."""

    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class _APIKeyRow(_Base):
    """Internal ORM model for API keys."""

    __tablename__ = "finjudge_api_keys"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, nullable=False)
    organization = Column(String, nullable=True, default="")
    key_hash = Column(String, nullable=False, unique=True)
    tier = Column(String, nullable=False, default=TierLevel.FREE.value)
    monthly_limit = Column(Integer, nullable=True, default=1000)
    current_month_usage = Column(Integer, nullable=False, default=0)
    total_usage = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))


class _APIKeyDTO:
    """Data-transfer object returned by generate_key / validate_key."""

    def __init__(self, row: _APIKeyRow) -> None:
        self.id = row.id
        self.email = row.email
        self.organization = row.organization
        self.tier = TierLevel(row.tier)
        self.monthly_limit = row.monthly_limit
        self.current_month_usage = row.current_month_usage
        self.is_active = row.is_active
        self.stripe_customer_id = row.stripe_customer_id


class APIKeyManager:
    """Manages FinJudge API key lifecycle."""

    TIER_CONFIGS: dict[TierLevel, dict[str, Any]] = {
        TierLevel.FREE: {
            "monthly_limit": 1000,
            "price": 0,
            "features": ["basic_judge"],
        },
        TierLevel.PRO: {
            "monthly_limit": 10000,
            "price": 99,
            "features": ["basic_judge", "analytics_dashboard", "priority_support"],
        },
        TierLevel.ENTERPRISE: {
            "monthly_limit": None,
            "price": 2499,
            "features": [
                "basic_judge",
                "analytics_dashboard",
                "priority_support",
                "custom_models",
                "sla",
            ],
        },
    }

    def __init__(self, db_url: str = "sqlite:///:memory:") -> None:
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
        _Base.metadata.create_all(engine)
        self._Session = sessionmaker(bind=engine)

    # -- helpers -------------------------------------------------------

    @staticmethod
    def _hash_key(plaintext: str) -> str:
        return hashlib.sha256(plaintext.encode()).hexdigest()

    # -- public API ----------------------------------------------------

    def generate_key(
        self,
        email: str,
        organization: str = "",
        tier: TierLevel = TierLevel.FREE,
    ) -> tuple[str, _APIKeyDTO]:
        """Generate a new API key and persist it."""
        plaintext = f"fj_{secrets.token_urlsafe(24)}"
        cfg = self.TIER_CONFIGS[tier]
        row = _APIKeyRow(
            email=email,
            organization=organization,
            key_hash=self._hash_key(plaintext),
            tier=tier.value,
            monthly_limit=cfg["monthly_limit"],
        )
        with self._Session() as session:
            session.add(row)
            session.commit()
            session.refresh(row)
            return plaintext, _APIKeyDTO(row)

    def validate_key(self, plaintext: str) -> tuple[bool, _APIKeyDTO | None, str | None]:
        """Validate a plaintext API key."""
        if not plaintext.startswith("fj_"):
            return False, None, "Invalid key format"
        key_hash = self._hash_key(plaintext)
        with self._Session() as session:
            row = session.query(_APIKeyRow).filter(_APIKeyRow.key_hash == key_hash).first()
            if row is None:
                return False, None, "API key not found"
            if not row.is_active:
                return False, None, "API key is disabled"
            if row.monthly_limit is not None and row.current_month_usage >= row.monthly_limit:
                return False, None, "Monthly limit exceeded"
            return True, _APIKeyDTO(row), None

    def record_usage(
        self,
        api_key_id: str,
        endpoint: str = "",
        decision_id: str = "",
        risk_level: str = "",
        disposition: str = "",
    ) -> None:
        """Increment usage counters for a key."""
        with self._Session() as session:
            row = session.query(_APIKeyRow).get(api_key_id)
            if row:
                row.current_month_usage += 1
                row.total_usage += 1
                session.commit()

    def get_usage_stats(self, api_key_id: str) -> dict[str, Any]:
        """Return usage statistics for a key."""
        with self._Session() as session:
            row = session.query(_APIKeyRow).get(api_key_id)
            if row is None:
                return {}
            remaining = (
                (row.monthly_limit - row.current_month_usage)
                if row.monthly_limit is not None
                else None
            )
            return {
                "tier": row.tier,
                "current_month_usage": row.current_month_usage,
                "monthly_limit": row.monthly_limit,
                "remaining": remaining,
                "total_usage": row.total_usage,
            }

    def upgrade_tier(
        self,
        api_key_id: str,
        new_tier: TierLevel,
        stripe_customer_id: str = "",
        stripe_subscription_id: str = "",
    ) -> bool:
        """Upgrade a key's tier."""
        cfg = self.TIER_CONFIGS[new_tier]
        with self._Session() as session:
            row = session.query(_APIKeyRow).get(api_key_id)
            if row is None:
                return False
            row.tier = new_tier.value
            row.monthly_limit = cfg["monthly_limit"]
            row.stripe_customer_id = stripe_customer_id
            row.stripe_subscription_id = stripe_subscription_id
            session.commit()
            return True


# -- FastAPI dependency helpers ----------------------------------------


async def verify_api_key(api_key: str) -> bool:
    """Verify an API key for FinJudge access.

    Args:
        api_key: The API key to verify.

    Returns:
        True if valid.

    """
    # Placeholder — real implementation delegates to Firebase Auth or
    # GCP Secret Manager validation.
    return bool(api_key and len(api_key) >= 16)


async def get_current_user(token: str) -> dict[str, Any]:
    """Extract user from bearer token.

    Args:
        token: JWT bearer token.

    Returns:
        User claims dict.

    """
    return {"sub": "anonymous", "tier": "free"}


__all__ = [
    "APIKeyManager",
    "TierLevel",
    "get_current_user",
    "verify_api_key",
]
