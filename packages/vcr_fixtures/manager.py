# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""VCR Fixture Manager — Core cassette record/replay engine.

This module provides a lightweight, zero-external-dependency VCR system for
recording and replaying HTTP API interactions during tests. It's designed
specifically for LLM API testing (Gemini, Anthropic, etc.) where:

    1. Real API calls are expensive and rate-limited
    2. Deterministic test output is required for CI
    3. API keys must never leak into fixture files

The design follows Claude Code's test cassette infrastructure pattern.

Usage::

    from vcr_fixtures import fixture_manager, CassetteMode

    # In test setup
    mgr = fixture_manager(
        fixture_dir="tests/fixtures/vcr",
        mode=CassetteMode.REPLAY,
    )

    # Record a new cassette
    with mgr.use_cassette("gemini_generate") as cassette:
        response = cassette.replay_or_record(
            method="POST",
            url="https://generativelanguage.googleapis.com/v1/models/gemini:generateContent",
            headers={"Authorization": "Bearer test-key"},
            body=b'{"contents": [{"parts": [{"text": "Hello"}]}]}',
            real_caller=lambda req: http_client.post(req.url, data=req.body),
        )
        assert response.status_code == 200

Reference: Claude Code v2.1.91 test infrastructure (VCR cassette pattern)
Reference: Reid Barber reverse engineering analysis
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any
from collections.abc import Callable, Generator

logger = logging.getLogger(__name__)


# ── Cassette Mode ──


class CassetteMode(StrEnum):
  """Operating mode for cassette playback."""

  RECORD = "record"
  """Always make real API calls and overwrite fixture files."""

  REPLAY = "replay"
  """Always use fixture files. Fail if fixture missing."""

  NEW_EPISODES = "new_episodes"
  """Use fixture if exists, record if not. Default for dev."""

  OFF = "off"
  """Bypass VCR entirely — pass through to real API."""


# ── Sensitive Key Patterns (auto-scrub) ──

_SCRUB_PATTERNS: list[tuple[re.Pattern[str], str]] = [
  # ── Bearer & Auth Tokens ──
  (re.compile(r"(Bearer\s+)[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE), r"\1[SCRUBBED]"),
  # ── API key query params ──
  (re.compile(r"(key=)[A-Za-z0-9\-._~+/]+=*"), r"\1[SCRUBBED]"),
  # ── x-goog-api-key header ──
  (re.compile(r"(x-goog-api-key:\s*)[^\s]+", re.IGNORECASE), r"\1[SCRUBBED]"),
  # ── x-api-key header (generic) ──
  (re.compile(r"(x-api-key:\s*)[^\s]+", re.IGNORECASE), r"\1[SCRUBBED]"),
  # ── Generic API key JSON fields ──
  (re.compile(r'("api_key"\s*:\s*")[^"]+(")'), r"\1[SCRUBBED]\2"),
  # ── OAuth tokens ──
  (re.compile(r'("access_token"\s*:\s*")[^"]+(")'), r"\1[SCRUBBED]\2"),
  (re.compile(r'("refresh_token"\s*:\s*")[^"]+(")'), r"\1[SCRUBBED]\2"),
  (re.compile(r'("id_token"\s*:\s*")[^"]+(")'), r"\1[SCRUBBED]\2"),
  # ── Stripe API keys (sk_live_, sk_test_, pk_live_, pk_test_, rk_live_, rk_test_, whsec_) ──
  (re.compile(r"(sk_(?:live|test)_)[A-Za-z0-9]+"), r"\1[SCRUBBED]"),
  (re.compile(r"(pk_(?:live|test)_)[A-Za-z0-9]+"), r"\1[SCRUBBED]"),
  (re.compile(r"(rk_(?:live|test)_)[A-Za-z0-9]+"), r"\1[SCRUBBED]"),
  (re.compile(r"(whsec_)[A-Za-z0-9]+"), r"whsec_[SCRUBBED]"),
  # ── GCP service account private key ──
  (re.compile(r'("private_key"\s*:\s*")[^"]+(")'), r"\1[SCRUBBED]\2"),
  (re.compile(r'("private_key_id"\s*:\s*")[^"]+(")'), r"\1[SCRUBBED]\2"),
  # ── Firebase / OIDC ID tokens (JWT format: eyJhbGci...) ──
  (re.compile(r'("idToken"\s*:\s*")[^"]+(")'), r"\1[SCRUBBED]\2"),
  # ── Password fields ──
  (re.compile(r'("password"\s*:\s*")[^"]+(")'), r"\1[SCRUBBED]\2"),
  # ── Client secrets ──
  (re.compile(r'("client_secret"\s*:\s*")[^"]+(")'), r"\1[SCRUBBED]\2"),
  # ── Session / cookie tokens ──
  (re.compile(r"(Cookie:\s*)[^\r\n]+", re.IGNORECASE), r"\1[SCRUBBED]"),
  (re.compile(r"(Set-Cookie:\s*)[^\r\n]+", re.IGNORECASE), r"\1[SCRUBBED]"),
]


def scrub_sensitive(text: str) -> str:
  """Remove API keys, tokens, and secrets from text before fixture storage.

  Applies a battery of regex patterns to strip common secret formats.
  This runs automatically on all recorded fixture data.

  Args:
      text: Raw text that may contain secrets.

  Returns:
      Sanitized text with secrets replaced by [SCRUBBED].
  """
  for pattern, replacement in _SCRUB_PATTERNS:
    text = pattern.sub(replacement, text)
  return text


# ── Data Models ──


@dataclass(frozen=True)
class RecordedRequest:
  """Captured HTTP request."""

  method: str
  url: str
  headers: dict[str, str] = field(default_factory=dict)
  body: str = ""

  def fingerprint(self) -> str:
    """Generate a stable hash for request matching.

    Uses method + URL path + sorted body hash for deterministic matching.
    Query parameters with API keys are excluded via scrubbing.
    """
    # Normalize URL by removing query params (they may contain keys)
    url_base = self.url.split("?")[0]
    body_hash = hashlib.sha256(self.body.encode()).hexdigest()[:16]
    key = f"{self.method}:{url_base}:{body_hash}"
    return hashlib.sha256(key.encode()).hexdigest()[:32]


@dataclass(frozen=True)
class RecordedResponse:
  """Captured HTTP response."""

  status_code: int
  headers: dict[str, str] = field(default_factory=dict)
  body: str = ""
  elapsed_ms: float = 0.0


@dataclass
class RecordedInteraction:
  """A single request-response pair (one VCR 'episode')."""

  request: RecordedRequest
  response: RecordedResponse
  recorded_at: str = ""
  cassette_version: int = 1

  def to_dict(self) -> dict[str, Any]:
    """Serialize to a JSON-safe dictionary with scrubbed secrets."""
    raw = asdict(self)
    # Scrub secrets from serialized form
    raw_str = json.dumps(raw)
    scrubbed_str = scrub_sensitive(raw_str)
    return json.loads(scrubbed_str)

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> RecordedInteraction:
    """Deserialize from a dictionary (fixture file)."""
    return cls(
      request=RecordedRequest(**data["request"]),
      response=RecordedResponse(**data["response"]),
      recorded_at=data.get("recorded_at", ""),
      cassette_version=data.get("cassette_version", 1),
    )


# ── Cassette (single fixture file) ──


class Cassette:
  """A named collection of recorded interactions (one fixture file).

  Each cassette maps to a single JSON file in the fixtures directory.
  Multiple interactions can be stored per cassette, keyed by request fingerprint.
  """

  def __init__(
    self,
    name: str,
    fixture_path: Path,
    mode: CassetteMode,
  ) -> None:
    self.name = name
    self.fixture_path = fixture_path
    self.mode = mode
    self._interactions: dict[str, RecordedInteraction] = {}
    self._dirty = False
    self._load()

  def _load(self) -> None:
    """Load interactions from fixture file if it exists."""
    if self.fixture_path.exists():
      try:
        data = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        for interaction_data in data.get("interactions", []):
          interaction = RecordedInteraction.from_dict(interaction_data)
          fp = interaction.request.fingerprint()
          self._interactions[fp] = interaction
        logger.debug(
          "Loaded %d interactions from %s",
          len(self._interactions),
          self.fixture_path,
        )
      except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("Failed to load cassette %s: %s", self.name, exc)
        self._interactions = {}

  def save(self) -> None:
    """Persist interactions to fixture file (with scrubbed secrets)."""
    if not self._dirty:
      return

    self.fixture_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
      "cassette_name": self.name,
      "cassette_version": 1,
      "interactions": [i.to_dict() for i in self._interactions.values()],
    }
    self.fixture_path.write_text(
      json.dumps(data, indent=2, sort_keys=True),
      encoding="utf-8",
    )
    logger.info(
      "Saved cassette %s with %d interactions", self.name, len(self._interactions)
    )
    self._dirty = False

  def replay_or_record(
    self,
    *,
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    body: str = "",
    real_caller: Callable[[RecordedRequest], RecordedResponse] | None = None,
  ) -> RecordedResponse:
    """Replay a recorded response or record a new one.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Full request URL
        headers: Request headers
        body: Request body
        real_caller: Callable that makes the actual API call.
                     Required in RECORD and NEW_EPISODES mode.

    Returns:
        RecordedResponse from fixture or live API.

    Raises:
        FileNotFoundError: In REPLAY mode when no fixture exists.
        ValueError: In RECORD/NEW_EPISODES mode when no real_caller provided.
    """
    request = RecordedRequest(
      method=method,
      url=url,
      headers=headers or {},
      body=body,
    )
    fp = request.fingerprint()

    # ── REPLAY: return cached fixture ──
    if self.mode == CassetteMode.REPLAY:
      if fp in self._interactions:
        logger.debug("VCR REPLAY: %s %s", method, url)
        return self._interactions[fp].response
      msg = f"No recorded fixture for {method} {url} in cassette '{self.name}'. Re-record with mode=NEW_EPISODES or RECORD."
      raise FileNotFoundError(msg)

    # ── NEW_EPISODES: replay if cached, record if not ──
    if self.mode == CassetteMode.NEW_EPISODES and fp in self._interactions:
      logger.debug("VCR REPLAY (cached): %s %s", method, url)
      return self._interactions[fp].response

    # ── RECORD or NEW_EPISODES (miss): make real call ──
    if self.mode in (CassetteMode.RECORD, CassetteMode.NEW_EPISODES):
      if real_caller is None:
        msg = f"real_caller required in {self.mode} mode"
        raise ValueError(msg)

      logger.info("VCR RECORD: %s %s", method, url)
      start = time.monotonic()
      response = real_caller(request)
      elapsed = (time.monotonic() - start) * 1000

      # Override elapsed with measured value
      response = RecordedResponse(
        status_code=response.status_code,
        headers=response.headers,
        body=response.body,
        elapsed_ms=elapsed,
      )

      interaction = RecordedInteraction(
        request=request,
        response=response,
        recorded_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
      )
      self._interactions[fp] = interaction
      self._dirty = True
      return response

    # ── OFF mode: must have real_caller ──
    if real_caller is None:
      msg = "real_caller required in OFF mode"
      raise ValueError(msg)
    return real_caller(request)

  @property
  def interaction_count(self) -> int:
    """Number of recorded interactions in this cassette."""
    return len(self._interactions)

  def has_recording(self, *, method: str, url: str, body: str = "") -> bool:
    """Check if a specific request has been recorded."""
    request = RecordedRequest(method=method, url=url, body=body)
    return request.fingerprint() in self._interactions


# ── VCR Context Manager ──


class VCRContext:
  """Context manager for a VCR cassette session.

  Automatically saves the cassette on exit (if dirty).
  """

  def __init__(self, cassette: Cassette) -> None:
    self.cassette = cassette

  def __enter__(self) -> Cassette:
    return self.cassette

  def __exit__(
    self, exc_type: type | None, exc_val: BaseException | None, exc_tb: Any
  ) -> None:
    if exc_type is None:
      self.cassette.save()


# ── Fixture Manager (top-level factory) ──


class FixtureManager:
  """Factory for VCR cassettes.

  Manages the fixture directory and provides cassette creation/retrieval.
  Enforces the test-only gate: VCR features are disabled outside test context.

  Args:
      fixture_dir: Path to the fixtures directory (default: tests/fixtures/vcr).
      mode: Default cassette mode. Overridable per-cassette.
      enforce_test_gate: If True (default), VCR only activates when
                        PYTEST_CURRENT_TEST or NODE_ENV=test is set.
  """

  def __init__(
    self,
    fixture_dir: str | Path = "tests/fixtures/vcr",
    mode: CassetteMode = CassetteMode.NEW_EPISODES,
    *,
    enforce_test_gate: bool = True,
  ) -> None:
    self.fixture_dir = Path(fixture_dir)
    self.default_mode = mode
    self.enforce_test_gate = enforce_test_gate

  def _is_test_context(self) -> bool:
    """Check if we're running in a test environment."""
    if os.environ.get("PYTEST_CURRENT_TEST"):
      return True
    if os.environ.get("NODE_ENV") == "test":
      return True
    return bool(os.environ.get("VCR_FORCE_ENABLE"))

  def _effective_mode(self, mode: CassetteMode | None = None) -> CassetteMode:
    """Resolve the effective mode, respecting the test gate."""
    resolved = mode or self.default_mode

    if self.enforce_test_gate and not self._is_test_context():
      logger.warning(
        "VCR disabled outside test context. Set PYTEST_CURRENT_TEST or VCR_FORCE_ENABLE."
      )
      return CassetteMode.OFF

    return resolved

  @contextmanager
  def use_cassette(
    self,
    name: str,
    *,
    mode: CassetteMode | None = None,
  ) -> Generator[Cassette]:
    """Open a named cassette for recording or replay.

    Args:
        name: Cassette name (becomes the fixture filename without extension).
        mode: Override the default mode for this cassette.

    Yields:
        A Cassette instance for recording/replaying interactions.
    """
    effective_mode = self._effective_mode(mode)
    fixture_path = self.fixture_dir / f"{name}.json"
    cassette = Cassette(name=name, fixture_path=fixture_path, mode=effective_mode)

    ctx = VCRContext(cassette)
    with ctx as c:
      yield c

  def list_cassettes(self) -> list[str]:
    """List all available cassette names in the fixture directory."""
    if not self.fixture_dir.exists():
      return []
    return sorted(p.stem for p in self.fixture_dir.glob("*.json"))

  def cassette_path(self, name: str) -> Path:
    """Get the file path for a named cassette."""
    return self.fixture_dir / f"{name}.json"

  def purge_cassette(self, name: str) -> bool:
    """Delete a cassette fixture file. Returns True if file existed.

    Note: This is the ONLY deletion path in VCR fixtures.
    Cassette files are test data, not production infrastructure.
    """
    path = self.cassette_path(name)
    if path.exists():
      path.unlink()
      logger.info("Purged cassette: %s", name)
      return True
    return False


# ── Module-level factory ──


def fixture_manager(
  fixture_dir: str | Path = "tests/fixtures/vcr",
  mode: CassetteMode = CassetteMode.NEW_EPISODES,
  *,
  enforce_test_gate: bool = True,
) -> FixtureManager:
  """Create a configured FixtureManager instance.

  This is the primary entry point for VCR fixture management.

  Args:
      fixture_dir: Path to fixtures directory.
      mode: Default cassette mode.
      enforce_test_gate: Whether to enforce test-only activation.

  Returns:
      Configured FixtureManager instance.
  """
  return FixtureManager(
    fixture_dir=fixture_dir,
    mode=mode,
    enforce_test_gate=enforce_test_gate,
  )
