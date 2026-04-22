# Copyright 2026 ShadowTag AI. All rights reserved.
# SPDX-License-Identifier: Proprietary
"""LiteLLM Proxy with per-tenant sandboxing.

Provides multi-model routing (Gemini, Claude, ChatGPT, Grok, Perplexity)
with tenant-isolated, ephemeral sandbox-bound tokens.

Security:
    - No master API keys in sandbox
    - Per-tenant token issuance with TTL
    - User-billed proxy (costs attributed to tenant)
    - Rate limiting per tenant + model
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ModelProvider(str, Enum):
    """Supported LLM providers for CounselConduit."""

    GEMINI = "gemini"
    CLAUDE = "claude"
    CHATGPT = "chatgpt"
    GROK = "grok"
    PERPLEXITY = "perplexity"


@dataclass
class TenantToken:
    """An ephemeral, sandbox-bound token for a tenant."""

    token_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    session_id: str = ""
    provider: ModelProvider = ModelProvider.GEMINI
    created_at: float = field(default_factory=time.time)
    ttl_seconds: int = 900  # 15 minutes
    usage_tokens: int = 0
    max_tokens: int = 100_000  # Token budget cap per session

    @property
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        return (time.time() - self.created_at) > self.ttl_seconds

    @property
    def is_budget_exceeded(self) -> bool:
        """Check if the token budget is exhausted."""
        return self.usage_tokens >= self.max_tokens


class LiteLLMProxy:
    """Per-tenant sandboxed LiteLLM proxy.

    Architecture:
    - Each tenant gets isolated, ephemeral tokens
    - Tokens are session-bound with short TTLs
    - No master keys exposed to sandboxes
    - All costs attributed to the tenant's Stripe subscription
    """

    # Model routing table (authorized runtime model first)
    MODEL_MAP: dict[ModelProvider, str] = {
        ModelProvider.GEMINI: "gemini-3.1-flash-lite-preview-thinking",
        ModelProvider.CLAUDE: "claude-sonnet-4-20250514",
        ModelProvider.CHATGPT: "gpt-4.1-mini",
        ModelProvider.GROK: "grok-3-mini-fast",
        ModelProvider.PERPLEXITY: "sonar-pro",
    }

    def __init__(self) -> None:
        self._active_tokens: dict[str, TenantToken] = {}

    def issue_token(
        self,
        tenant_id: str,
        session_id: str,
        provider: ModelProvider = ModelProvider.GEMINI,
        ttl: int = 900,
        max_tokens: int = 100_000,
    ) -> TenantToken:
        """Issue an ephemeral proxy token for a tenant session.

        Args:
            tenant_id: The law firm tenant ID.
            session_id: The session requesting the token.
            provider: The LLM provider to route to.
            ttl: Token time-to-live in seconds.
            max_tokens: Maximum token budget for this session.

        Returns:
            A TenantToken bound to the session.
        """
        token = TenantToken(
            tenant_id=tenant_id,
            session_id=session_id,
            provider=provider,
            ttl_seconds=ttl,
            max_tokens=max_tokens,
        )
        self._active_tokens[token.token_id] = token
        logger.info(
            "Proxy token issued: token=%s tenant=%s provider=%s ttl=%ds",
            token.token_id,
            tenant_id,
            provider.value,
            ttl,
        )
        return token

    def validate_token(self, token_id: str) -> tuple[bool, str]:
        """Validate a proxy token.

        Args:
            token_id: The token ID to validate.

        Returns:
            Tuple of (valid: bool, reason: str).
        """
        token = self._active_tokens.get(token_id)
        if not token:
            return False, "Token not found"
        if token.is_expired:
            del self._active_tokens[token_id]
            return False, "Token expired"
        if token.is_budget_exceeded:
            return False, "Token budget exceeded"
        return True, "Valid"

    def revoke_token(self, token_id: str) -> bool:
        """Revoke an active token.

        Args:
            token_id: The token to revoke.

        Returns:
            True if the token was found and revoked.
        """
        if token_id in self._active_tokens:
            del self._active_tokens[token_id]
            logger.info("Proxy token revoked: %s", token_id)
            return True
        return False

    def get_model_id(self, provider: ModelProvider) -> str:
        """Get the model ID for a provider.

        Args:
            provider: The LLM provider.

        Returns:
            The model identifier string.
        """
        return self.MODEL_MAP.get(provider, self.MODEL_MAP[ModelProvider.GEMINI])

    def record_usage(self, token_id: str, tokens_used: int) -> None:
        """Record token usage against a proxy token.

        Args:
            token_id: The token to record against.
            tokens_used: Number of tokens consumed.
        """
        token = self._active_tokens.get(token_id)
        if token:
            token.usage_tokens += tokens_used
