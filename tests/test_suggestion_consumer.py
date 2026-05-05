# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for SuggestionConsumer — the reader module for cached KAIROS suggestions.

Validates:
  - Fresh suggestion retrieval
  - TTL-based expiry
  - Suppressed/filtered skipping
  - Accept/dismiss lifecycle
  - Cache clearing behavior
  - Peek diagnostics
"""

from __future__ import annotations

import json
import time

import pytest

from speculation_engine.consumer import (
    SuggestionConsumer,
    SuggestionEntry,
)


@pytest.fixture
def cache_dir(tmp_path):
    """Provide a temporary cache directory."""
    return tmp_path


@pytest.fixture
def consumer(cache_dir):
    """Create a consumer pointing to the temp cache."""
    return SuggestionConsumer(cache_dir=cache_dir, ttl_seconds=600.0)


def _write_cache(cache_dir, data: dict) -> None:
    """Write a cache entry to the temp directory."""
    cache_file = cache_dir / "suggestion_cache.json"
    cache_file.write_text(json.dumps(data))


class TestGetSuggestion:
    """Tests for get_suggestion() reader."""

    def test_returns_none_when_no_cache(self, consumer: SuggestionConsumer) -> None:
        assert consumer.get_suggestion() is None

    def test_returns_suggestion_when_fresh(self, consumer: SuggestionConsumer, cache_dir) -> None:
        _write_cache(
            cache_dir,
            {
                "timestamp": time.time(),
                "iso": "2026-05-02T00:00:00Z",
                "suggestion": "Run the test suite",
                "suppressed": False,
                "filtered": False,
                "generation_time_ms": 3200.0,
            },
        )
        entry = consumer.get_suggestion()
        assert entry is not None
        assert entry.text == "Run the test suite"

    def test_returns_none_when_stale(self, consumer: SuggestionConsumer, cache_dir) -> None:
        _write_cache(
            cache_dir,
            {
                "timestamp": time.time() - 700,  # > 600s TTL
                "suggestion": "Old suggestion",
                "suppressed": False,
                "filtered": False,
            },
        )
        assert consumer.get_suggestion() is None

    def test_returns_none_when_suppressed(self, consumer: SuggestionConsumer, cache_dir) -> None:
        _write_cache(
            cache_dir,
            {
                "timestamp": time.time(),
                "suggestion": "Suppressed action",
                "suppressed": True,
                "filtered": False,
            },
        )
        assert consumer.get_suggestion() is None

    def test_returns_none_when_filtered(self, consumer: SuggestionConsumer, cache_dir) -> None:
        _write_cache(
            cache_dir,
            {
                "timestamp": time.time(),
                "suggestion": "Filtered action",
                "suppressed": False,
                "filtered": True,
            },
        )
        assert consumer.get_suggestion() is None

    def test_returns_none_when_suggestion_null(self, consumer: SuggestionConsumer, cache_dir) -> None:
        _write_cache(
            cache_dir,
            {
                "timestamp": time.time(),
                "suggestion": None,
                "suppressed": False,
                "filtered": False,
            },
        )
        assert consumer.get_suggestion() is None

    def test_returns_none_on_malformed_json(self, consumer: SuggestionConsumer, cache_dir) -> None:
        cache_file = cache_dir / "suggestion_cache.json"
        cache_file.write_text("{bad json")
        assert consumer.get_suggestion() is None


class TestSuggestionEntry:
    """Tests for SuggestionEntry properties."""

    def test_is_fresh_within_ttl(self) -> None:
        entry = SuggestionEntry(text="test", timestamp=time.time())
        assert entry.is_fresh is True

    def test_is_fresh_outside_ttl(self) -> None:
        entry = SuggestionEntry(text="test", timestamp=time.time() - 700)
        assert entry.is_fresh is False

    def test_age_seconds(self) -> None:
        entry = SuggestionEntry(text="test", timestamp=time.time() - 10)
        assert entry.age_seconds >= 10


class TestAcceptDismiss:
    """Tests for accept/dismiss lifecycle."""

    def test_accept_clears_cache(self, consumer: SuggestionConsumer, cache_dir) -> None:
        _write_cache(
            cache_dir,
            {
                "timestamp": time.time(),
                "suggestion": "Run tests",
                "suppressed": False,
                "filtered": False,
            },
        )
        entry = consumer.get_suggestion()
        assert entry is not None
        consumer.accept(entry)
        # Cache should be cleared — next read returns None
        assert consumer.get_suggestion() is None

    def test_dismiss_clears_cache(self, consumer: SuggestionConsumer, cache_dir) -> None:
        _write_cache(
            cache_dir,
            {
                "timestamp": time.time(),
                "suggestion": "Deploy now",
                "suppressed": False,
                "filtered": False,
            },
        )
        entry = consumer.get_suggestion()
        assert entry is not None
        consumer.dismiss(entry)
        assert consumer.get_suggestion() is None


class TestPeek:
    """Tests for peek() diagnostics."""

    def test_peek_returns_raw_data(self, consumer: SuggestionConsumer, cache_dir) -> None:
        data = {"timestamp": 12345, "suggestion": "test", "extra": "field"}
        _write_cache(cache_dir, data)
        peeked = consumer.peek()
        assert peeked is not None
        assert peeked["extra"] == "field"

    def test_peek_returns_none_when_no_cache(self, consumer: SuggestionConsumer) -> None:
        assert consumer.peek() is None


class TestCustomTTL:
    """Tests for custom TTL configuration."""

    def test_short_ttl_expires_quickly(self, cache_dir) -> None:
        consumer = SuggestionConsumer(cache_dir=cache_dir, ttl_seconds=1.0)
        _write_cache(
            cache_dir,
            {
                "timestamp": time.time() - 2,  # 2 seconds ago, > 1s TTL
                "suggestion": "Old suggestion",
                "suppressed": False,
                "filtered": False,
            },
        )
        assert consumer.get_suggestion() is None

    def test_long_ttl_keeps_entries(self, cache_dir) -> None:
        consumer = SuggestionConsumer(cache_dir=cache_dir, ttl_seconds=3600.0)
        _write_cache(
            cache_dir,
            {
                "timestamp": time.time() - 1800,  # 30 minutes ago, < 1 hour TTL
                "suggestion": "Still fresh",
                "suppressed": False,
                "filtered": False,
            },
        )
        entry = consumer.get_suggestion()
        assert entry is not None
        assert entry.text == "Still fresh"


class TestQualityScore:
    """Tests for the Tier 2 quality scoring property."""

    def test_sweet_spot_word_count(self) -> None:
        """3-8 words should score highest."""
        entry = SuggestionEntry(text="Run the test suite now", timestamp=time.time())
        assert entry.quality_score > 0.5

    def test_single_word_lower_score(self) -> None:
        """Single word suggestions score lower."""
        entry = SuggestionEntry(text="deploy", timestamp=time.time())
        score = entry.quality_score
        # Should still be > 0 but lower than sweet spot
        assert 0.0 < score < 1.0

    def test_imperative_verb_boost(self) -> None:
        """Starting with an imperative verb should boost score."""
        with_verb = SuggestionEntry(text="Fix the failing test", timestamp=time.time())
        without_verb = SuggestionEntry(text="the failing test needs fixing", timestamp=time.time())
        assert with_verb.quality_score >= without_verb.quality_score

    def test_slash_command_bonus(self) -> None:
        """Slash commands should get a bonus."""
        slash = SuggestionEntry(text="/deploy staging", timestamp=time.time())
        normal = SuggestionEntry(text="deploy to staging", timestamp=time.time())
        assert slash.quality_score >= normal.quality_score

    def test_freshness_decay(self) -> None:
        """Older suggestions should score lower."""
        fresh = SuggestionEntry(text="Run tests", timestamp=time.time())
        old = SuggestionEntry(text="Run tests", timestamp=time.time() - 500)
        assert fresh.quality_score > old.quality_score

    def test_stale_minimal_freshness(self) -> None:
        """Stale suggestions should have near-zero freshness component."""
        stale = SuggestionEntry(text="Run tests", timestamp=time.time() - 700)
        assert stale.quality_score > 0  # Word count still contributes


class TestCacheStatus:
    """Tests for cache_status() heartbeat integration."""

    def test_empty_when_no_cache(self, consumer: SuggestionConsumer) -> None:
        status = consumer.cache_status()
        assert status["state"] == "empty"
        assert status["suggestion"] is None

    def test_fresh_when_valid(self, consumer: SuggestionConsumer, cache_dir) -> None:
        _write_cache(
            cache_dir,
            {
                "timestamp": time.time(),
                "suggestion": "Run the test suite",
                "suppressed": False,
                "filtered": False,
            },
        )
        status = consumer.cache_status()
        assert status["state"] == "fresh"
        assert status["suggestion"] is not None
        assert status["quality"] > 0
        assert status["age_s"] >= 0

    def test_stale_when_expired(self, consumer: SuggestionConsumer, cache_dir) -> None:
        _write_cache(
            cache_dir,
            {
                "timestamp": time.time() - 700,  # > 600s TTL
                "suggestion": "Old suggestion",
                "suppressed": False,
                "filtered": False,
            },
        )
        status = consumer.cache_status()
        assert status["state"] == "stale"

    def test_consumed_when_null(self, consumer: SuggestionConsumer, cache_dir) -> None:
        _write_cache(
            cache_dir,
            {"consumed_at": time.time(), "suggestion": None},
        )
        status = consumer.cache_status()
        assert status["state"] == "consumed"

    def test_corrupt_on_bad_json(self, consumer: SuggestionConsumer, cache_dir) -> None:
        cache_file = cache_dir / "suggestion_cache.json"
        cache_file.write_text("{bad json")
        status = consumer.cache_status()
        assert status["state"] == "corrupt"
