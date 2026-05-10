"""ROC Drill — gVisor Sand Table (Rehearsal of Concept).

JP 3-33 mandates that no operation proceeds without a Combined Arms
Rehearsal (CAR). A unit test checks if code compiles. A ROC Drill
wargames the execution phase-by-phase on a Sand Table to ensure
synchronization and zero fratricide.

The gVisor sandbox (runsc) provides:
    - Syscall-level isolation (no host kernel escape)
    - No network access during rehearsal
    - Read-only filesystem mounts
    - UCMJ Article 92 timeout enforcement
"""

from __future__ import annotations

import logging
import subprocess

from temporalio import activity

logger = logging.getLogger("J3-ROC-Drill")

# UCMJ Article 92 timeout: agents that hang are court-martialed
_ROC_DRILL_TIMEOUT_SECONDS = 120


@activity.defn(name="j3_roc_drill_sandbox")
async def j3_roc_drill_sandbox(artifact: dict) -> dict:
  """Execute the ROC Drill in a gVisor-secured sandbox.

  Runs the complete test suite against the generated artifact
  inside a gVisor container. No network. No escape. If tests
  fail or timeout, the artifact is rejected.

  Args:
      artifact: The generated artifact to rehearse.

  Returns:
      Dict with passed status, logs, and fratricide indicators.
  """
  logger.info("🗺️ INITIATING ROC DRILL IN gVISOR SANDBOX")

  cmd = [
    "docker",
    "run",
    "--runtime=runsc",
    "--rm",
    "--network=none",
    "--read-only",
    "--tmpfs=/tmp:rw,noexec,nosuid",
    "-v",
    "$(pwd)/patch:/workspace:ro",
    "shadowtag-tester:latest",
    "pytest",
    "/workspace",
    "-v",
    "--tb=short",
  ]

  try:
    result = subprocess.run(
      " ".join(cmd),
      shell=True,
      capture_output=True,
      text=True,
      timeout=_ROC_DRILL_TIMEOUT_SECONDS,
    )

    if result.returncode != 0:
      logger.warning(
        "❌ ROC DRILL FAILED. Fratricide detected.\n%s",
        result.stderr[:500],
      )
      return {
        "passed": False,
        "fratricide_detected": True,
        "logs": result.stderr[:2000],
        "directive": "KICKBACK_TO_J3",
      }

    logger.info("✅ ROC DRILL PASSED. Zero fratricide. Deploy authorized.")
    return {
      "passed": True,
      "fratricide_detected": False,
      "logs": result.stdout[:2000],
      "directive": "PROCEED_TO_SUSTAINING_OPS",
    }

  except subprocess.TimeoutExpired:
    logger.critical(
      "⏰ UCMJ ARTICLE 92: ROC Drill timed out (%ds). Agent court-martialed.",
      _ROC_DRILL_TIMEOUT_SECONDS,
    )
    return {
      "passed": False,
      "fratricide_detected": True,
      "logs": f"UCMJ ART 92: TIMEOUT after {_ROC_DRILL_TIMEOUT_SECONDS}s",
      "directive": "REPLACE_AGENT",
    }
  except FileNotFoundError:
    logger.error("Docker/gVisor runtime not available for ROC Drill.")
    return {
      "passed": False,
      "fratricide_detected": False,
      "logs": "gVisor runtime not available. Falling back to direct pytest.",
      "directive": "FALLBACK_DIRECT_TEST",
    }
