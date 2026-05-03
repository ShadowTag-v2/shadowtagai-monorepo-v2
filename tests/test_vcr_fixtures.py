# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for VCR Fixture Manager — record/replay, scrubbing, gating, modes.

Covers:
    - CassetteMode behavior (RECORD, REPLAY, NEW_EPISODES, OFF)
    - Request fingerprinting stability
    - Auto-scrubbing of API keys, tokens, and secrets
    - Test gate enforcement (PYTEST_CURRENT_TEST, NODE_ENV)
    - Fixture file I/O (save/load cycle)
    - Error paths (missing fixture in REPLAY, missing real_caller)
    - FixtureManager factory and cassette listing

Reference: strategic-testing/SKILL.md VCR section
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from vcr_fixtures.manager import (
    Cassette,
    CassetteMode,
    FixtureManager,
    RecordedInteraction,
    RecordedRequest,
    RecordedResponse,
    scrub_sensitive,
)


# ── Test Helpers ──


def _make_request(
    method: str = "POST",
    url: str = "https://api.example.com/v1/generate",
    body: str = '{"prompt": "hello"}',
) -> RecordedRequest:
    return RecordedRequest(method=method, url=url, body=body)


def _make_response(
    status_code: int = 200,
    body: str = '{"text": "world"}',
) -> RecordedResponse:
    return RecordedResponse(status_code=status_code, body=body, elapsed_ms=42.0)


def _fake_caller(response: RecordedResponse) -> callable:
    """Create a fake real_caller that returns a fixed response."""

    def caller(request: RecordedRequest) -> RecordedResponse:
        return response

    return caller


# ── Scrubbing Tests ──


class TestScrubSensitive:
    """Tests for automatic secret scrubbing."""

    def test_scrub_bearer_token(self):
        text = "Authorization: Bearer sk-abc123xyz456"
        result = scrub_sensitive(text)
        assert "sk-abc123xyz456" not in result
        assert "[SCRUBBED]" in result

    def test_scrub_api_key_param(self):
        text = "https://api.example.com?key=AIzaSyAbc123"
        result = scrub_sensitive(text)
        assert "AIzaSyAbc123" not in result
        assert "key=[SCRUBBED]" in result

    def test_scrub_x_goog_api_key(self):
        text = "x-goog-api-key: AIzaSyAbcDef123"
        result = scrub_sensitive(text)
        assert "AIzaSyAbcDef123" not in result

    def test_scrub_json_api_key(self):
        text = '{"api_key": "secret-key-value"}'
        result = scrub_sensitive(text)
        assert "secret-key-value" not in result

    def test_scrub_oauth_tokens(self):
        text = '{"access_token": "ya29.abc", "refresh_token": "1//xyz"}'
        result = scrub_sensitive(text)
        assert "ya29.abc" not in result
        assert "1//xyz" not in result

    def test_scrub_preserves_non_secret_text(self):
        text = "Hello, this is a normal response with no secrets."
        result = scrub_sensitive(text)
        assert result == text

    def test_scrub_stripe_secret_key_live(self):
        text = "sk_live_51Hj7abcdefghijklmnopqrstuvwxyz"
        result = scrub_sensitive(text)
        assert "51Hj7abcdefghijklmnopqrstuvwxyz" not in result
        assert "sk_live_[SCRUBBED]" in result

    def test_scrub_stripe_secret_key_test(self):
        text = "sk_test_51Hj7TestKey123456789"
        result = scrub_sensitive(text)
        assert "51Hj7TestKey123456789" not in result
        assert "sk_test_[SCRUBBED]" in result

    def test_scrub_stripe_publishable_key(self):
        text = "pk_live_51Hj7PublishableKeyValue"
        result = scrub_sensitive(text)
        assert "51Hj7PublishableKeyValue" not in result
        assert "pk_live_[SCRUBBED]" in result

    def test_scrub_stripe_webhook_secret(self):
        text = "whsec_AbcDefGhi123456789"
        result = scrub_sensitive(text)
        assert "AbcDefGhi123456789" not in result
        assert "whsec_[SCRUBBED]" in result

    def test_scrub_gcp_private_key(self):
        text = '{"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIE..."}'
        result = scrub_sensitive(text)
        assert "BEGIN RSA PRIVATE KEY" not in result
        assert "[SCRUBBED]" in result

    def test_scrub_gcp_private_key_id(self):
        text = '{"private_key_id": "abc123def456ghi789"}'
        result = scrub_sensitive(text)
        assert "abc123def456ghi789" not in result

    def test_scrub_firebase_id_token(self):
        text = '{"idToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature"}'
        result = scrub_sensitive(text)
        assert "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9" not in result

    def test_scrub_oidc_id_token(self):
        text = '{"id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.claims.sig"}'
        result = scrub_sensitive(text)
        assert "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9" not in result

    def test_scrub_password_field(self):
        text = '{"password": "hunter2"}'
        result = scrub_sensitive(text)
        assert "hunter2" not in result
        assert "[SCRUBBED]" in result

    def test_scrub_client_secret(self):
        text = '{"client_secret": "GOCSPX-abc123xyz456"}'
        result = scrub_sensitive(text)
        assert "GOCSPX-abc123xyz456" not in result

    def test_scrub_cookie_header(self):
        text = "Cookie: session=abc123; token=xyz789"
        result = scrub_sensitive(text)
        assert "abc123" not in result
        assert "xyz789" not in result

    def test_scrub_set_cookie_header(self):
        text = "Set-Cookie: auth_token=secretValue; Path=/; HttpOnly"
        result = scrub_sensitive(text)
        assert "secretValue" not in result

    def test_scrub_x_api_key_header(self):
        text = "x-api-key: my-secret-api-key-value"
        result = scrub_sensitive(text)
        assert "my-secret-api-key-value" not in result


# ── Rate-Limit Cassette Fixture Validation Tests ──


class TestRateLimitCassetteValidation:
    """Tests validating the 10-call BashTool rate-limit cassette structure."""

    @pytest.fixture()
    def rate_limit_cassette(self) -> dict:
        """Load the rate-limit cassette fixture."""
        fixture_path = Path(__file__).parent / "fixtures" / "vcr" / "bash-rate-limit-10calls.json"
        return json.loads(fixture_path.read_text())

    def test_cassette_has_10_interactions(self, rate_limit_cassette: dict):
        """Cassette contains exactly 10 interactions."""
        assert len(rate_limit_cassette["interactions"]) == 10

    def test_interaction_7_is_429(self, rate_limit_cassette: dict):
        """Interaction #7 (0-indexed: 6) returns 429 rate-limit error."""
        interaction = rate_limit_cassette["interactions"][6]
        assert interaction["response"]["status_code"] == 429

    def test_interaction_7_has_retry_after(self, rate_limit_cassette: dict):
        """429 response includes Retry-After header."""
        interaction = rate_limit_cassette["interactions"][6]
        assert "Retry-After" in interaction["response"]["headers"]
        assert interaction["response"]["headers"]["Retry-After"] == "60"

    def test_recovery_after_429(self, rate_limit_cassette: dict):
        """Interaction #8 (0-indexed: 7) returns 200 after rate-limit recovery."""
        interaction = rate_limit_cassette["interactions"][7]
        assert interaction["response"]["status_code"] == 200

    def test_all_interactions_have_scrubbed_auth(self, rate_limit_cassette: dict):
        """All interactions must have scrubbed Authorization headers."""
        for interaction in rate_limit_cassette["interactions"]:
            auth = interaction["request"]["headers"].get("Authorization", "")
            assert "Bearer [SCRUBBED]" in auth, f"Unscrubbed auth in interaction: {interaction['request'].get('url')}"

    def test_rate_limit_headers_progressive_decrease(self, rate_limit_cassette: dict):
        """X-RateLimit-Remaining decreases progressively through calls 1-6."""
        for i in range(6):
            headers = rate_limit_cassette["interactions"][i]["response"]["headers"]
            remaining = int(headers["X-RateLimit-Remaining"])
            if i > 0:
                prev_remaining = int(rate_limit_cassette["interactions"][i - 1]["response"]["headers"]["X-RateLimit-Remaining"])
                assert remaining < prev_remaining, f"Rate limit not decreasing at interaction {i + 1}"


# ── Request Fingerprinting Tests ──


class TestRequestFingerprint:
    """Tests for stable request fingerprinting."""

    def test_same_request_same_fingerprint(self):
        r1 = _make_request()
        r2 = _make_request()
        assert r1.fingerprint() == r2.fingerprint()

    def test_different_url_different_fingerprint(self):
        r1 = _make_request(url="https://api.example.com/v1/a")
        r2 = _make_request(url="https://api.example.com/v1/b")
        assert r1.fingerprint() != r2.fingerprint()

    def test_different_method_different_fingerprint(self):
        r1 = _make_request(method="GET")
        r2 = _make_request(method="POST")
        assert r1.fingerprint() != r2.fingerprint()

    def test_different_body_different_fingerprint(self):
        r1 = _make_request(body="body1")
        r2 = _make_request(body="body2")
        assert r1.fingerprint() != r2.fingerprint()

    def test_query_params_ignored(self):
        """URL query params (often containing API keys) are stripped for matching."""
        r1 = _make_request(url="https://api.example.com/v1/gen?key=abc")
        r2 = _make_request(url="https://api.example.com/v1/gen?key=xyz")
        assert r1.fingerprint() == r2.fingerprint()


# ── RecordedInteraction Serialization Tests ──


class TestRecordedInteraction:
    """Tests for interaction serialization/deserialization."""

    def test_round_trip(self):
        interaction = RecordedInteraction(
            request=_make_request(),
            response=_make_response(),
            recorded_at="2026-05-01T00:00:00Z",
        )
        data = interaction.to_dict()
        restored = RecordedInteraction.from_dict(data)
        assert restored.request.method == "POST"
        assert restored.response.status_code == 200

    def test_to_dict_scrubs_secrets(self):
        interaction = RecordedInteraction(
            request=RecordedRequest(
                method="POST",
                url="https://api.example.com/v1/gen",
                headers={"Authorization": "Bearer sk-secret123"},
                body="{}",
            ),
            response=_make_response(),
        )
        data = interaction.to_dict()
        serialized = json.dumps(data)
        assert "sk-secret123" not in serialized
        assert "[SCRUBBED]" in serialized


# ── Cassette Mode Tests ──


class TestCassette:
    """Tests for Cassette record/replay logic."""

    def test_record_mode_calls_real_api(self, tmp_path: Path):
        """RECORD mode always calls the real API."""
        fixture = tmp_path / "test.json"
        cassette = Cassette(name="test", fixture_path=fixture, mode=CassetteMode.RECORD)

        expected = _make_response(status_code=200, body='{"ok": true}')
        response = cassette.replay_or_record(
            method="POST",
            url="https://api.example.com/v1/gen",
            body='{"prompt": "test"}',
            real_caller=_fake_caller(expected),
        )

        assert response.status_code == 200
        assert cassette.interaction_count == 1

    def test_record_mode_saves_fixture(self, tmp_path: Path):
        """RECORD mode persists interactions to disk."""
        fixture = tmp_path / "test.json"
        cassette = Cassette(name="test", fixture_path=fixture, mode=CassetteMode.RECORD)

        cassette.replay_or_record(
            method="POST",
            url="https://api.example.com/v1/gen",
            body="{}",
            real_caller=_fake_caller(_make_response()),
        )
        cassette.save()

        assert fixture.exists()
        data = json.loads(fixture.read_text())
        assert len(data["interactions"]) == 1

    def test_replay_mode_returns_cached(self, tmp_path: Path):
        """REPLAY mode returns cached fixture without calling real API."""
        fixture = tmp_path / "test.json"

        # First: record
        cassette = Cassette(name="test", fixture_path=fixture, mode=CassetteMode.RECORD)
        cassette.replay_or_record(
            method="POST",
            url="https://api.example.com/v1/gen",
            body="{}",
            real_caller=_fake_caller(_make_response(body='{"cached": true}')),
        )
        cassette.save()

        # Second: replay (no real_caller needed)
        cassette2 = Cassette(name="test", fixture_path=fixture, mode=CassetteMode.REPLAY)
        response = cassette2.replay_or_record(
            method="POST",
            url="https://api.example.com/v1/gen",
            body="{}",
        )
        assert '"cached"' in response.body

    def test_replay_mode_raises_on_missing(self, tmp_path: Path):
        """REPLAY mode raises FileNotFoundError when fixture is missing."""
        fixture = tmp_path / "missing.json"
        cassette = Cassette(name="missing", fixture_path=fixture, mode=CassetteMode.REPLAY)

        with pytest.raises(FileNotFoundError, match="No recorded fixture"):
            cassette.replay_or_record(
                method="POST",
                url="https://api.example.com/v1/gen",
                body="{}",
            )

    def test_new_episodes_replays_cached(self, tmp_path: Path):
        """NEW_EPISODES mode replays from cache when available."""
        fixture = tmp_path / "test.json"

        # Record first
        c1 = Cassette(name="test", fixture_path=fixture, mode=CassetteMode.RECORD)
        c1.replay_or_record(
            method="POST",
            url="https://api.example.com/v1/gen",
            body="{}",
            real_caller=_fake_caller(_make_response(body='{"cached": true}')),
        )
        c1.save()

        # NEW_EPISODES: should replay
        call_count = 0

        def counting_caller(req: RecordedRequest) -> RecordedResponse:
            nonlocal call_count
            call_count += 1
            return _make_response(body='{"live": true}')

        c2 = Cassette(name="test", fixture_path=fixture, mode=CassetteMode.NEW_EPISODES)
        response = c2.replay_or_record(
            method="POST",
            url="https://api.example.com/v1/gen",
            body="{}",
            real_caller=counting_caller,
        )

        assert call_count == 0  # Did NOT call real API
        assert '"cached"' in response.body

    def test_new_episodes_records_new(self, tmp_path: Path):
        """NEW_EPISODES mode records when no cache exists."""
        fixture = tmp_path / "test.json"
        cassette = Cassette(name="test", fixture_path=fixture, mode=CassetteMode.NEW_EPISODES)

        response = cassette.replay_or_record(
            method="POST",
            url="https://api.example.com/v1/gen",
            body="{}",
            real_caller=_fake_caller(_make_response(body='{"new": true}')),
        )

        assert '"new"' in response.body
        assert cassette.interaction_count == 1

    def test_record_requires_real_caller(self, tmp_path: Path):
        """RECORD mode raises ValueError when no real_caller provided."""
        fixture = tmp_path / "test.json"
        cassette = Cassette(name="test", fixture_path=fixture, mode=CassetteMode.RECORD)

        with pytest.raises(ValueError, match="real_caller required"):
            cassette.replay_or_record(
                method="POST",
                url="https://api.example.com/v1/gen",
                body="{}",
            )

    def test_has_recording(self, tmp_path: Path):
        """has_recording returns True for recorded interactions."""
        fixture = tmp_path / "test.json"
        cassette = Cassette(name="test", fixture_path=fixture, mode=CassetteMode.RECORD)

        assert not cassette.has_recording(method="POST", url="https://api.example.com/v1/gen")

        cassette.replay_or_record(
            method="POST",
            url="https://api.example.com/v1/gen",
            body="{}",
            real_caller=_fake_caller(_make_response()),
        )

        assert cassette.has_recording(method="POST", url="https://api.example.com/v1/gen", body="{}")


# ── FixtureManager Tests ──


class TestFixtureManager:
    """Tests for the top-level FixtureManager factory."""

    def test_use_cassette_context_manager(self, tmp_path: Path):
        """use_cassette yields a working Cassette and saves on exit."""
        mgr = FixtureManager(
            fixture_dir=tmp_path,
            mode=CassetteMode.RECORD,
            enforce_test_gate=False,
        )

        with mgr.use_cassette("ctx_test") as cassette:
            cassette.replay_or_record(
                method="GET",
                url="https://api.example.com/v1/status",
                real_caller=_fake_caller(_make_response()),
            )

        # File should exist after context exit
        assert (tmp_path / "ctx_test.json").exists()

    def test_list_cassettes(self, tmp_path: Path):
        """list_cassettes returns names of all fixture files."""
        mgr = FixtureManager(fixture_dir=tmp_path, enforce_test_gate=False)

        # Create two cassette files
        (tmp_path / "alpha.json").write_text('{"interactions": []}')
        (tmp_path / "beta.json").write_text('{"interactions": []}')

        names = mgr.list_cassettes()
        assert names == ["alpha", "beta"]

    def test_list_cassettes_empty_dir(self, tmp_path: Path):
        """list_cassettes returns empty list when directory is empty."""
        mgr = FixtureManager(fixture_dir=tmp_path / "nonexistent", enforce_test_gate=False)
        assert mgr.list_cassettes() == []

    def test_purge_cassette(self, tmp_path: Path):
        """purge_cassette removes the fixture file."""
        mgr = FixtureManager(fixture_dir=tmp_path, enforce_test_gate=False)
        (tmp_path / "doomed.json").write_text('{"interactions": []}')

        assert mgr.purge_cassette("doomed") is True
        assert not (tmp_path / "doomed.json").exists()

    def test_purge_nonexistent_cassette(self, tmp_path: Path):
        """purge_cassette returns False for nonexistent cassette."""
        mgr = FixtureManager(fixture_dir=tmp_path, enforce_test_gate=False)
        assert mgr.purge_cassette("ghost") is False

    def test_test_gate_blocks_outside_test(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test gate returns OFF mode when not in test context."""
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        monkeypatch.delenv("NODE_ENV", raising=False)
        monkeypatch.delenv("VCR_FORCE_ENABLE", raising=False)

        mgr = FixtureManager(
            fixture_dir=tmp_path,
            mode=CassetteMode.RECORD,
            enforce_test_gate=True,
        )

        # The effective mode should be OFF outside test context
        effective = mgr._effective_mode()
        assert effective == CassetteMode.OFF

    def test_test_gate_allows_in_pytest(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test gate allows VCR when PYTEST_CURRENT_TEST is set."""
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "test_foo.py::test_bar (call)")

        mgr = FixtureManager(
            fixture_dir=tmp_path,
            mode=CassetteMode.RECORD,
            enforce_test_gate=True,
        )

        effective = mgr._effective_mode()
        assert effective == CassetteMode.RECORD

    def test_test_gate_allows_force_enable(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """Test gate allows VCR when VCR_FORCE_ENABLE is set."""
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        monkeypatch.setenv("VCR_FORCE_ENABLE", "1")

        mgr = FixtureManager(
            fixture_dir=tmp_path,
            mode=CassetteMode.NEW_EPISODES,
            enforce_test_gate=True,
        )

        effective = mgr._effective_mode()
        assert effective == CassetteMode.NEW_EPISODES


# ── Integration: Full Record → Replay Cycle ──


class TestIntegrationRecordReplay:
    """End-to-end test: record a cassette, reload, replay."""

    def test_full_cycle(self, tmp_path: Path):
        """Full VCR lifecycle: record → save → reload → replay → verify."""
        fixture_dir = tmp_path / "vcr"
        mgr = FixtureManager(
            fixture_dir=fixture_dir,
            mode=CassetteMode.RECORD,
            enforce_test_gate=False,
        )

        # Phase 1: Record
        with mgr.use_cassette("gemini_generate") as cassette:
            cassette.replay_or_record(
                method="POST",
                url="https://generativelanguage.googleapis.com/v1/models/gemini:generateContent",
                headers={"Authorization": "Bearer real-api-key-123"},
                body='{"contents": [{"parts": [{"text": "Hello"}]}]}',
                real_caller=_fake_caller(
                    RecordedResponse(
                        status_code=200,
                        body='{"candidates": [{"content": {"parts": [{"text": "Hi there!"}]}}]}',
                        elapsed_ms=150.0,
                    )
                ),
            )

        # Verify fixture was saved with scrubbed secrets
        fixture_path = fixture_dir / "gemini_generate.json"
        assert fixture_path.exists()
        fixture_data = json.loads(fixture_path.read_text())
        fixture_str = json.dumps(fixture_data)
        assert "real-api-key-123" not in fixture_str
        assert "[SCRUBBED]" in fixture_str

        # Phase 2: Replay
        mgr2 = FixtureManager(
            fixture_dir=fixture_dir,
            mode=CassetteMode.REPLAY,
            enforce_test_gate=False,
        )

        with mgr2.use_cassette("gemini_generate") as cassette:
            response = cassette.replay_or_record(
                method="POST",
                url="https://generativelanguage.googleapis.com/v1/models/gemini:generateContent",
                body='{"contents": [{"parts": [{"text": "Hello"}]}]}',
            )

        assert response.status_code == 200
        assert "Hi there!" in response.body

    def test_multi_interaction_cassette(self, tmp_path: Path):
        """A single cassette can hold multiple distinct interactions."""
        fixture_dir = tmp_path / "vcr"
        mgr = FixtureManager(
            fixture_dir=fixture_dir,
            mode=CassetteMode.RECORD,
            enforce_test_gate=False,
        )

        with mgr.use_cassette("multi") as cassette:
            # Interaction 1
            cassette.replay_or_record(
                method="POST",
                url="https://api.example.com/v1/generate",
                body='{"prompt": "hello"}',
                real_caller=_fake_caller(_make_response(body='{"text": "world"}')),
            )
            # Interaction 2 (different body)
            cassette.replay_or_record(
                method="POST",
                url="https://api.example.com/v1/generate",
                body='{"prompt": "goodbye"}',
                real_caller=_fake_caller(_make_response(body='{"text": "farewell"}')),
            )

        assert cassette.interaction_count == 2

        # Replay both
        mgr2 = FixtureManager(
            fixture_dir=fixture_dir,
            mode=CassetteMode.REPLAY,
            enforce_test_gate=False,
        )

        with mgr2.use_cassette("multi") as cassette:
            r1 = cassette.replay_or_record(
                method="POST",
                url="https://api.example.com/v1/generate",
                body='{"prompt": "hello"}',
            )
            r2 = cassette.replay_or_record(
                method="POST",
                url="https://api.example.com/v1/generate",
                body='{"prompt": "goodbye"}',
            )

        assert "world" in r1.body
        assert "farewell" in r2.body
