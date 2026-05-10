# labs/uphillsnowball/agent/gauntlet.py
"""The 17-Layer Gauntlet: Request Filtering & Risk Scoring.

All agent actions pass through this gauntlet before execution.
Each layer is a deterministic check — no AI involved.

Layer Categories:
    L1-L4:   Identity & Authentication
    L5-L8:   Content Safety & Compliance
    L9-L12:  Structural Integrity
    L13-L16: Operational Boundaries
    L17:     Dead-Man's Switch (RKILL)
"""

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger("uphillsnowball.gauntlet")


class GauntletVerdict(Enum):
  """Result of gauntlet evaluation."""

  PASS = "pass"
  WARN = "warn"
  BLOCK = "block"
  RKILL = "rkill"  # Emergency shutdown


@dataclass
class LayerResult:
  """Result from a single gauntlet layer."""

  layer_id: int
  layer_name: str
  verdict: GauntletVerdict
  detail: str = ""
  elapsed_us: int = 0


@dataclass
class GauntletResult:
  """Aggregate result from all 17 layers."""

  passed: bool
  verdict: GauntletVerdict
  layers: list[LayerResult] = field(default_factory=list)
  blocked_by: int | None = None
  total_elapsed_ms: int = 0


# ── Protected Paths ────────────────────────────────────────────────────────

_IMMUTABLE_FILES = {
  "AGENTS.md",
  "GEMINI.md",
  "CLAUDE.md",
  "monorepo_manifest.yaml",
  "antigravity-mcp-config.json",
  "BUSINESS_CONTEXT_LOCKED.md",
  "RISK_REGISTER.md",
  ".gitignore",
}

_FORBIDDEN_COMMANDS = {
  "rm -rf",
  "sudo",
  "chmod 777",
  "mkfs",
  "dd if=",
  "curl | sh",
  "wget | sh",
  "eval(",
}

_FORBIDDEN_PATTERNS = [
  r"(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]+['\"]",
  r"sk-[a-zA-Z0-9]{48}",  # OpenAI key pattern
  r"AIza[a-zA-Z0-9\-_]{35}",  # Google API key pattern
  r"ghp_[a-zA-Z0-9]{36}",  # GitHub PAT pattern
]


# ── Layer Implementations ──────────────────────────────────────────────────


def _l01_identity_check(action: dict[str, Any]) -> LayerResult:
  """L1: Verify agent identity is registered."""
  agent_id = action.get("agent_id", "")
  if not agent_id:
    return LayerResult(
      1, "Identity Check", GauntletVerdict.BLOCK, "No agent_id provided"
    )
  return LayerResult(1, "Identity Check", GauntletVerdict.PASS)


def _l02_role_authorization(action: dict[str, Any]) -> LayerResult:
  """L2: Verify agent role is authorized for this action type."""
  role = action.get("role", "")
  action_type = action.get("type", "")

  # Executors can write code; Directors cannot
  if action_type == "code_write" and role == "director":
    return LayerResult(
      2,
      "Role Authorization",
      GauntletVerdict.BLOCK,
      "Directors cannot write code directly",
    )
  return LayerResult(2, "Role Authorization", GauntletVerdict.PASS)


def _l03_session_validity(action: dict[str, Any]) -> LayerResult:
  """L3: Verify session is active and not expired."""
  session_start = action.get("session_start", 0)
  max_session_hours = 8
  if time.time() - session_start > max_session_hours * 3600:
    return LayerResult(
      3,
      "Session Validity",
      GauntletVerdict.WARN,
      f"Session exceeds {max_session_hours}h limit",
    )
  return LayerResult(3, "Session Validity", GauntletVerdict.PASS)


def _l04_rate_limit(action: dict[str, Any]) -> LayerResult:
  """L4: Check rate limiting (actions per minute)."""
  actions_this_minute = action.get("actions_this_minute", 0)
  if actions_this_minute > 60:
    return LayerResult(
      4,
      "Rate Limit",
      GauntletVerdict.BLOCK,
      f"Rate limit exceeded: {actions_this_minute}/min",
    )
  return LayerResult(4, "Rate Limit", GauntletVerdict.PASS)


def _l05_content_safety(action: dict[str, Any]) -> LayerResult:
  """L5: Check content for forbidden patterns (secrets, keys)."""
  content = action.get("content", "")
  for pattern in _FORBIDDEN_PATTERNS:
    if re.search(pattern, content):
      return LayerResult(
        5,
        "Content Safety",
        GauntletVerdict.BLOCK,
        "Potential secret/key detected in content",
      )
  return LayerResult(5, "Content Safety", GauntletVerdict.PASS)


def _l06_command_safety(action: dict[str, Any]) -> LayerResult:
  """L6: Check commands for forbidden operations."""
  command = action.get("command", "")
  for forbidden in _FORBIDDEN_COMMANDS:
    if forbidden in command:
      return LayerResult(
        6, "Command Safety", GauntletVerdict.BLOCK, f"Forbidden command: {forbidden}"
      )
  return LayerResult(6, "Command Safety", GauntletVerdict.PASS)


def _l07_path_protection(action: dict[str, Any]) -> LayerResult:
  """L7: Protect immutable files from modification."""
  target_file = action.get("target_file", "")
  if target_file:
    filename = Path(target_file).name
    if filename in _IMMUTABLE_FILES:
      return LayerResult(
        7, "Path Protection", GauntletVerdict.BLOCK, f"Immutable file: {filename}"
      )
  return LayerResult(7, "Path Protection", GauntletVerdict.PASS)


def _l08_gemini_zone(action: dict[str, Any]) -> LayerResult:
  """L8: Ensure .gemini/ directory is not modified without override."""
  target = action.get("target_file", "")
  if ".gemini/" in target and action.get("type") in ("write", "delete"):
    if not action.get("system_override", False):
      return LayerResult(
        8,
        "Gemini Zone",
        GauntletVerdict.BLOCK,
        "Cannot modify .gemini/ without system override",
      )
  return LayerResult(8, "Gemini Zone", GauntletVerdict.PASS)


def _l09_loc_ceiling(action: dict[str, Any]) -> LayerResult:
  """L9: Enforce 500 LOC ceiling per file change."""
  lines_changed = action.get("lines_changed", 0)
  if lines_changed > 500:
    return LayerResult(
      9,
      "LOC Ceiling",
      GauntletVerdict.WARN,
      f"Change exceeds 500 LOC ceiling: {lines_changed}",
    )
  return LayerResult(9, "LOC Ceiling", GauntletVerdict.PASS)


def _l10_dependency_check(action: dict[str, Any]) -> LayerResult:
  """L10: Check for banned dependencies (BullMQ, etc)."""
  content = action.get("content", "")
  banned = ["bullmq", "bull", "agenda", "bee-queue"]
  for dep in banned:
    if dep in content.lower():
      return LayerResult(
        10,
        "Dependency Check",
        GauntletVerdict.BLOCK,
        f"Banned dependency: {dep} (use Google Cloud Tasks)",
      )
  return LayerResult(10, "Dependency Check", GauntletVerdict.PASS)


def _l11_model_isolation(action: dict[str, Any]) -> LayerResult:
  """L11: Ensure only authorized models are invoked."""
  model = action.get("model", "")
  if model and "anthropic" not in model.lower() and "openai" not in model.lower():
    return LayerResult(11, "Model Isolation", GauntletVerdict.PASS)
  if model:
    return LayerResult(
      11, "Model Isolation", GauntletVerdict.WARN, f"Non-Google model detected: {model}"
    )
  return LayerResult(11, "Model Isolation", GauntletVerdict.PASS)


def _l12_output_size(action: dict[str, Any]) -> LayerResult:
  """L12: Check output doesn't exceed context limits."""
  output_tokens = action.get("output_tokens", 0)
  if output_tokens > 32000:
    return LayerResult(
      12,
      "Output Size",
      GauntletVerdict.WARN,
      f"Output exceeds safe context: {output_tokens} tokens",
    )
  return LayerResult(12, "Output Size", GauntletVerdict.PASS)


def _l13_network_egress(action: dict[str, Any]) -> LayerResult:
  """L13: Monitor network egress for data exfiltration."""
  urls = action.get("urls", [])
  for url in urls:
    if not any(
      safe in url
      for safe in [
        "googleapis.com",
        "google.com",
        "firebase",
        "github.com",
        "shadowtagai",
      ]
    ):
      return LayerResult(
        13, "Network Egress", GauntletVerdict.WARN, f"External URL: {url}"
      )
  return LayerResult(13, "Network Egress", GauntletVerdict.PASS)


def _l14_cost_guard(action: dict[str, Any]) -> LayerResult:
  """L14: Check estimated cost doesn't exceed budget."""
  estimated_cost_usd = action.get("estimated_cost_usd", 0.0)
  if estimated_cost_usd > 1.0:
    return LayerResult(
      14,
      "Cost Guard",
      GauntletVerdict.WARN,
      f"Estimated cost ${estimated_cost_usd:.2f} > $1.00 threshold",
    )
  return LayerResult(14, "Cost Guard", GauntletVerdict.PASS)


def _l15_git_safety(action: dict[str, Any]) -> LayerResult:
  """L15: Block force-pushes and history rewrites."""
  command = action.get("command", "")
  if any(x in command for x in ["--force", "push -f", "rebase", "reset --hard"]):
    return LayerResult(
      15,
      "Git Safety",
      GauntletVerdict.BLOCK,
      "Force-push / history rewrite requires Clutch mode",
    )
  return LayerResult(15, "Git Safety", GauntletVerdict.PASS)


def _l16_telemetry_airgap(action: dict[str, Any]) -> LayerResult:
  """L16: Ensure telemetry and error reporting are disabled."""
  content = action.get("content", "")
  if any(x in content for x in ["SENTRY_DSN", "BUGSNAG", "DATADOG_API_KEY"]):
    return LayerResult(
      16,
      "Telemetry Airgap",
      GauntletVerdict.BLOCK,
      "External telemetry service detected",
    )
  return LayerResult(16, "Telemetry Airgap", GauntletVerdict.PASS)


def _l17_rkill(action: dict[str, Any]) -> LayerResult:
  """L17: RKILL Dead-Man's Switch.

  If the RKILL flag file exists, ALL operations are blocked.
  This is the emergency shutdown mechanism.
  """
  rkill_path = os.getenv("RKILL_FLAG", "/tmp/uphillsnowball_rkill")
  if Path(rkill_path).exists():
    return LayerResult(
      17,
      "RKILL Dead-Man's Switch",
      GauntletVerdict.RKILL,
      "RKILL ACTIVATED — all operations suspended",
    )
  return LayerResult(17, "RKILL Dead-Man's Switch", GauntletVerdict.PASS)


# ── All 17 Layers ──────────────────────────────────────────────────────────

_LAYERS = [
  _l01_identity_check,
  _l02_role_authorization,
  _l03_session_validity,
  _l04_rate_limit,
  _l05_content_safety,
  _l06_command_safety,
  _l07_path_protection,
  _l08_gemini_zone,
  _l09_loc_ceiling,
  _l10_dependency_check,
  _l11_model_isolation,
  _l12_output_size,
  _l13_network_egress,
  _l14_cost_guard,
  _l15_git_safety,
  _l16_telemetry_airgap,
  _l17_rkill,
]


# ── Main Entry Point ──────────────────────────────────────────────────────


def evaluate(action: dict[str, Any]) -> GauntletResult:
  """Run all 17 layers of the gauntlet on an agent action.

  Stops on first BLOCK or RKILL.
  Aggregates all WARNs.
  """
  start = time.monotonic()
  results = []
  final_verdict = GauntletVerdict.PASS
  blocked_by = None

  for layer_fn in _LAYERS:
    t0 = time.monotonic()
    result = layer_fn(action)
    result.elapsed_us = int((time.monotonic() - t0) * 1_000_000)
    results.append(result)

    if result.verdict == GauntletVerdict.RKILL:
      final_verdict = GauntletVerdict.RKILL
      blocked_by = result.layer_id
      logger.critical("RKILL TRIGGERED at Layer %d", result.layer_id)
      break

    if result.verdict == GauntletVerdict.BLOCK:
      final_verdict = GauntletVerdict.BLOCK
      blocked_by = result.layer_id
      logger.warning(
        "Gauntlet BLOCKED at Layer %d (%s): %s",
        result.layer_id,
        result.layer_name,
        result.detail,
      )
      break

    if result.verdict == GauntletVerdict.WARN and final_verdict == GauntletVerdict.PASS:
      final_verdict = GauntletVerdict.WARN

  elapsed_ms = int((time.monotonic() - start) * 1000)

  return GauntletResult(
    passed=final_verdict in (GauntletVerdict.PASS, GauntletVerdict.WARN),
    verdict=final_verdict,
    layers=results,
    blocked_by=blocked_by,
    total_elapsed_ms=elapsed_ms,
  )
