#!/usr/bin/env python3
"""Secret Manager Helper — Thin GCP Secret Manager wrapper.

Provides caching, retry, and environment-aware secret access.
Replaces raw google.cloud.secretmanager calls throughout the monorepo.

Usage:
    from libs.secret_manager_helper import get_secret, list_secrets

    # Get a secret value
    api_key = get_secret("gemini-api-key")

    # Get with specific version
    old_key = get_secret("gemini-api-key", version="2")

    # List all secrets
    secrets = list_secrets()
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

# Cache TTL in seconds (default: 5 minutes)
_CACHE_TTL = int(os.getenv("SECRET_CACHE_TTL", "300"))

# Project ID from environment or default
_PROJECT_ID = os.getenv("GCP_PROJECT", os.getenv("GCLOUD_PROJECT", "shadowtag-omega-v4"))

# In-memory cache: {cache_key: (value, expiry_timestamp)}
_cache: dict[str, tuple[str, float]] = {}


def _get_client():
    """Lazy-load the Secret Manager client."""
    try:
        from google.cloud import secretmanager  # type: ignore[import-untyped]

        return secretmanager.SecretManagerServiceClient()
    except ImportError:
        logger.warning("google-cloud-secret-manager not installed. Install with: pip install google-cloud-secret-manager")
        return None


def get_secret(
    secret_id: str,
    *,
    project_id: str | None = None,
    version: str = "latest",
    use_cache: bool = True,
    max_retries: int = 3,
) -> str:
    """Retrieve a secret value from GCP Secret Manager.

    Args:
        secret_id: The secret ID (e.g., "gemini-api-key").
        project_id: GCP project ID. Defaults to shadowtag-omega-v4.
        version: Secret version. Defaults to "latest".
        use_cache: Whether to use in-memory caching. Defaults to True.
        max_retries: Number of retry attempts on transient failures.

    Returns:
        The secret value as a string.

    Raises:
        RuntimeError: If the secret cannot be retrieved after retries.
        ValueError: If secret_id is empty or contains path separators.
    """
    if not secret_id or "/" in secret_id:
        msg = f"Invalid secret_id: {secret_id!r}. Must be a plain name, not a path."
        raise ValueError(msg)

    project = project_id or _PROJECT_ID
    cache_key = f"{project}/{secret_id}/{version}"

    # Check cache first
    if use_cache and cache_key in _cache:
        value, expiry = _cache[cache_key]
        if time.time() < expiry:
            logger.debug("Cache hit for secret: %s", secret_id)
            return value
        else:
            del _cache[cache_key]

    # Check environment fallback (for local dev without Secret Manager access)
    env_key = secret_id.upper().replace("-", "_")
    env_value = os.getenv(env_key)
    if env_value:
        logger.debug("Using environment fallback for secret: %s → $%s", secret_id, env_key)
        if use_cache:
            _cache[cache_key] = (env_value, time.time() + _CACHE_TTL)
        return env_value

    # Access Secret Manager
    client = _get_client()
    if client is None:
        msg = f"Cannot retrieve secret '{secret_id}': google-cloud-secret-manager not installed and no environment variable ${env_key} found."
        raise RuntimeError(msg)

    name = f"projects/{project}/secrets/{secret_id}/versions/{version}"

    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            response = client.access_secret_version(request={"name": name})
            value = response.payload.data.decode("utf-8")

            # Cache the result
            if use_cache:
                _cache[cache_key] = (value, time.time() + _CACHE_TTL)

            logger.debug("Retrieved secret: %s (attempt %d)", secret_id, attempt + 1)
            return value

        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                # Exponential backoff: 0.5s, 1s, 2s
                wait = 0.5 * (2**attempt)
                logger.warning(
                    "Retry %d/%d for secret '%s': %s (waiting %.1fs)",
                    attempt + 1,
                    max_retries,
                    secret_id,
                    e,
                    wait,
                )
                time.sleep(wait)

    msg = f"Failed to retrieve secret '{secret_id}' after {max_retries} attempts: {last_error}"
    raise RuntimeError(msg)


def list_secrets(
    project_id: str | None = None,
    filter_str: str = "",
) -> list[dict[str, Any]]:
    """List all secrets in the project.

    Args:
        project_id: GCP project ID. Defaults to shadowtag-omega-v4.
        filter_str: Optional filter string (e.g., "labels.env=prod").

    Returns:
        List of secret metadata dicts with 'name' and 'labels' keys.
    """
    project = project_id or _PROJECT_ID
    client = _get_client()

    if client is None:
        logger.warning("Cannot list secrets: google-cloud-secret-manager not installed")
        return []

    parent = f"projects/{project}"
    request: dict[str, Any] = {"parent": parent}
    if filter_str:
        request["filter"] = filter_str

    secrets = []
    for secret in client.list_secrets(request=request):
        secrets.append(
            {
                "name": secret.name.split("/")[-1],
                "full_name": secret.name,
                "labels": dict(secret.labels) if secret.labels else {},
                "create_time": secret.create_time.isoformat() if secret.create_time else None,
            }
        )

    return secrets


def clear_cache() -> int:
    """Clear the in-memory secret cache.

    Returns:
        Number of cache entries cleared.
    """
    count = len(_cache)
    _cache.clear()
    logger.info("Cleared %d cached secrets", count)
    return count


# Known secrets registry for documentation and IDE autocomplete
KNOWN_SECRETS = {
    "developer-knowledge-api-key": "Google Developer Knowledge MCP API key",
    "stitch-api-key": "Stitch MCP API key",
    "google-design-api-key": "Google Design API key",
    "gemini-api-key": "Gemini API key for runtime inference",
    "stripe-secret-key": "Stripe secret key (live mode)",
    "stripe-publishable-key": "Stripe publishable key (frontend-safe)",
    "stripe-webhook-secret": "Stripe webhook signing secret",
    "KOVEL_ATTESTATION_SECRET": "Kovel attestation HMAC secret",
    "MAGIC_LINK_SECRET": "Magic link authentication secret",
    "github-app-shadowtag-v2-pem": "GitHub App PEM private key",
}
