# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Property-based tests for AsyncVCR cassette serialization.

Uses Hypothesis to fuzz cassette edge cases:
- Hash determinism: same input → same hash
- Roundtrip integrity: record → replay returns identical data
- Stale rotation: expired cassettes are correctly purged
- Secret sanitization: sensitive keys never leak to disk
- Index persistence: index survives save/load cycles
- Concurrent safety: parallel async_intercept calls don't corrupt state
"""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
import time

import pytest
from hypothesis import given, settings, assume, HealthCheck
from hypothesis import strategies as st

from packages.agnt_vcr.vcr import VCRReplay
from packages.agnt_vcr.async_vcr import AsyncVCR


# ─── Fuzz Multiplier (env-driven) ─────────────────────────────────────
# Set HYPOTHESIS_FUZZ_MULTIPLIER=10 to run 10x more examples.
# Default is 1 (standard CI). Use 5-10 for extended fuzzing sessions.
_FUZZ_MULT = int(os.environ.get("HYPOTHESIS_FUZZ_MULTIPLIER", "1"))


# ─── Strategies ────────────────────────────────────────────────────────

# JSON-serializable values (no NaN/Inf which break JSON roundtrip)
json_primitives = st.one_of(
  st.none(),
  st.booleans(),
  st.integers(min_value=-(2**53), max_value=2**53),
  st.floats(allow_nan=False, allow_infinity=False),
  st.text(max_size=200),
)

json_values = st.recursive(
  json_primitives,
  lambda children: st.one_of(
    st.lists(children, max_size=5),
    st.dictionaries(st.text(min_size=1, max_size=20), children, max_size=5),
  ),
  max_leaves=15,
)

method_names = st.text(
  alphabet=st.characters(whitelist_categories=("L", "N"), whitelist_characters="_-."),
  min_size=1,
  max_size=50,
)

kwargs_strategy = st.dictionaries(
  st.text(min_size=1, max_size=30),
  json_values,
  max_size=10,
)

# Secret key names that must be redacted
SECRET_KEYS = frozenset({"token", "api_key", "password", "secret", "authorization"})

# Common health check suppressions for tests using fixtures + Hypothesis
_FIXTURE_HC = [HealthCheck.too_slow, HealthCheck.function_scoped_fixture]


# ─── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture()
def vcr_dir(tmp_path):
  """Provide a fresh cassette directory."""
  d = tmp_path / "cassettes"
  d.mkdir()
  return str(d)


# ─── Property: Hash Determinism ───────────────────────────────────────


class TestHashDeterminism:
  """_hash_request must be pure: same inputs → same hash."""

  @given(method=method_names, kwargs=kwargs_strategy)
  @settings(max_examples=200 * _FUZZ_MULT, suppress_health_check=[HealthCheck.too_slow])
  def test_same_input_same_hash(self, method, kwargs):
    """Identical method+kwargs always produce the same hash."""
    vcr = VCRReplay.__new__(VCRReplay)
    vcr.cassette_dir = "/dev/null"
    vcr.recording = False
    vcr.replaying = False
    h1 = vcr._hash_request(method, kwargs)
    h2 = vcr._hash_request(method, kwargs)
    assert h1 == h2, "Hash must be deterministic"

  @given(
    method=method_names,
    kwargs_a=kwargs_strategy,
    kwargs_b=kwargs_strategy,
  )
  @settings(max_examples=200 * _FUZZ_MULT, suppress_health_check=[HealthCheck.too_slow])
  def test_different_kwargs_different_hash(self, method, kwargs_a, kwargs_b):
    """Different kwargs should (almost always) produce different hashes."""
    assume(kwargs_a != kwargs_b)
    vcr = VCRReplay.__new__(VCRReplay)
    vcr.cassette_dir = "/dev/null"
    vcr.recording = False
    vcr.replaying = False
    h1 = vcr._hash_request(method, kwargs_a)
    h2 = vcr._hash_request(method, kwargs_b)
    # SHA-256 collision is astronomically unlikely
    assert h1 != h2, "Different inputs must produce different hashes"


# ─── Property: Cassette Roundtrip Integrity ───────────────────────────


class TestCassetteRoundtrip:
  """Record → replay must return identical JSON-serializable data."""

  @given(method=method_names, kwargs=kwargs_strategy, response=json_values)
  @settings(max_examples=100 * _FUZZ_MULT, suppress_health_check=_FIXTURE_HC)
  def test_record_then_replay(self, method, kwargs, response, vcr_dir, monkeypatch):
    """Recording a response and replaying it yields the exact same value."""
    # Record phase
    monkeypatch.setenv("AGNT_FC_OVERRIDES", json.dumps({"vcr_mode": "record"}))
    recorder = VCRReplay(cassette_dir=vcr_dir)

    recorded = recorder.intercept(method, kwargs, lambda: response)
    assert recorded == response

    # Replay phase — fresh VCR instance
    monkeypatch.setenv("AGNT_FC_OVERRIDES", json.dumps({"vcr_mode": "replay"}))
    replayer = VCRReplay(cassette_dir=vcr_dir)

    replayed = replayer.intercept(
      method,
      kwargs,
      lambda: pytest.fail("execute_fn should not be called in replay"),
    )
    assert replayed == response, "Replay must match recorded response exactly"


# ─── Property: Secret Sanitization ────────────────────────────────────


class TestSecretSanitization:
  """Sensitive keys must NEVER appear in cassette files."""

  @given(
    method=method_names,
    secret_key=st.sampled_from(sorted(SECRET_KEYS)),
    secret_value=st.text(min_size=8, max_size=100),
  )
  @settings(max_examples=50 * _FUZZ_MULT, suppress_health_check=_FIXTURE_HC)
  def test_secrets_redacted_in_cassette(
    self, method, secret_key, secret_value, vcr_dir, monkeypatch
  ):
    """Secret values must be [REDACTED] in cassette JSON on disk."""
    monkeypatch.setenv("AGNT_FC_OVERRIDES", json.dumps({"vcr_mode": "record"}))
    recorder = VCRReplay(cassette_dir=vcr_dir)

    kwargs = {secret_key: secret_value, "safe_key": "safe_value"}
    recorder.intercept(method, kwargs, lambda: {"ok": True})

    # Structurally verify: parse the cassette JSON and check the field value
    for fname in os.listdir(vcr_dir):
      if not fname.endswith(".json"):
        continue
      with open(os.path.join(vcr_dir, fname), encoding="utf-8") as f:
        data = json.load(f)
      req_kwargs = data.get("request", {}).get("kwargs", {})
      if secret_key in req_kwargs:
        assert req_kwargs[secret_key] == "[REDACTED]", (
          f"Secret key {secret_key!r} was not redacted: got {req_kwargs[secret_key]!r}"
        )

  @given(
    method=method_names,
    auth_header=st.text(min_size=1, max_size=100),
  )
  @settings(max_examples=30 * _FUZZ_MULT, suppress_health_check=_FIXTURE_HC)
  def test_authorization_header_redacted(
    self, method, auth_header, vcr_dir, monkeypatch
  ):
    """Authorization header in nested headers dict must be redacted."""
    monkeypatch.setenv("AGNT_FC_OVERRIDES", json.dumps({"vcr_mode": "record"}))
    recorder = VCRReplay(cassette_dir=vcr_dir)

    kwargs = {"headers": {"Authorization": auth_header}, "body": "test"}
    recorder.intercept(method, kwargs, lambda: {"ok": True})

    for fname in os.listdir(vcr_dir):
      if not fname.endswith(".json"):
        continue
      with open(os.path.join(vcr_dir, fname), encoding="utf-8") as f:
        data = json.load(f)
      req_headers = data.get("request", {}).get("kwargs", {}).get("headers", {})
      if "Authorization" in req_headers:
        assert req_headers["Authorization"] == "[REDACTED]"


# ─── Property: Stale Rotation ─────────────────────────────────────────


class TestStaleRotation:
  """Expired cassettes must be correctly identified and purged."""

  @given(
    methods=st.lists(method_names, min_size=1, max_size=5),
  )
  @settings(max_examples=30 * _FUZZ_MULT, suppress_health_check=_FIXTURE_HC)
  def test_fresh_cassettes_not_rotated(self, methods, monkeypatch):
    """Cassettes recorded within max_age_s must NOT be purged."""
    # Each Hypothesis example gets its own isolated directory
    with tempfile.TemporaryDirectory() as td:
      iso_dir = os.path.join(td, "cassettes")
      os.makedirs(iso_dir)

      monkeypatch.setenv("AGNT_FC_OVERRIDES", json.dumps({"vcr_mode": "record"}))
      vcr = AsyncVCR(cassette_dir=iso_dir, max_age_s=3600.0)  # 1 hour

      async def _record():
        for m in methods:
          await vcr.async_intercept(m, {"i": m}, lambda: {"result": m})

      asyncio.run(_record())

      rotated = vcr.rotate_stale()
      assert rotated == 0, f"Expected 0 rotated, got {rotated}"
      assert vcr.cassette_count() == len(set(methods))

  def test_stale_cassettes_rotated(self, vcr_dir, monkeypatch):
    """Cassettes older than max_age_s must be purged by rotate_stale()."""
    monkeypatch.setenv("AGNT_FC_OVERRIDES", json.dumps({"vcr_mode": "record"}))
    vcr = AsyncVCR(cassette_dir=vcr_dir, max_age_s=0.01)  # 10ms

    async def _record():
      await vcr.async_intercept("stale_method", {"x": 1}, lambda: {"y": 2})

    asyncio.run(_record())
    assert vcr.cassette_count() == 1

    # Wait for expiry
    time.sleep(0.05)

    rotated = vcr.rotate_stale()
    assert rotated == 1
    assert vcr.cassette_count() == 0


# ─── Property: Index Persistence ──────────────────────────────────────


class TestIndexPersistence:
  """Cassette index must survive save/load cycles."""

  @given(
    methods=st.lists(method_names, min_size=1, max_size=8, unique=True),
  )
  @settings(max_examples=30 * _FUZZ_MULT, suppress_health_check=_FIXTURE_HC)
  def test_index_roundtrip(self, methods, monkeypatch):
    """Save → load → same index keys."""
    with tempfile.TemporaryDirectory() as td:
      iso_dir = os.path.join(td, "cassettes")
      os.makedirs(iso_dir)

      monkeypatch.setenv("AGNT_FC_OVERRIDES", json.dumps({"vcr_mode": "record"}))
      vcr1 = AsyncVCR(cassette_dir=iso_dir, max_age_s=3600.0)

      async def _record():
        for m in methods:
          await vcr1.async_intercept(m, {}, lambda: {"r": m})

      asyncio.run(_record())

      original_count = vcr1.cassette_count()
      original_keys = set(vcr1._index.keys())

      # Recreate from same directory — should load persisted index
      vcr2 = AsyncVCR(cassette_dir=iso_dir, max_age_s=3600.0)
      assert vcr2.cassette_count() == original_count
      assert set(vcr2._index.keys()) == original_keys


# ─── Property: Cassette Stats Consistency ─────────────────────────────


class TestCassetteStats:
  """cassette_stats() invariants must hold."""

  @given(
    n_fresh=st.integers(min_value=0, max_value=5),
  )
  @settings(max_examples=20 * _FUZZ_MULT, suppress_health_check=_FIXTURE_HC)
  def test_stats_arithmetic(self, n_fresh, monkeypatch):
    """total = fresh + stale must always hold."""
    with tempfile.TemporaryDirectory() as td:
      iso_dir = os.path.join(td, "cassettes")
      os.makedirs(iso_dir)

      monkeypatch.setenv("AGNT_FC_OVERRIDES", json.dumps({"vcr_mode": "record"}))
      vcr = AsyncVCR(cassette_dir=iso_dir, max_age_s=3600.0)

      async def _record():
        for i in range(n_fresh):
          await vcr.async_intercept(f"method_{i}", {"i": i}, lambda: {"r": i})

      asyncio.run(_record())

      stats = vcr.cassette_stats()
      assert (
        stats["total_cassettes"] == stats["fresh_cassettes"] + stats["stale_cassettes"]
      )
      assert stats["total_cassettes"] == n_fresh
      assert stats["max_age_s"] == 3600.0


# ─── Property: Async Concurrent Safety ────────────────────────────────


class TestConcurrentSafety:
  """Concurrent async_intercept calls must not corrupt the index."""

  def test_parallel_records_consistent(self, vcr_dir, monkeypatch):
    """Parallel async_intercept calls produce correct cassette count."""
    monkeypatch.setenv("AGNT_FC_OVERRIDES", json.dumps({"vcr_mode": "record"}))
    vcr = AsyncVCR(cassette_dir=vcr_dir, max_age_s=3600.0)
    n_tasks = 20

    async def _record_one(i: int):
      await vcr.async_intercept(f"concurrent_{i}", {"idx": i}, lambda: {"v": i})

    async def _main():
      tasks = [_record_one(i) for i in range(n_tasks)]
      await asyncio.gather(*tasks)

    asyncio.run(_main())

    assert vcr.cassette_count() == n_tasks
    stats = vcr.cassette_stats()
    assert stats["total_cassettes"] == n_tasks
    assert stats["stale_cassettes"] == 0
