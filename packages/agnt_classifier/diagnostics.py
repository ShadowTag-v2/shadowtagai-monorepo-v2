# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Classifier Diagnostics — Health checks for the AGNT classifier subsystem.

Ported from Claude Code's Doctor.tsx diagnostic pattern. Provides structured
health checks for the classifier, MCP policy, and gateway components.

Usage::

    diag = ClassifierDiagnostics()
    report = diag.run_all()
    for check in report:
        print(f"{check.name}: {check.status} — {check.message}")

Reference: Claude Code v2.1.91 Doctor.tsx
Reference: AGNT STATE B Spec P6.1
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class DiagnosticStatus(StrEnum):
  """Status of a diagnostic check."""

  PASS = "pass"
  WARN = "warn"
  FAIL = "fail"
  SKIP = "skip"


@dataclass(frozen=True)
class DiagnosticCheck:
  """A single diagnostic check result."""

  name: str
  status: DiagnosticStatus
  message: str
  duration_ms: float = 0.0
  details: dict[str, Any] = field(default_factory=dict)


class ClassifierDiagnostics:
  """Diagnostic suite for the AGNT classifier subsystem.

  Checks:
      1. Classifier instantiation and basic function
      2. Allowlist configuration sanity
      3. MCP policy configuration
      4. Gateway pipeline end-to-end
      5. Telemetry emission
  """

  def run_all(self) -> list[DiagnosticCheck]:
    """Run all diagnostic checks and return results."""
    checks: list[DiagnosticCheck] = [
      self._check_classifier_import(),
      self._check_classifier_function(),
      self._check_allowlist_sanity(),
      self._check_policy_config(),
      self._check_gateway_pipeline(),
      self._check_telemetry_catalog(),
    ]
    return checks

  def _check_classifier_import(self) -> DiagnosticCheck:
    """Check that all classifier modules import correctly."""
    start = time.perf_counter()
    try:
      from agnt_classifier import (  # noqa: F401
        AGNTClassifier,  # noqa: F401
        ClassifierResult,  # noqa: F401
        ClassifierVerdict,  # noqa: F401
        TwoStageClassifier,  # noqa: F401
        XMLClassifier,  # noqa: F401
      )

      duration = (time.perf_counter() - start) * 1000
      return DiagnosticCheck(
        name="classifier_import",
        status=DiagnosticStatus.PASS,
        message="All classifier modules imported successfully.",
        duration_ms=duration,
        details={
          "modules": [
            "AGNTClassifier",
            "ClassifierResult",
            "ClassifierVerdict",
            "TwoStageClassifier",
            "XMLClassifier",
          ]
        },
      )
    except ImportError as e:
      duration = (time.perf_counter() - start) * 1000
      return DiagnosticCheck(
        name="classifier_import",
        status=DiagnosticStatus.FAIL,
        message=f"Import failed: {e}",
        duration_ms=duration,
      )

  def _check_classifier_function(self) -> DiagnosticCheck:
    """Check that classifier produces correct verdicts for known inputs."""
    start = time.perf_counter()
    try:
      from agnt_classifier import AGNTClassifier, ClassifierVerdict

      classifier = AGNTClassifier()

      # Test allowlisted tool
      safe_result = classifier.classify(tool_id="view_file")
      if safe_result.verdict != ClassifierVerdict.ALLOW:
        duration = (time.perf_counter() - start) * 1000
        return DiagnosticCheck(
          name="classifier_function",
          status=DiagnosticStatus.FAIL,
          message=f"Allowlisted tool 'view_file' got verdict {safe_result.verdict}",
          duration_ms=duration,
        )

      # Test known-safe command
      echo_result = classifier.classify(
        tool_id="run_command",
        tool_input={"CommandLine": "echo hello"},
      )

      # Test known-dangerous command
      rm_result = classifier.classify(
        tool_id="run_command",
        tool_input={"CommandLine": "rm -rf /"},
      )
      if rm_result.verdict == ClassifierVerdict.ALLOW:
        duration = (time.perf_counter() - start) * 1000
        return DiagnosticCheck(
          name="classifier_function",
          status=DiagnosticStatus.FAIL,
          message="Dangerous command 'rm -rf /' was ALLOWED!",
          duration_ms=duration,
        )

      duration = (time.perf_counter() - start) * 1000
      return DiagnosticCheck(
        name="classifier_function",
        status=DiagnosticStatus.PASS,
        message="Classifier produces correct verdicts for test cases.",
        duration_ms=duration,
        details={
          "safe_tool_verdict": str(safe_result.verdict),
          "echo_verdict": str(echo_result.verdict),
          "rm_verdict": str(rm_result.verdict),
        },
      )
    except Exception as e:
      duration = (time.perf_counter() - start) * 1000
      return DiagnosticCheck(
        name="classifier_function",
        status=DiagnosticStatus.FAIL,
        message=f"Classifier function check failed: {e}",
        duration_ms=duration,
      )

  def _check_allowlist_sanity(self) -> DiagnosticCheck:
    """Check that the allowlist contains expected tools and no dangerous ones."""
    start = time.perf_counter()
    try:
      from agnt_classifier.allowlist import (
        CLASSIFIER_REQUIRED,
        SAFE_ALLOWLIST,
      )

      # Verify expected safe tools
      expected_safe = {"view_file", "list_dir", "grep_search", "command_status"}
      missing = expected_safe - SAFE_ALLOWLIST
      if missing:
        duration = (time.perf_counter() - start) * 1000
        return DiagnosticCheck(
          name="allowlist_sanity",
          status=DiagnosticStatus.WARN,
          message=f"Expected safe tools missing from allowlist: {missing}",
          duration_ms=duration,
        )

      # Verify no dangerous tools leaked into allowlist
      dangerous = {"run_command", "write_to_file", "send_command_input"}
      leaked = dangerous & SAFE_ALLOWLIST
      if leaked:
        duration = (time.perf_counter() - start) * 1000
        return DiagnosticCheck(
          name="allowlist_sanity",
          status=DiagnosticStatus.FAIL,
          message=f"DANGEROUS tools in allowlist: {leaked}",
          duration_ms=duration,
        )

      # Verify no overlap between allowlist and classifier-required
      overlap = SAFE_ALLOWLIST & CLASSIFIER_REQUIRED
      if overlap:
        duration = (time.perf_counter() - start) * 1000
        return DiagnosticCheck(
          name="allowlist_sanity",
          status=DiagnosticStatus.WARN,
          message=f"Tools in both allowlist and classifier-required: {overlap}",
          duration_ms=duration,
        )

      duration = (time.perf_counter() - start) * 1000
      return DiagnosticCheck(
        name="allowlist_sanity",
        status=DiagnosticStatus.PASS,
        message=f"Allowlist has {len(SAFE_ALLOWLIST)} safe tools, {len(CLASSIFIER_REQUIRED)} require classification.",
        duration_ms=duration,
        details={
          "safe_count": len(SAFE_ALLOWLIST),
          "classifier_required_count": len(CLASSIFIER_REQUIRED),
        },
      )
    except Exception as e:
      duration = (time.perf_counter() - start) * 1000
      return DiagnosticCheck(
        name="allowlist_sanity",
        status=DiagnosticStatus.FAIL,
        message=f"Allowlist sanity check failed: {e}",
        duration_ms=duration,
      )

  def _check_policy_config(self) -> DiagnosticCheck:
    """Check MCP policy configuration."""
    start = time.perf_counter()
    try:
      from agnt_classifier.mcp_policy import (
        MCPServerInfo,
        get_default_agnt_policy,
        is_mcp_server_allowed_by_policy,
      )

      policy = get_default_agnt_policy()

      # Verify fleet servers are allowed
      fleet_servers = [
        "StitchMCP",
        "chrome-devtools-mcp",
        "firebase-mcp-server",
        "google-developer-knowledge",
        "sequential-thinking",
      ]
      blocked_fleet = []
      for name in fleet_servers:
        info = MCPServerInfo(name=name)
        result = is_mcp_server_allowed_by_policy(name, info, policy)
        if not result.allowed:
          blocked_fleet.append(name)

      if blocked_fleet:
        duration = (time.perf_counter() - start) * 1000
        return DiagnosticCheck(
          name="policy_config",
          status=DiagnosticStatus.FAIL,
          message=f"Fleet servers blocked by policy: {blocked_fleet}",
          duration_ms=duration,
        )

      # Verify reserved names are blocked
      info = MCPServerInfo(name="claude-in-chrome")
      result = is_mcp_server_allowed_by_policy("claude-in-chrome", info, policy)
      if result.allowed:
        duration = (time.perf_counter() - start) * 1000
        return DiagnosticCheck(
          name="policy_config",
          status=DiagnosticStatus.FAIL,
          message="Reserved server 'claude-in-chrome' was ALLOWED!",
          duration_ms=duration,
        )

      duration = (time.perf_counter() - start) * 1000
      return DiagnosticCheck(
        name="policy_config",
        status=DiagnosticStatus.PASS,
        message=f"MCP policy configured: {len(fleet_servers)} fleet servers allowed, reserved names blocked.",
        duration_ms=duration,
        details={
          "fleet_servers_count": len(fleet_servers),
          "allowlist_count": len(policy.allowed_servers)
          if policy.allowed_servers
          else 0,
          "denylist_count": len(policy.denied_servers),
        },
      )
    except Exception as e:
      duration = (time.perf_counter() - start) * 1000
      return DiagnosticCheck(
        name="policy_config",
        status=DiagnosticStatus.FAIL,
        message=f"Policy config check failed: {e}",
        duration_ms=duration,
      )

  def _check_gateway_pipeline(self) -> DiagnosticCheck:
    """Check end-to-end gateway pipeline."""
    start = time.perf_counter()
    try:
      from agnt_classifier.bridge import ClassifiedGateway

      gateway = ClassifiedGateway()

      # Test allowlisted tool passes
      r1 = gateway.evaluate("view_file")
      if not r1.allowed:
        duration = (time.perf_counter() - start) * 1000
        return DiagnosticCheck(
          name="gateway_pipeline",
          status=DiagnosticStatus.FAIL,
          message="Gateway blocked allowlisted tool 'view_file'.",
          duration_ms=duration,
        )

      # Test dangerous command is blocked
      r2 = gateway.evaluate(
        "run_command",
        {"CommandLine": "rm -rf /"},
      )
      if r2.allowed:
        duration = (time.perf_counter() - start) * 1000
        return DiagnosticCheck(
          name="gateway_pipeline",
          status=DiagnosticStatus.FAIL,
          message="Gateway ALLOWED 'rm -rf /'!",
          duration_ms=duration,
        )

      # Verify telemetry was recorded
      summary = gateway.get_summary()
      evals = summary["telemetry"]["total_evaluations"]
      if evals != 2:
        duration = (time.perf_counter() - start) * 1000
        return DiagnosticCheck(
          name="gateway_pipeline",
          status=DiagnosticStatus.WARN,
          message=f"Expected 2 evaluations, got {evals}.",
          duration_ms=duration,
        )

      duration = (time.perf_counter() - start) * 1000
      return DiagnosticCheck(
        name="gateway_pipeline",
        status=DiagnosticStatus.PASS,
        message="Gateway pipeline end-to-end check passed.",
        duration_ms=duration,
        details=summary,
      )
    except Exception as e:
      duration = (time.perf_counter() - start) * 1000
      return DiagnosticCheck(
        name="gateway_pipeline",
        status=DiagnosticStatus.FAIL,
        message=f"Gateway pipeline check failed: {e}",
        duration_ms=duration,
      )

  def _check_telemetry_catalog(self) -> DiagnosticCheck:
    """Check that telemetry catalog has classifier events."""
    start = time.perf_counter()
    try:
      from telemetry.catalog import EventCatalog, EventCategory

      # Verify classifier_outcome event exists
      event = EventCatalog.classifier_outcome(
        tool_id="test",
        verdict="allow",
        stage=1,
      )
      if event.category != EventCategory.CLASSIFIER:
        duration = (time.perf_counter() - start) * 1000
        return DiagnosticCheck(
          name="telemetry_catalog",
          status=DiagnosticStatus.FAIL,
          message=f"classifier_outcome has wrong category: {event.category}",
          duration_ms=duration,
        )

      duration = (time.perf_counter() - start) * 1000
      return DiagnosticCheck(
        name="telemetry_catalog",
        status=DiagnosticStatus.PASS,
        message="Telemetry catalog has classifier events.",
        duration_ms=duration,
        details={"event_name": event.event},
      )
    except Exception as e:
      duration = (time.perf_counter() - start) * 1000
      return DiagnosticCheck(
        name="telemetry_catalog",
        status=DiagnosticStatus.FAIL,
        message=f"Telemetry catalog check failed: {e}",
        duration_ms=duration,
      )


def run_classifier_diagnostics() -> dict[str, Any]:
  """Run all classifier diagnostics and return a structured report.

  Convenience function for CLI integration.
  """
  diag = ClassifierDiagnostics()
  checks = diag.run_all()

  passed = sum(1 for c in checks if c.status == DiagnosticStatus.PASS)
  warned = sum(1 for c in checks if c.status == DiagnosticStatus.WARN)
  failed = sum(1 for c in checks if c.status == DiagnosticStatus.FAIL)

  overall = "PASS" if failed == 0 else "FAIL"

  return {
    "overall": overall,
    "passed": passed,
    "warned": warned,
    "failed": failed,
    "total": len(checks),
    "checks": [
      {
        "name": c.name,
        "status": c.status.value,
        "message": c.message,
        "duration_ms": round(c.duration_ms, 2),
        "details": c.details,
      }
      for c in checks
    ],
  }
