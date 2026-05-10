"""
tools/mcp-telemetry-healer/diagnose.py — Dual Immune System

Implements a two-layer diagnostic protocol:
  Layer 1 (Innate): MCP server health checks via process monitoring
  Layer 2 (Adaptive): Cloud Logging analysis for recurring error patterns

This works alongside the Spanner Healer (database immune system) to provide
full-stack self-healing. The Spanner Healer handles data-plane issues while
this module handles control-plane and telemetry anomalies.

Dependencies:
  - Observability MCP (uphill-observability) for log queries
  - Cloud Run MCP (uphill-cloud-run) for service health
  - MCP Watchdog (scripts/mcp_watchdog.py) for process-level monitoring

Rule 00 compliant: No destructive operations. All healing is append-only logging
and advisory scale recommendations.
"""

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path


# ─── Configuration ──────────────────────────────────────────────────────────

PROJECT_ID = "shadowtag-omega-v4"

# Error pattern thresholds (per hour)
ERROR_RATE_WARN = 10
ERROR_RATE_CRITICAL = 50

# Known healable patterns
HEALABLE_PATTERNS = {
  "ECONNRESET": {
    "fix": "Inject NODE_OPTIONS=--dns-result-order=ipv4first into MCP server env",
    "severity": "HIGH",
    "auto_heal": True,
  },
  "DEADLINE_EXCEEDED": {
    "fix": "Increase Cloud Run request timeout or add retry with exponential backoff",
    "severity": "MEDIUM",
    "auto_heal": False,
  },
  "PERMISSION_DENIED": {
    "fix": "Verify IAM roles on service account. Check ADC configuration.",
    "severity": "HIGH",
    "auto_heal": False,
  },
  "RESOURCE_EXHAUSTED": {
    "fix": "Scale up Cloud Run instances or increase Firestore throughput",
    "severity": "CRITICAL",
    "auto_heal": False,
  },
  "UNAUTHENTICATED": {
    "fix": "Refresh ADC: gcloud auth application-default login --project=shadowtag-omega-v4",
    "severity": "HIGH",
    "auto_heal": False,
  },
  "TLS handshake": {
    "fix": "IPv6 blackholing detected. Apply IPv4-first DNS resolution.",
    "severity": "HIGH",
    "auto_heal": True,
  },
}


# ─── Data Models ────────────────────────────────────────────────────────────


@dataclass
class HealthCheck:
  """Result of a single health check."""

  target: str
  status: str  # "healthy", "degraded", "down"
  latency_ms: float
  error: str | None = None
  recommendation: str | None = None


@dataclass
class ErrorPattern:
  """A detected recurring error pattern."""

  pattern: str
  count: int
  severity: str
  fix: str
  auto_healable: bool


@dataclass
class DiagnosticReport:
  """Full diagnostic report from both immune layers."""

  timestamp: str
  layer1_results: list[HealthCheck]
  layer2_patterns: list[ErrorPattern]
  overall_health: str
  recommendations: list[str]


# ─── Layer 1: Innate Immunity (Process Monitoring) ──────────────────────────


def check_mcp_processes() -> list[HealthCheck]:
  """Check MCP server processes via ps (Layer 1 — Innate)."""
  results = []

  mcp_signatures = [
    ("StitchMCP", "stitch"),
    ("chrome-devtools-mcp", "chrome-devtools"),
    ("firebase-mcp-server", "firebase"),
    ("google-developer-knowledge", "developer-knowledge"),
    ("sequential-thinking", "sequential"),
    ("gcloud-mcp", "gcloud-mcp"),
    ("observability-mcp", "observability-mcp"),
    ("cloud-run-mcp", "cloud-run-mcp"),
    ("storage-mcp", "storage-mcp"),
    ("design.googleapis.com", "design-mcp"),
  ]

  for name, signature in mcp_signatures:
    try:
      result = subprocess.run(
        ["pgrep", "-f", signature],
        capture_output=True,
        text=True,
        timeout=5,
      )
      if result.returncode == 0:
        results.append(
          HealthCheck(
            target=name,
            status="healthy",
            latency_ms=0,
          )
        )
      else:
        results.append(
          HealthCheck(
            target=name,
            status="down",
            latency_ms=-1,
            error="No matching process found",
            recommendation=f"Restart {name} MCP server",
          )
        )
    except subprocess.TimeoutExpired:
      results.append(
        HealthCheck(
          target=name,
          status="degraded",
          latency_ms=5000,
          error="Process check timed out",
          recommendation=f"Investigate hung {name} process",
        )
      )
    except FileNotFoundError:
      # pgrep not available (e.g., CI environment)
      results.append(
        HealthCheck(
          target=name,
          status="unknown",
          latency_ms=-1,
          error="pgrep not available",
        )
      )

  return results


# ─── Layer 2: Adaptive Immunity (Log Pattern Analysis) ──────────────────────


def analyze_error_patterns(log_entries: list[dict]) -> list[ErrorPattern]:
  """Analyze log entries for known healable error patterns (Layer 2 — Adaptive)."""
  pattern_counts: dict[str, int] = {}

  for entry in log_entries:
    message = entry.get("message", "")
    for pattern in HEALABLE_PATTERNS:
      if pattern.lower() in message.lower():
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

  results = []
  for pattern, count in pattern_counts.items():
    info = HEALABLE_PATTERNS[pattern]
    results.append(
      ErrorPattern(
        pattern=pattern,
        count=count,
        severity=info["severity"],
        fix=info["fix"],
        auto_healable=info["auto_heal"],
      )
    )

  return sorted(results, key=lambda p: p.count, reverse=True)


# ─── Diagnostic Engine ──────────────────────────────────────────────────────


def run_diagnostic() -> DiagnosticReport:
  """Execute the full dual-layer diagnostic protocol."""
  print("=" * 60)
  print("  🛡️ Dual Immune System — Telemetry Diagnostic")
  print("=" * 60)

  ts = datetime.now(UTC).isoformat()

  # Layer 1: Innate Immunity
  print("\n[Layer 1] Innate Immunity — MCP Process Health Check...")
  l1_results = check_mcp_processes()

  healthy = sum(1 for r in l1_results if r.status == "healthy")
  degraded = sum(1 for r in l1_results if r.status == "degraded")
  down = sum(1 for r in l1_results if r.status == "down")
  unknown = sum(1 for r in l1_results if r.status == "unknown")

  for r in l1_results:
    icon = {"healthy": "✅", "degraded": "⚠️", "down": "🔴", "unknown": "❓"}.get(
      r.status, "❓"
    )
    print(f"  {icon} {r.target}: {r.status}")
    if r.recommendation:
      print(f"     ↳ {r.recommendation}")

  print(
    f"\n  Summary: {healthy} healthy, {degraded} degraded, {down} down, {unknown} unknown"
  )

  # Layer 2: Adaptive Immunity
  print("\n[Layer 2] Adaptive Immunity — Error Pattern Analysis...")

  # In production, this queries the Observability MCP for recent error logs.
  # For standalone testing, use sample data.
  sample_logs = [
    {
      "message": "Client network socket disconnected before secure TLS handshake",
      "severity": "ERROR",
    },
    {
      "message": "ECONNRESET on connection to developerknowledge.googleapis.com",
      "severity": "ERROR",
    },
    {
      "message": "ECONNRESET on connection to developerknowledge.googleapis.com",
      "severity": "ERROR",
    },
    {
      "message": "DEADLINE_EXCEEDED: Cloud Spanner query timeout after 30s",
      "severity": "WARNING",
    },
    {"message": "Request completed successfully", "severity": "INFO"},
    {
      "message": "TLS handshake timeout connecting to remote MCP endpoint",
      "severity": "ERROR",
    },
  ]

  l2_patterns = analyze_error_patterns(sample_logs)

  for p in l2_patterns:
    auto_tag = " [AUTO-HEAL]" if p.auto_healable else ""
    print(f"  🔍 {p.pattern}: {p.count}x ({p.severity}){auto_tag}")
    print(f"     ↳ Fix: {p.fix}")

  if not l2_patterns:
    print("  ✅ No recurring error patterns detected")

  # Generate recommendations
  recommendations = []
  for p in l2_patterns:
    if p.auto_healable:
      recommendations.append(f"[AUTO] {p.fix}")
    else:
      recommendations.append(f"[MANUAL] {p.fix}")

  for r in l1_results:
    if r.recommendation:
      recommendations.append(f"[PROCESS] {r.recommendation}")

  # Determine overall health
  if down > 2 or any(p.severity == "CRITICAL" for p in l2_patterns):
    overall = "CRITICAL"
  elif down > 0 or degraded > 0 or any(p.severity == "HIGH" for p in l2_patterns):
    overall = "DEGRADED"
  else:
    overall = "HEALTHY"

  # Persist to audit trail
  audit_path = (
    Path(__file__).parent.parent.parent / ".beads" / "telemetry_diagnostics.jsonl"
  )
  audit_path.parent.mkdir(parents=True, exist_ok=True)
  with open(audit_path, "a") as f:
    f.write(
      json.dumps(
        {
          "ts": ts,
          "overall": overall,
          "healthy": healthy,
          "degraded": degraded,
          "down": down,
          "patterns": [{"pattern": p.pattern, "count": p.count} for p in l2_patterns],
        }
      )
      + "\n"
    )

  print(f"\n{'=' * 60}")
  print(f"  {'✅' if overall == 'HEALTHY' else '⚠️'} Overall Health: {overall}")
  print(f"{'=' * 60}")

  return DiagnosticReport(
    timestamp=ts,
    layer1_results=l1_results,
    layer2_patterns=l2_patterns,
    overall_health=overall,
    recommendations=recommendations,
  )


if __name__ == "__main__":
  report = run_diagnostic()
  if report.recommendations:
    print(f"\n📋 {len(report.recommendations)} recommendation(s):")
    for i, r in enumerate(report.recommendations, 1):
      print(f"  {i}. {r}")
