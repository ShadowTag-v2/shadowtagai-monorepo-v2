"""Undercover mode — safety utilities for contributing to public/open-source repos.

When active, the AGNT framework adds safety instructions to commit/PR prompts
and strips all attribution to avoid leaking internal model codenames, project
names, or other organisation-internal information. The model is not told what
model it is.

Activation:
  - ``AGNT_UNDERCOVER=1``   — force ON (even in internal repos)
  - Otherwise AUTO: active UNLESS the repo remote matches the internal
    allowlist (:data:`repo_classification.INTERNAL_REPO_PATTERNS`). Safe
    default is ON — the agent may push to public remotes from a CWD that
    is not itself a git checkout (e.g. /tmp crash repro).
  - There is **NO force-OFF**. This guards against model codename leaks —
    if we are not confident we are in an internal repo, we stay undercover.

All code paths are gated on ``os.environ.get("AGNT_UNDERCOVER_ENABLED")``.
When the env var is unset the feature is dormant (external builds). When set
to any truthy value, the full undercover pipeline activates.

Ported from: Claude Code utils/undercover.ts
"""

from __future__ import annotations

import os
from typing import Any

from .repo_classification import get_repo_class, is_internal_repo

__all__ = [
    "is_undercover",
    "get_undercover_instructions",
    "should_show_auto_notice",
    # Re-exports from repo_classification
    "get_repo_class",
    "is_internal_repo",
]

# --- Environment helpers ---


def _is_env_truthy(key: str) -> bool:
    """Return ``True`` if env var *key* is set to a truthy value."""
    val = os.environ.get(key, "").strip().lower()
    return val in {"1", "true", "yes", "on"}


def _is_feature_enabled() -> bool:
    """Return ``True`` if undercover mode is available in this build.

    Maps to the ``process.env.USER_TYPE === 'ant'`` gate in the TS source.
    For the AGNT framework, set ``AGNT_UNDERCOVER_ENABLED=1`` to enable.
    """
    return _is_env_truthy("AGNT_UNDERCOVER_ENABLED")


# --- Per-session state ---

_has_seen_auto_notice: bool = False


def mark_auto_notice_seen() -> None:
    """Record that the one-time auto-undercover notice was shown."""
    global _has_seen_auto_notice
    _has_seen_auto_notice = True


# --- Public API ---


def is_undercover() -> bool:
    """Return ``True`` if undercover mode is currently active.

    Activation rules:
    1. Feature gate (``AGNT_UNDERCOVER_ENABLED``) must be truthy.
    2. ``AGNT_UNDERCOVER=1`` forces ON regardless of repo class.
    3. Otherwise auto: active UNLESS the repo is classified ``'internal'``.
       ``'external'``, ``'none'``, and ``None`` (check not yet run) all
       resolve to ON.
    4. There is **no force-OFF** — if we cannot confirm internal, we stay
       undercover.
    """
    if not _is_feature_enabled():
        return False

    if _is_env_truthy("AGNT_UNDERCOVER"):
        return True

    # Auto: active unless positively confirmed internal.
    return get_repo_class() != "internal"


def get_undercover_instructions() -> str:
    """Return the safety instructions injected when undercover.

    These instructions are appended to commit/PR system prompts to prevent
    the agent from leaking internal model codenames or attribution.

    Returns:
        The full instruction block if undercover is enabled, else ``""``.
    """
    if not _is_feature_enabled():
        return ""

    return """## UNDERCOVER MODE — CRITICAL

You are operating UNDERCOVER in a PUBLIC/OPEN-SOURCE repository. Your commit
messages, PR titles, and PR bodies MUST NOT contain ANY organisation-internal
information. Do not blow your cover.

NEVER include in commit messages or PR descriptions:
- Internal model codenames (animal names, project code words, etc.)
- Unreleased model version numbers
- Internal repo or project names
- Internal tooling, messaging channels, or short links
- The phrase "AI assistant" or any mention that you are an AI
- Any hint of what model or version you are
- Co-Authored-By lines or any other attribution

Write commit messages as a human developer would — describe only what the code
change does.

GOOD:
- "Fix race condition in file watcher initialization"
- "Add support for custom key bindings"
- "Refactor parser for better error messages"

BAD (never write these):
- "Fix bug found while testing with [model codename]"
- "Generated with [AI product name]"
- "Co-Authored-By: [AI identity]"
"""


def should_show_auto_notice() -> bool:
    """Check whether to show the one-time explainer dialog.

    Returns ``True`` when undercover is active via auto-detection (not forced
    via ``AGNT_UNDERCOVER=1``) and the user hasn't seen the notice before.
    """
    if not _is_feature_enabled():
        return False
    # If forced via env, user already knows — don't nag.
    if _is_env_truthy("AGNT_UNDERCOVER"):
        return False
    if not is_undercover():
        return False
    return not _has_seen_auto_notice


def get_config() -> dict[str, Any]:
    """Return a snapshot of the current undercover configuration.

    Useful for diagnostics and the /status CLI command.
    """
    return {
        "feature_enabled": _is_feature_enabled(),
        "forced_on": _is_env_truthy("AGNT_UNDERCOVER"),
        "repo_class": get_repo_class(),
        "is_undercover": is_undercover(),
        "has_seen_auto_notice": _has_seen_auto_notice,
    }
