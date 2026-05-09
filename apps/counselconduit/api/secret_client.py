# apps/counselconduit/api/secret_client.py
"""Secret Manager client for CounselConduit.

Replaces direct .env reads with Secret Manager lookups in production.
Falls back to os.getenv() for local development.

Usage:
    from api.secret_client import get_secret
    stripe_key = get_secret("STRIPE_SECRET_KEY", "stripe-secret-key")

Architecture:
    - Production (Cloud Run): secrets mounted as env vars via --set-secrets
    - Staging (Cloud Run): same mechanism, test keys
    - Local dev: reads from .env via os.getenv()

    The --set-secrets flag on Cloud Run injects Secret Manager values
    as environment variables at container start. This means os.getenv()
    works for ALL environments — no Secret Manager API calls needed at
    runtime. This module exists for:
    1. Explicit documentation of the secret → env var mapping
    2. Fallback to Secret Manager API if env var is missing
    3. Secret rotation support (version pinning)
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache

logger = logging.getLogger("counselconduit.secrets")

# Project ID for Secret Manager lookups
_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "shadowtag-omega-v4")

# Mapping: environment variable name → Secret Manager secret name
SECRET_MAP: dict[str, str] = {
    "STRIPE_SECRET_KEY": "stripe-secret-key",
    "STRIPE_WEBHOOK_SECRET": "stripe-webhook-secret",
    "STRIPE_PUBLISHABLE_KEY": "stripe-publishable-key",
    "STRIPE_CONNECT_WEBHOOK_SECRET": "stripe-connect-webhook-secret",
    "DISCORD_WEBHOOK_URL": "discord-webhook-url",
    "RESEND_API_KEY": "resend-api-key",
    "STITCH_API_KEY": "stitch-api-key",
    "GEMINI_API_KEY": "gemini-api-key",
    "DEVELOPER_KNOWLEDGE_API_KEY": "developer-knowledge-api-key",
}


@lru_cache(maxsize=32)
def get_secret(
    env_var: str,
    secret_name: str | None = None,
    version: str = "latest",
) -> str | None:
    """Get a secret value.

    Resolution order:
    1. Environment variable (works for both local .env and Cloud Run --set-secrets)
    2. Secret Manager API lookup (fallback, protected by circuit breaker)
    3. None (secret not found)

    Args:
        env_var: Environment variable name (e.g., "STRIPE_SECRET_KEY").
        secret_name: Secret Manager name. If None, looked up from SECRET_MAP.
        version: Secret version (default: "latest").

    Returns:
        Secret value string, or None if not found.
    """
    # Try environment variable first (covers both local and Cloud Run)
    value = os.getenv(env_var)
    if value:
        return value

    # Resolve secret name from map if not provided
    if secret_name is None:
        secret_name = SECRET_MAP.get(env_var)
        if not secret_name:
            logger.warning("No Secret Manager mapping for %s", env_var)
            return None

    # Circuit breaker gate for Secret Manager API calls
    breaker = None
    try:
        from circuit_breaker.telemetry_bridge import default_registry

        breaker = default_registry.get_or_create(
            "secret_manager",
            failure_threshold=3,
            reset_timeout_s=60.0,
        )
        if not breaker.allow_request():
            logger.warning(
                "Circuit breaker OPEN for secret_manager — skipping API call for %s (probe in %.0fs)",
                env_var,
                breaker.seconds_until_probe,
            )
            return None
    except Exception:
        pass  # Circuit breaker not available — proceed without protection

    # Fallback: query Secret Manager API directly
    try:
        from google.cloud import secretmanager

        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{_PROJECT_ID}/secrets/{secret_name}/versions/{version}"
        response = client.access_secret_version(request={"name": name})
        value = response.payload.data.decode("UTF-8")
        logger.info("Loaded %s from Secret Manager", env_var)
        if breaker:
            breaker.record_success()
        return value
    except Exception as e:
        logger.warning("Failed to load %s from Secret Manager: %s", env_var, e)
        if breaker:
            breaker.record_failure()
        return None


def get_all_secrets() -> dict[str, str | None]:
    """Load all mapped secrets. Returns dict of env_var → value."""
    return {env_var: get_secret(env_var) for env_var in SECRET_MAP}


def validate_required_secrets(required: list[str]) -> list[str]:
    """Check that all required secrets are available.

    Args:
        required: List of environment variable names that must be present.

    Returns:
        List of missing secret names (empty if all present).
    """
    missing = []
    for env_var in required:
        if get_secret(env_var) is None:
            missing.append(env_var)
    return missing
