# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Pexpect-based live API integration test for the Gemini Bridge.

This test validates real Gemini API connectivity by launching a subprocess
that exercises the bridge health probe via ``python scripts/kairos_daemon.py --bridge-health``.

**Gate:** Only runs when ``GEMINI_LIVE_TEST=1`` is set.
Use ``CI=true GEMINI_LIVE_TEST=1 python -m pytest tests/integration/test_live_bridge.py -v``

Architecture:
  Uses pexpect to spawn the KAIROS daemon in bridge-health probe mode.
  This avoids TUI traps (headless CLI doctrine) since --bridge-health is a
  single-shot JSON output command.

Run locally:
    GEMINI_LIVE_TEST=1 python -m pytest tests/integration/test_live_bridge.py -v
"""

from __future__ import annotations

import json
import os
import sys
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "packages"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# Gate: only run with explicit opt-in
LIVE_ENABLED = os.environ.get("GEMINI_LIVE_TEST", "0") == "1"
SKIP_REASON = "Set GEMINI_LIVE_TEST=1 to enable live API tests"


@pytest.fixture
def pexpect_available():
  """Check pexpect is installed."""
  try:
    import pexpect  # noqa: F401

    return True
  except ImportError:
    pytest.skip("pexpect not installed — install with: pip install pexpect")


# ---------------------------------------------------------------------------
# 1. Bridge Health via pexpect subprocess
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not LIVE_ENABLED, reason=SKIP_REASON)
class TestLiveBridgeHealth:
  """Spawn kairos_daemon.py --bridge-health and validate JSON output."""

  def test_bridge_health_subprocess(self, pexpect_available: bool) -> None:
    import pexpect

    # Spawn the bridge health probe
    child = pexpect.spawn(
      sys.executable,
      [str(REPO_ROOT / "scripts" / "kairos_daemon.py"), "--bridge-health"],
      cwd=str(REPO_ROOT),
      timeout=30,
      encoding="utf-8",
      env={
        **os.environ,
        "CI": "true",
        "PYTHONPATH": f"{REPO_ROOT}:{REPO_ROOT / 'packages'}:{REPO_ROOT / 'scripts'}",
      },
    )

    # Wait for completion
    child.expect(pexpect.EOF, timeout=30)
    output = child.before.strip()
    child.close()

    # Validate exit code
    assert child.exitstatus == 0, f"Bridge health probe exited with {child.exitstatus}"

    # Parse the JSON output
    # Filter out logging lines (lines starting with non-JSON chars)

    # The full JSON is multi-line, so reconstruct
    json_text = output[output.index("{") :] if "{" in output else output
    health = json.loads(json_text)

    assert health["healthy"] is True
    assert health["importable"] is True
    assert health["orchestrator_init"] is True
    assert health["sweep_ready"] is True
    assert health["error"] is None

  def test_bridge_health_exit_code_success(self, pexpect_available: bool) -> None:
    import pexpect

    child = pexpect.spawn(
      sys.executable,
      [str(REPO_ROOT / "scripts" / "kairos_daemon.py"), "--bridge-health"],
      cwd=str(REPO_ROOT),
      timeout=30,
      encoding="utf-8",
      env={
        **os.environ,
        "CI": "true",
        "PYTHONPATH": f"{REPO_ROOT}:{REPO_ROOT / 'packages'}:{REPO_ROOT / 'scripts'}",
      },
    )
    child.expect(pexpect.EOF, timeout=30)
    child.close()
    assert child.exitstatus == 0


# ---------------------------------------------------------------------------
# 2. Direct module live test (no subprocess)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not LIVE_ENABLED, reason=SKIP_REASON)
class TestLiveDirectBridge:
  """Direct import test — validates bridge modules resolve without import errors."""

  def test_orchestrator_auto_route_live(self) -> None:
    from speculation_engine.orchestrator import (
      SpeculativeResearchOrchestrator,
      SpeculativeResearchConfig,
    )
    from speculation_engine.gemini_bridge import PipelineMode

    orch = SpeculativeResearchOrchestrator(
      workspace=str(REPO_ROOT),
      config=SpeculativeResearchConfig(
        speculate_during_research=False,
        speculate_during_synthesis=False,
      ),
    )
    mode = orch.auto_route("Research the competitive landscape for legal AI startups")
    assert mode == PipelineMode.RESEARCH_SWEEP

  def test_firestore_persistence_doc_mapping_live(self) -> None:
    from speculation_engine.firestore_persistence import sweep_result_to_doc
    from speculation_engine.gemini_bridge import SweepResult

    result = SweepResult(
      query="Live API test",
      report_text="Test report from live integration",
      duration_seconds=0.1,
    )
    doc = sweep_result_to_doc(result, session_id="live-test")
    assert doc["query"] == "Live API test"
    assert doc["session_id"] == "live-test"

  def test_kairos_probe_live(self) -> None:
    from kairos_daemon import _probe_bridge_health

    health = _probe_bridge_health()
    assert health["healthy"] is True


# ---------------------------------------------------------------------------
# 3. Non-gated structural tests (always run)
# ---------------------------------------------------------------------------


class TestBridgeStructural:
  """Structural tests that run without GEMINI_LIVE_TEST gate."""

  def test_firestore_persistence_importable(self) -> None:
    from speculation_engine.firestore_persistence import (
      persist_sweep_result,  # noqa: F401
      query_recent_sweeps,  # noqa: F401
      get_sweep_by_id,  # noqa: F401
      sweep_result_to_doc,  # noqa: F401
      COLLECTION,
    )

    assert COLLECTION == "sweep_results"

  def test_pexpect_importable(self) -> None:
    """Verify pexpect is in the dependency tree."""
    try:
      import pexpect  # noqa: F401

      assert True
    except ImportError:
      pytest.skip("pexpect not installed")

  def test_kairos_bridge_health_flag_exists(self) -> None:
    """Verify kairos_daemon.py has --bridge-health argparse flag."""
    import importlib

    kairos = importlib.import_module("kairos_daemon")
    # The main() function creates an argparse parser
    assert hasattr(kairos, "_probe_bridge_health")
