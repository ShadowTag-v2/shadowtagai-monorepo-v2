# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Authentication Service
Handles user registration, login, API key management
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..models.database import User, APIKey, SubscriptionTier
from ..core.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication and authorization service"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storage"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        """
        Create JWT access token
        Used for dashboard authentication
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> dict | None:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    def generate_api_key() -> tuple[str, str, str]:
        """
        Generate a new API key
        Returns: (full_key, key_hash, key_prefix)

        Format: judge6_sk_<random_32_chars>
        """
        # Generate random key
        random_bytes = secrets.token_urlsafe(settings.API_KEY_LENGTH)
        full_key = f"judge6_sk_{random_bytes}"

        # Hash for storage (don't store plaintext)
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()

        # Prefix for display (first 12 chars)
        key_prefix = full_key[:12]

        return full_key, key_hash, key_prefix

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key for lookup"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    async def verify_api_key(api_key: str, db: Session) -> User | None:
        """
        Verify API key and return associated user
        Also updates last_used_at timestamp
        """
        if not api_key or not api_key.startswith("judge6_sk_"):
            return None

        key_hash = AuthService.hash_api_key(api_key)

        # Look up API key
        api_key_obj = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()

        if not api_key_obj:
            return None

        # Check if active
        if not api_key_obj.is_active:
            return None

        # Check expiration
        if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
            return None

        # Update last used
        api_key_obj.last_used_at = datetime.utcnow()
        api_key_obj.total_requests += 1
        db.commit()

        # Get user
        user = db.query(User).filter(User.id == api_key_obj.user_id).first()

        if not user or not user.is_active:
            return None

        return user

    @staticmethod
    def create_user(
        email: str,
        password: str,
        full_name: str | None = None,
        company: str | None = None,
        tier: SubscriptionTier = SubscriptionTier.FREE,
        db: Session = None,
    ) -> User:
        """Create a new user"""
        hashed_password = AuthService.hash_password(password)

        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            company=company,
            tier=tier,
            monthly_request_limit=settings.RATE_LIMIT_FREE,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def create_api_key_for_user(user_id: int, name: str, db: Session) -> tuple[APIKey, str]:
        """
        Create a new API key for a user
        Returns: (APIKey object, plaintext_key)

        IMPORTANT: plaintext_key is only returned once!
        """
        full_key, key_hash, key_prefix = AuthService.generate_api_key()

        api_key_obj = APIKey(
            user_id=user_id,
            key_hash=key_hash,
            key_prefix=key_prefix,
            name=name,
        )

        db.add(api_key_obj)
        db.commit()
        db.refresh(api_key_obj)

        return api_key_obj, full_key

    @staticmethod
    def authenticate_user(email: str, password: str, db: Session) -> User | None:
        """Authenticate user by email and password"""
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return None

        if not AuthService.verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    def get_rate_limit_for_tier(tier: SubscriptionTier) -> int:
        """Get monthly rate limit for a tier"""
        limits = {
            SubscriptionTier.FREE: settings.RATE_LIMIT_FREE,
            SubscriptionTier.STARTER: settings.RATE_LIMIT_STARTER,
            SubscriptionTier.PROFESSIONAL: settings.RATE_LIMIT_PROFESSIONAL,
            SubscriptionTier.ENTERPRISE: settings.RATE_LIMIT_ENTERPRISE,
        }
        return limits.get(tier, settings.RATE_LIMIT_FREE)
