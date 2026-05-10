"""Voice mode feature gate.

Ported from src/voice/voiceModeEnabled.ts

Three-layer gate:
  1. GrowthBook kill-switch (tengu_amber_quartz_disabled)
  2. Auth provider check (Anthropic OAuth required)
  3. Token existence check (access_token must be present)

Design decisions:
  - Uses protocol-based dependency injection so callers provide their own
    token/auth/flag implementations rather than importing concrete modules.
  - Default providers read from environment variables for zero-config
    local development.
  - Fail-open for the kill-switch: a missing flag defaults to False
    (not killed), so fresh installs get voice working immediately.
"""

from __future__ import annotations

import logging
import os

from ._types import AuthChecker, FeatureFlagProvider, TokenProvider

logger = logging.getLogger(__name__)

# ─── Environment-based defaults ──────────────────────────────────────

# These default providers read from env vars. In production, callers
# should inject real GrowthBook / OAuth providers.

_VOICE_MODE_ENV = "AGNT_VOICE_MODE"
_VOICE_KILLSWITCH_ENV = "AGNT_VOICE_KILLED"
_VOICE_TOKEN_ENV = "AGNT_VOICE_TOKEN"
_AUTH_ENABLED_ENV = "AGNT_AUTH_ENABLED"


def _default_feature_flag(flag_name: str, default: bool) -> bool:
  """Environment-based feature flag provider.

  Checks AGNT_VOICE_KILLED for the kill-switch. Returns the env
  value (truthy = 1/true/yes) or falls back to *default*.
  """
  if flag_name == "tengu_amber_quartz_disabled":
    val = os.environ.get(_VOICE_KILLSWITCH_ENV, "").strip().lower()
    if val in ("1", "true", "yes"):
      return True
    if val in ("0", "false", "no"):
      return False
    return default
  return default


def _default_auth_checker() -> bool:
  """Check if Anthropic auth is enabled via env var."""
  return os.environ.get(_AUTH_ENABLED_ENV, "").strip().lower() in (
    "1",
    "true",
    "yes",
  )


def _default_token_provider() -> str | None:
  """Read OAuth access token from env var."""
  token = os.environ.get(_VOICE_TOKEN_ENV, "").strip()
  return token if token else None


# ─── Gate functions ──────────────────────────────────────────────────


def is_voice_growthbook_enabled(
  *,
  feature_flag: FeatureFlagProvider = _default_feature_flag,
) -> bool:
  """Kill-switch check for voice mode.

  Returns True unless ``tengu_amber_quartz_disabled`` is flipped on
  (emergency off). Default ``False`` means a missing/stale cache reads
  as "not killed" — so fresh installs get voice working immediately
  without waiting for GrowthBook init.

  Use this for deciding whether voice mode should be *visible*
  (e.g., command registration, config UI).
  """
  # Check if voice mode feature is enabled at all
  voice_mode = os.environ.get(_VOICE_MODE_ENV, "").strip().lower()
  if voice_mode in ("0", "false", "no"):
    return False

  # Positive ternary pattern — kill-switch is negative logic
  return not feature_flag("tengu_amber_quartz_disabled", False)


def has_voice_auth(
  *,
  auth_checker: AuthChecker = _default_auth_checker,
  token_provider: TokenProvider = _default_token_provider,
) -> bool:
  """Auth-only check for voice mode.

  Returns True when the user has a valid Anthropic OAuth token.
  Voice mode requires Anthropic OAuth — it uses the voice_stream
  endpoint on claude.ai which is not available with API keys,
  Bedrock, Vertex, or Foundry.
  """
  if not auth_checker():
    return False
  # auth_checker only checks the auth *provider*, not whether a token
  # exists. Without this check, the voice UI renders but
  # connect_voice_stream fails silently when the user isn't logged in.
  token = token_provider()
  return token is not None and len(token) > 0


def is_voice_mode_enabled(
  *,
  auth_checker: AuthChecker = _default_auth_checker,
  token_provider: TokenProvider = _default_token_provider,
  feature_flag: FeatureFlagProvider = _default_feature_flag,
) -> bool:
  """Full runtime check: auth + GrowthBook kill-switch.

  Callers: ``/voice`` command, ConfigTool, VoiceModeNotice —
  command-time paths where a fresh token read is acceptable.
  """
  return has_voice_auth(
    auth_checker=auth_checker,
    token_provider=token_provider,
  ) and is_voice_growthbook_enabled(feature_flag=feature_flag)
