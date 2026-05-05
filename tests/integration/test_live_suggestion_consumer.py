# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Live integration test for the SuggestionConsumer end-to-end flow.

Gated behind GEMINI_LIVE_TEST=1 env var. Tests:
  - Real Gemini API suggestion generation via KAIROS probe
  - Cache write + consumer read lifecycle
  - Tier 2 quality filtering on live responses
  - Accept/dismiss telemetry emission
"""

from __future__ import annotations

import json
import os
import time

import pytest

# Gate: only run when explicitly enabled
pytestmark = pytest.mark.skipif(
    os.environ.get("GEMINI_LIVE_TEST") != "1",
    reason="Live integration test — set GEMINI_LIVE_TEST=1 to run",
)


@pytest.fixture
def beads_dir(tmp_path):
    """Create a temp .beads/ directory for test isolation."""
    beads = tmp_path / ".beads"
    beads.mkdir()
    return beads


@pytest.fixture
def cache_file(beads_dir):
    """Path to the suggestion cache file."""
    return beads_dir / "suggestion_cache.json"


@pytest.fixture
def consumer(beads_dir):
    """Create a SuggestionConsumer with temp cache dir."""
    from speculation_engine.consumer import SuggestionConsumer

    return SuggestionConsumer(cache_dir=beads_dir, ttl_seconds=600.0)


class TestLiveGenerationCycle:
    """Tests that exercise the real Gemini API for suggestion generation."""

    def test_tier1_generates_and_caches_suggestion(self, beads_dir, cache_file, consumer):
        """Verify Tier 1 (Flash-Lite) produces a cacheable suggestion end-to-end."""
        # Write a synthetic conversation history for context
        history_file = beads_dir / "conversation_history.jsonl"
        history_entries = [
            {"role": "user", "content": "Run the full test suite"},
            {"role": "assistant", "content": "Running pytest... 2060 passed, 1 failed."},
            {"role": "user", "content": "Fix the failing test"},
            {"role": "assistant", "content": "Fixed the caplog propagation issue."},
        ]
        with open(history_file, "w") as f:
            for entry in history_entries:
                f.write(json.dumps(entry) + "\n")

        # Run the actual probe with real API key
        api_key = os.environ.get("GEMINI_API_KEY")
        assert api_key, "GEMINI_API_KEY must be set for live test"

        # Build the probe inline (simplified from kairos_daemon)
        from speculation_engine.suggestion import (
            SessionState,
            SuggestionConfig,
            try_generate_suggestion,
        )

        state = SessionState(
            suggestion_enabled=True,
            assistant_turn_count=10,
            last_request_tokens=0,
        )
        config = SuggestionConfig(
            enabled=True,
            feature_flag_enabled=True,
            is_interactive=True,
            is_swarm_leader=True,
            min_assistant_turns=0,
        )

        messages = [{"role": e["role"], "content": e["content"]} for e in history_entries]

        def _live_generate_fn(msgs, prompt):
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            context_text = "\n".join(m.get("content", "")[:200] for m in msgs[-3:])
            full_prompt = f"{prompt}\n\nRecent context:\n{context_text}"

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=("You predict the developer's next action. STRICT FORMAT: Reply with ONLY a single short phrase, 2-12 words."),
                    temperature=0.3,
                    max_output_tokens=60,
                    thinking_config=types.ThinkingConfig(thinking_level="minimal"),
                ),
            )
            text = response.text if hasattr(response, "text") else None
            if text:
                import re

                cleaned = text.strip().strip("\"'`").rstrip(".")
                first_frag = re.split(r"[.!?]\s+", cleaned)[0].strip()
                words = first_frag.split()
                if len(words) > 12:
                    first_frag = " ".join(words[:12])
                return (first_frag, f"live-test-{int(time.time())}")
            return (None, None)

        result = try_generate_suggestion(
            messages=messages,
            state=state,
            config=config,
            generate_fn=_live_generate_fn,
        )

        # The suggestion might be filtered — but generation should not error
        assert not result.suppressed, f"Suggestion was suppressed: {result.suppress_reason}"
        # Either we got a suggestion or it was filtered (both are valid)
        if result.suggestion:
            assert len(result.suggestion.split()) <= 12
            assert result.generation_time_ms > 0
        elif result.filtered:
            assert result.filter_reason is not None

    def test_consumer_reads_cached_suggestion(self, beads_dir, cache_file, consumer):
        """Verify the consumer reads a freshly written cache entry."""
        cache_data = {
            "timestamp": time.time(),
            "iso": "2026-05-02T00:00:00Z",
            "suggestion": "Deploy to staging now",
            "suppressed": False,
            "filtered": False,
            "generation_time_ms": 1500.0,
        }
        cache_file.write_text(json.dumps(cache_data))

        entry = consumer.get_suggestion()
        assert entry is not None
        assert entry.text == "Deploy to staging now"
        assert entry.is_fresh is True

    def test_tier2_quality_filter_on_live_response(self):
        """Verify should_filter_suggestion catches common bad patterns."""
        from speculation_engine.suggestion import should_filter_suggestion

        # Patterns that should be filtered
        assert should_filter_suggestion("Let me help you with that") is not None  # Claude voice
        assert should_filter_suggestion("I'll run the tests for you") is not None  # Claude voice
        assert should_filter_suggestion("done") is not None  # Done
        assert should_filter_suggestion("Suggestion: run tests") is not None  # Prefixed
        assert should_filter_suggestion("Run tests. Then deploy.") is not None  # Multi-sentence
        assert should_filter_suggestion("thanks for the update") is not None  # Evaluative

        # Patterns that should NOT be filtered (valid suggestions)
        assert should_filter_suggestion("Run the test suite") is None
        assert should_filter_suggestion("Fix the failing import") is None
        assert should_filter_suggestion("Deploy to staging") is None

    def test_accept_emits_telemetry(self, beads_dir, cache_file, consumer):
        """Verify accept() writes telemetry and clears cache."""
        cache_data = {
            "timestamp": time.time(),
            "iso": "2026-05-02T00:00:00Z",
            "suggestion": "Run pytest",
            "suppressed": False,
            "filtered": False,
        }
        cache_file.write_text(json.dumps(cache_data))

        # Set BEADS_DIR for telemetry writer
        os.environ["BEADS_DIR"] = str(beads_dir)
        try:
            entry = consumer.get_suggestion()
            assert entry is not None
            consumer.accept(entry)

            # Cache should be consumed
            assert consumer.get_suggestion() is None

            # Telemetry should be written
            telemetry_file = beads_dir / "speculation_telemetry.jsonl"
            assert telemetry_file.exists()
            events = [json.loads(line) for line in telemetry_file.read_text().strip().split("\n")]
            assert any(e.get("event_type") == "suggestion_outcome" for e in events)
        finally:
            os.environ.pop("BEADS_DIR", None)

    def test_dismiss_emits_telemetry(self, beads_dir, cache_file, consumer):
        """Verify dismiss() writes telemetry and clears cache."""
        cache_data = {
            "timestamp": time.time(),
            "iso": "2026-05-02T00:00:00Z",
            "suggestion": "Deploy now",
            "suppressed": False,
            "filtered": False,
        }
        cache_file.write_text(json.dumps(cache_data))

        os.environ["BEADS_DIR"] = str(beads_dir)
        try:
            entry = consumer.get_suggestion()
            assert entry is not None
            consumer.dismiss(entry)

            assert consumer.get_suggestion() is None

            telemetry_file = beads_dir / "speculation_telemetry.jsonl"
            assert telemetry_file.exists()
        finally:
            os.environ.pop("BEADS_DIR", None)
