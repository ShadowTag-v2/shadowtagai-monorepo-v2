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
