# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Suggestion Consumer — Reads cached proactive suggestions from KAIROS.

Architecture (ported from Claude Code v2.1.91 promptSuggestion consumer):
  - Reads .beads/suggestion_cache.json produced by KAIROS daemon's
    run_proactive_suggestion_probe()
  - Validates freshness (TTL-based expiry)
  - Returns typed SuggestionEntry for display or acceptance
  - Clears stale entries to prevent showing outdated suggestions

Usage:
    from speculation_engine.consumer import SuggestionConsumer

    consumer = SuggestionConsumer()
    entry = consumer.get_suggestion()
    if entry:
        print(f"Suggestion: {entry.text}")
        if user_accepted:
            consumer.accept(entry)
        else:
            consumer.dismiss(entry)
"""

from __future__ import annotations

import json
import logging
import pathlib
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Default cache location
DEFAULT_CACHE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / ".beads"
# Suggestion TTL: 10 minutes
SUGGESTION_TTL_SECONDS = 600.0


@dataclass
class SuggestionEntry:
    """A cached proactive suggestion.

    Attributes:
        text: The suggestion text.
        timestamp: When the suggestion was generated (epoch seconds).
        iso: ISO-8601 timestamp string.
        generation_time_ms: How long generation took.
        suppressed: Whether the suggestion was suppressed by gates.
        filtered: Whether the suggestion was filtered by client rules.
        generation_request_id: Correlation ID for telemetry.
    """

    text: str
    timestamp: float
    iso: str = ""
    generation_time_ms: float = 0.0
    suppressed: bool = False
    filtered: bool = False
    generation_request_id: str | None = None

    @property
    def age_seconds(self) -> float:
        """Time since this suggestion was generated."""
        return time.time() - self.timestamp

    @property
    def is_fresh(self) -> bool:
        """Whether this suggestion is within TTL."""
        return self.age_seconds < SUGGESTION_TTL_SECONDS


class SuggestionConsumer:
    """Reader for KAIROS-generated proactive suggestions.

    Reads from .beads/suggestion_cache.json, validates freshness,
    and provides accept/dismiss lifecycle methods for telemetry.

    Args:
        cache_dir: Directory containing suggestion_cache.json.
            Defaults to the repo's .beads/ directory.
        ttl_seconds: Maximum age in seconds before a suggestion is stale.
    """

    def __init__(
        self,
        *,
        cache_dir: pathlib.Path | None = None,
        ttl_seconds: float = SUGGESTION_TTL_SECONDS,
    ) -> None:
        self._cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self._ttl = ttl_seconds
        self._cache_file = self._cache_dir / "suggestion_cache.json"

    def get_suggestion(self) -> SuggestionEntry | None:
        """Read the latest cached suggestion.

        Returns None if:
          - No cache file exists
          - The cache is malformed
          - The suggestion is stale (exceeded TTL)
          - The suggestion was suppressed or filtered
          - The suggestion text is empty
        """
        if not self._cache_file.exists():
            logger.debug("No suggestion cache file at %s", self._cache_file)
            return None

        try:
            data = json.loads(self._cache_file.read_text())
        except (json.JSONDecodeError, OSError) as e:
            logger.debug("Failed to read suggestion cache: %s", e)
            return None

        suggestion_text = data.get("suggestion")
        if not suggestion_text:
            return None

        # Check staleness
        ts = data.get("timestamp", 0)
        age = time.time() - ts
        if age > self._ttl:
            logger.debug("Suggestion is stale (%.0fs > %.0fs TTL)", age, self._ttl)
            return None

        # Skip suppressed/filtered
        if data.get("suppressed"):
            return None
        if data.get("filtered"):
            return None

        return SuggestionEntry(
            text=suggestion_text,
            timestamp=ts,
            iso=data.get("iso", ""),
            generation_time_ms=data.get("generation_time_ms", 0.0),
            suppressed=data.get("suppressed", False),
            filtered=data.get("filtered", False),
            generation_request_id=data.get("generation_request_id"),
        )

    def accept(self, entry: SuggestionEntry) -> None:
        """Mark a suggestion as accepted and log telemetry.

        Clears the cache file to prevent re-display.
        """
        from speculation_engine.suggestion import SuggestionOutcome, log_suggestion_outcome

        outcome = SuggestionOutcome(
            suggestion=entry.text,
            was_accepted=True,
            generation_request_id=entry.generation_request_id,
            displayed_at=entry.timestamp,
        )
        log_suggestion_outcome(outcome, entry.text)
        self._clear_cache()
        logger.info("Suggestion accepted: '%s'", entry.text[:40])

    def dismiss(self, entry: SuggestionEntry) -> None:
        """Mark a suggestion as dismissed and log telemetry.

        Clears the cache file to prevent re-display.
        """
        from speculation_engine.suggestion import SuggestionOutcome, log_suggestion_outcome

        outcome = SuggestionOutcome(
            suggestion=entry.text,
            was_accepted=False,
            generation_request_id=entry.generation_request_id,
            displayed_at=entry.timestamp,
        )
        log_suggestion_outcome(outcome, "")
        self._clear_cache()
        logger.debug("Suggestion dismissed: '%s'", entry.text[:40])

    def peek(self) -> dict | None:
        """Read the raw cache without validation — for diagnostics."""
        if not self._cache_file.exists():
            return None
        try:
            return json.loads(self._cache_file.read_text())
        except Exception:
            return None

    def _clear_cache(self) -> None:
        """Clear the suggestion cache after consumption."""
        try:
            if self._cache_file.exists():
                # Write an empty entry rather than deleting (immutable infra)
                self._cache_file.write_text(
                    json.dumps({"consumed_at": time.time(), "suggestion": None})
                )
        except OSError as e:
            logger.debug("Failed to clear suggestion cache: %s", e)
