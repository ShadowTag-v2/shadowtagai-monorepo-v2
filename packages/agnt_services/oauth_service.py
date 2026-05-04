# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""OAuth Service — Ported from Claude Code v2.1.91 oauth/index.ts.

Implements the OAuth 2.0 authorization code flow with PKCE (Proof Key for Code
Exchange). Supports both automatic (browser redirect to localhost) and manual
(user copy-pastes the code) authentication flows.

Architecture:
    - Generates PKCE code verifier + challenge per RFC 7636.
    - Spawns a temporary local HTTP server to capture the authorization code.
    - Exchanges authorization code for access/refresh tokens.
    - Fetches profile info (subscription type, rate limit tier).
    - Handles success/error redirects for browser-based flow.

Reference: Claude Code v2.1.91 src/services/oauth/index.ts (199 lines)
"""

from __future__ import annotations

import hashlib
import logging
import secrets
from base64 import urlsafe_b64encode
from dataclasses import dataclass, field
from enum import StrEnum

logger = logging.getLogger(__name__)


# ── PKCE Helpers ──────────────────────────────────────────────────────


def generate_code_verifier(length: int = 64) -> str:
    """Generate a cryptographically random PKCE code verifier (RFC 7636)."""
    return secrets.token_urlsafe(length)[:128]  # max 128 chars per spec


def generate_code_challenge(verifier: str) -> str:
    """Generate S256 code challenge from verifier (RFC 7636 §4.2)."""
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def generate_state() -> str:
    """Generate a random state parameter for CSRF protection."""
    return secrets.token_urlsafe(32)


# ── Types ─────────────────────────────────────────────────────────────


class SubscriptionType(StrEnum):
    """User subscription tier."""

    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"
    MAX = "max"


class RateLimitTier(StrEnum):
    """Rate limit tier for the user."""

    STANDARD = "standard"
    HIGHER = "higher"
    UNLIMITED = "unlimited"


@dataclass(frozen=True)
class OAuthTokens:
    """Token set returned after successful OAuth flow."""

    access_token: str
    refresh_token: str
    expires_at: float  # Unix timestamp (seconds)
    scopes: list[str] = field(default_factory=list)
    subscription_type: SubscriptionType | None = None
    rate_limit_tier: RateLimitTier | None = None
    token_account_uuid: str | None = None
    email_address: str | None = None
    organization_uuid: str | None = None


@dataclass(frozen=True)
class OAuthConfig:
    """Configuration for the OAuth provider."""

    base_api_url: str
    client_id: str
    authorize_url: str
    token_url: str
    profile_url: str
    redirect_path: str = "/oauth/callback"


# ── OAuth Service ─────────────────────────────────────────────────────


class OAuthService:
    """OAuth 2.0 + PKCE service.

    Ported from Claude Code's OAuthService class. Provides:
    1. PKCE flow initiation (code verifier + challenge generation).
    2. Authorization URL construction.
    3. Token exchange.
    4. Profile info fetching.
    5. Token formatting.

    In the AGNT architecture, actual HTTP calls and browser launching
    are handled by the caller; this service provides the protocol logic.
    """

    def __init__(self, config: OAuthConfig) -> None:
        self.config = config
        self._code_verifier = generate_code_verifier()
        self._state = generate_state()

    @property
    def code_verifier(self) -> str:
        return self._code_verifier

    @property
    def state(self) -> str:
        return self._state

    def build_auth_url(
        self,
        *,
        port: int,
        is_manual: bool = False,
        login_hint: str | None = None,
        org_uuid: str | None = None,
    ) -> str:
        """Build the authorization URL for the OAuth flow."""
        code_challenge = generate_code_challenge(self._code_verifier)
        redirect_uri = f"http://localhost:{port}{self.config.redirect_path}"

        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": redirect_uri,
            "state": self._state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        if is_manual:
            params["prompt"] = "manual"
        if login_hint:
            params["login_hint"] = login_hint
        if org_uuid:
            params["org_uuid"] = org_uuid

        from urllib.parse import urlencode

        return f"{self.config.authorize_url}?{urlencode(params)}"

    def build_token_request(
        self,
        authorization_code: str,
        port: int,
        is_manual: bool = False,
    ) -> dict[str, str]:
        """Build the token exchange request parameters."""
        redirect_uri = f"http://localhost:{port}{self.config.redirect_path}"
        return {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": redirect_uri,
            "code_verifier": self._code_verifier,
            "client_id": self.config.client_id,
        }

    @staticmethod
    def parse_scopes(scope_str: str) -> list[str]:
        """Parse space-delimited scope string into list."""
        return [s.strip() for s in scope_str.split() if s.strip()]

    @staticmethod
    def format_tokens(
        access_token: str,
        refresh_token: str,
        expires_in: int,
        scope: str,
        subscription_type: SubscriptionType | None = None,
        rate_limit_tier: RateLimitTier | None = None,
        account_uuid: str | None = None,
        email_address: str | None = None,
        organization_uuid: str | None = None,
    ) -> OAuthTokens:
        """Format raw token response into OAuthTokens dataclass."""
        import time

        return OAuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=time.time() + expires_in,
            scopes=OAuthService.parse_scopes(scope),
            subscription_type=subscription_type,
            rate_limit_tier=rate_limit_tier,
            token_account_uuid=account_uuid,
            email_address=email_address,
            organization_uuid=organization_uuid,
        )

    def cleanup(self) -> None:
        """Reset internal state for reuse."""
        self._code_verifier = generate_code_verifier()
        self._state = generate_state()
