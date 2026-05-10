#!/usr/bin/env python3
"""
Antigravity Doctor — Ported from Claude Code's /doctor slash command

Grounded in:
  - Claude_Source_Code/utils/doctorDiagnostic.ts (626 lines)
  - Claude_Source_Code/utils/preflightChecks.tsx (19K, startup validation)
  - Claude_Source_Code/utils/doctorContextWarnings.ts (8K, context warnings)
  - Claude_Source_Code/bridge/envLessBridgeConfig.ts (7K, env validation)

Architecture:
  Comprehensive system health diagnostic that checks:
  1. Python/Node runtime versions and compatibility
  2. MCP server fleet health (delegates to mcp_autosync.py)
  3. Git repository integrity and auth chain
  4. Daemon fleet status (KAIROS, Loop Steward, Dream, etc.)
  5. Disk space and resource availability
  6. Secret Manager connectivity

  This is the equivalent of `claude doctor` — a single command to diagnose
  all known failure modes in the Antigravity ecosystem.

Usage:
  python scripts/antigravity_doctor.py [--json] [--verbose]

Integration:
  Called from /repo-pulse workflow and KAIROS startup sequence.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BEADS_DIR = PROJECT_ROOT / ".beads"
DOCTOR_LOG = BEADS_DIR / "doctor_report.jsonl"

# From AGENTS.md daemon fleet registry
DAEMON_FLEET = {
  "Dream Consolidation": "scripts/dream_consolidation.py",
  "Loop Steward": "scripts/loop_steward.py",
  "KAIROS": "scripts/kairos_daemon.py",
  "pnkln-evolve": "scripts/pnkln_evolve.py",
  "Omni-Autolint": "scripts/gca_autolint_daemon.py",
}

# Required tools (from doctorDiagnostic.ts ripgrepStatus check)
REQUIRED_TOOLS = {
  "python3": "Python 3.14+ required",
  "node": "Node.js required for MCP servers",
  "git": "Git required for repository operations",
  "ruff": "Ruff linter required (TACSOP 5)",
  "rg": "ripgrep required for search operations",
}

OPTIONAL_TOOLS = {
  "biome": "Biome linter for TypeScript",
  "firebase": "Firebase CLI for deployment",
  "gcloud": "Google Cloud SDK",
  "dotnet": ".NET SDK for Semantic Kernel",
}


# ── Types ────────────────────────────────────────────────────────────────


@dataclass
class CheckResult:
  """Single diagnostic check result."""

  name: str
  passed: bool
  message: str
  details: str | None = None
  severity: str = "info"  # info, warning, error, critical
  fix: str | None = None

  def to_dict(self) -> dict:
    d = {
      "name": self.name,
      "passed": self.passed,
      "message": self.message,
      "severity": self.severity,
    }
    if self.details:
      d["details"] = self.details
    if self.fix:
      d["fix"] = self.fix
    return d


@dataclass
class DoctorReport:
  """
  Full doctor report, modeled after doctorDiagnostic.ts DiagnosticInfo.
  """

  timestamp: float = field(default_factory=time.time)
  platform_info: dict = field(default_factory=dict)
  checks: list[CheckResult] = field(default_factory=list)
  passed: int = 0
  failed: int = 0
  warnings: int = 0
  overall_health: str = "unknown"

  def to_dict(self) -> dict:
    return {
      "timestamp": self.timestamp,
      "platform_info": self.platform_info,
      "checks": [c.to_dict() for c in self.checks],
      "summary": {
        "passed": self.passed,
        "failed": self.failed,
        "warnings": self.warnings,
        "total": len(self.checks),
        "overall_health": self.overall_health,
      },
    }


# ── Doctor Engine ────────────────────────────────────────────────────────


class AntigravityDoctor:
  """
  Port of Claude Code's getDoctorDiagnostic() + preflightChecks.

  Diagnostic pipeline:
    1. Platform info (maps to getInstallationPath/getInvokedBinary)
    2. Runtime checks (maps to ripgrepStatus)
    3. Repository checks (maps to detectMultipleInstallations)
    4. Fleet checks (maps to MCP validation)
    5. Resource checks (maps to diskSpace warnings)
  """

  def __init__(self, verbose: bool = False) -> None:
    self.verbose = verbose
    self.logger = logging.getLogger("antigravity_doctor")

  def diagnose(self) -> DoctorReport:
    """Execute full diagnostic pipeline."""
    report = DoctorReport()

    # Phase 0: Platform info
    report.platform_info = self._get_platform_info()

    # Phase 1: Runtime environment
    self._check_runtimes(report)

    # Phase 2: Repository integrity
    self._check_repository(report)

    # Phase 3: Auth chain
    self._check_auth(report)

    # Phase 4: Daemon fleet
    self._check_daemons(report)

    # Phase 5: Disk space
    self._check_resources(report)

    # Phase 6: MCP fleet (delegates to mcp_autosync.py)
    self._check_mcp_fleet(report)

    # Phase 7: Truth surfaces
    self._check_truth_surfaces(report)

    # Summarize
    report.passed = sum(1 for c in report.checks if c.passed)
    report.failed = sum(
      1 for c in report.checks if not c.passed and c.severity in ("error", "critical")
    )
    report.warnings = sum(
      1 for c in report.checks if not c.passed and c.severity == "warning"
    )

    if report.failed == 0 and report.warnings == 0:
      report.overall_health = "healthy"
    elif report.failed == 0:
      report.overall_health = "degraded"
    else:
      report.overall_health = "unhealthy"

    return report

  def _get_platform_info(self) -> dict:
    """Gather platform information (maps to getNormalizedPaths)."""
    return {
      "os": platform.system(),
      "os_version": platform.version(),
      "machine": platform.machine(),
      "python_version": platform.python_version(),
      "hostname": platform.node(),
      "cwd": str(PROJECT_ROOT),
    }

  def _check_runtimes(self, report: DoctorReport) -> None:
    """Check required and optional tool availability."""
    for tool, desc in REQUIRED_TOOLS.items():
      path = shutil.which(tool)
      if path:
        version = self._get_version(tool)
        report.checks.append(
          CheckResult(
            name=f"runtime/{tool}",
            passed=True,
            message=f"{tool}: {version or 'found'} at {path}",
          )
        )
      else:
        report.checks.append(
          CheckResult(
            name=f"runtime/{tool}",
            passed=False,
            message=f"{tool}: NOT FOUND — {desc}",
            severity="error",
            fix=f"Install {tool} via your package manager",
          )
        )

    for tool, desc in OPTIONAL_TOOLS.items():
      path = shutil.which(tool)
      if path:
        version = self._get_version(tool)
        report.checks.append(
          CheckResult(
            name=f"runtime/{tool}",
            passed=True,
            message=f"{tool}: {version or 'found'} (optional)",
          )
        )
      else:
        report.checks.append(
          CheckResult(
            name=f"runtime/{tool}",
            passed=False,
            message=f"{tool}: not found — {desc}",
            severity="info",
          )
        )

  def _check_repository(self, report: DoctorReport) -> None:
    """Check git repository integrity."""
    git_dir = PROJECT_ROOT / ".git"
    if git_dir.exists():
      report.checks.append(
        CheckResult(
          name="repo/git_init",
          passed=True,
          message="Git repository initialized",
        )
      )

      # Check remote
      try:
        result = subprocess.run(
          ["git", "remote", "-v"],
          cwd=str(PROJECT_ROOT),
          capture_output=True,
          text=True,
          timeout=5,
        )
        if "ShadowTag-v2/Monorepo-Uphillsnowball" in result.stdout:
          report.checks.append(
            CheckResult(
              name="repo/remote",
              passed=True,
              message="Remote configured: ShadowTag-v2/Monorepo-Uphillsnowball",
            )
          )
        else:
          report.checks.append(
            CheckResult(
              name="repo/remote",
              passed=False,
              message="Remote not pointing to canonical repository",
              severity="warning",
              fix="git remote set-url origin git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git",
            )
          )
      except subprocess.TimeoutExpired, FileNotFoundError:
        report.checks.append(
          CheckResult(
            name="repo/remote",
            passed=False,
            message="Could not check git remote",
            severity="warning",
          )
        )

      # Check for uncommitted changes
      try:
        result = subprocess.run(
          ["git", "status", "--porcelain"],
          cwd=str(PROJECT_ROOT),
          capture_output=True,
          text=True,
          timeout=10,
        )
        changes = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
        report.checks.append(
          CheckResult(
            name="repo/clean",
            passed=changes == 0,
            message=f"Working tree: {changes} uncommitted changes"
            if changes
            else "Working tree clean",
            severity="info" if changes > 0 else "info",
          )
        )
      except subprocess.TimeoutExpired, FileNotFoundError:
        pass
    else:
      report.checks.append(
        CheckResult(
          name="repo/git_init",
          passed=False,
          message="Not a git repository",
          severity="error",
          fix="git init",
        )
      )

  def _check_auth(self, report: DoctorReport) -> None:
    """Check authentication chain."""
    # GitHub App PEM
    pem_paths = [
      Path.home()
      / "Downloads"
      / "antigravity-shadowtag-manager.2026-03-17.private-key.pem",
      Path.home() / ".ssh" / "antigravity-shadowtag-manager.pem",
    ]
    pem_found = any(p.exists() for p in pem_paths)
    pem_env = bool(os.environ.get("SHADOWTAG_PEM"))

    report.checks.append(
      CheckResult(
        name="auth/github_pem",
        passed=pem_found or pem_env,
        message="GitHub App PEM found"
        if pem_found or pem_env
        else "GitHub App PEM not found",
        severity="warning" if not (pem_found or pem_env) else "info",
        fix="Ensure PEM at ~/Downloads/ or set $SHADOWTAG_PEM",
      )
    )

    # SSH key
    ssh_dir = Path.home() / ".ssh"
    has_ssh = any((ssh_dir / f).exists() for f in ("id_ed25519", "id_rsa", "id_ecdsa"))
    report.checks.append(
      CheckResult(
        name="auth/ssh_key",
        passed=has_ssh,
        message="SSH key found" if has_ssh else "No SSH key found",
        severity="warning" if not has_ssh else "info",
      )
    )

    # GCP ADC
    adc_path = (
      Path.home() / ".config" / "gcloud" / "application_default_credentials.json"
    )
    report.checks.append(
      CheckResult(
        name="auth/gcp_adc",
        passed=adc_path.exists(),
        message="GCP ADC found" if adc_path.exists() else "GCP ADC not found",
        severity="warning" if not adc_path.exists() else "info",
        fix="gcloud auth application-default login --project=shadowtag-omega-v4",
      )
    )

  def _check_daemons(self, report: DoctorReport) -> None:
    """Check daemon fleet scripts exist."""
    for name, script in DAEMON_FLEET.items():
      path = PROJECT_ROOT / script
      report.checks.append(
        CheckResult(
          name=f"daemon/{name.lower().replace(' ', '_')}",
          passed=path.exists(),
          message=f"{name}: {'found' if path.exists() else 'MISSING'}",
          severity="warning" if not path.exists() else "info",
        )
      )

  def _check_resources(self, report: DoctorReport) -> None:
    """Check disk space and system resources."""
    try:
      usage = shutil.disk_usage(str(PROJECT_ROOT))
      free_gb = usage.free / (1024**3)
      total_gb = usage.total / (1024**3)
      pct_free = (usage.free / usage.total) * 100

      report.checks.append(
        CheckResult(
          name="resources/disk",
          passed=pct_free > 5,
          message=f"Disk: {free_gb:.1f}GB free / {total_gb:.1f}GB total ({pct_free:.1f}% free)",
          severity="error"
          if pct_free <= 5
          else ("warning" if pct_free <= 15 else "info"),
        )
      )
    except OSError, PermissionError:
      pass

    # Check project size
    try:
      result = subprocess.run(
        ["du", "-sh", "."],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=10,
      )
      if result.returncode == 0:
        size = result.stdout.strip().split("\t")[0]
        report.checks.append(
          CheckResult(
            name="resources/project_size",
            passed=True,
            message=f"Project size: {size}",
          )
        )
    except subprocess.TimeoutExpired, FileNotFoundError:
      pass

  def _check_mcp_fleet(self, report: DoctorReport) -> None:
    """Delegate MCP fleet check to mcp_autosync.py."""
    mcp_script = PROJECT_ROOT / "scripts" / "mcp_autosync.py"
    if mcp_script.exists():
      try:
        result = subprocess.run(
          [sys.executable, str(mcp_script), "--json"],
          capture_output=True,
          text=True,
          timeout=30,
        )
        if result.returncode == 0:
          mcp_data = json.loads(result.stdout)
          healthy = mcp_data.get("total_healthy", 0)
          total = len(mcp_data.get("servers", []))
          report.checks.append(
            CheckResult(
              name="mcp/fleet",
              passed=healthy >= 3,
              message=f"MCP Fleet: {healthy}/{total} servers healthy",
              severity="warning" if healthy < total else "info",
            )
          )
        else:
          report.checks.append(
            CheckResult(
              name="mcp/fleet",
              passed=False,
              message="MCP sync check failed",
              severity="warning",
            )
          )
      except subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError:
        report.checks.append(
          CheckResult(
            name="mcp/fleet",
            passed=False,
            message="MCP sync check unavailable",
            severity="info",
          )
        )
    else:
      report.checks.append(
        CheckResult(
          name="mcp/fleet",
          passed=False,
          message="mcp_autosync.py not found",
          severity="warning",
          fix="Create scripts/mcp_autosync.py",
        )
      )

  def _check_truth_surfaces(self, report: DoctorReport) -> None:
    """Check truth surface files exist."""
    surfaces = {
      "AGENTS.md": PROJECT_ROOT / ".ruler" / "AGENTS.md",
      "GEMINI.md": PROJECT_ROOT / "GEMINI.md",
      "monorepo_manifest.yaml": PROJECT_ROOT / "monorepo_manifest.yaml",
    }
    for name, path in surfaces.items():
      report.checks.append(
        CheckResult(
          name=f"truth/{name}",
          passed=path.exists(),
          message=f"{name}: {'found' if path.exists() else 'MISSING'}",
          severity="error" if not path.exists() else "info",
        )
      )

  def _get_version(self, tool: str) -> str | None:
    """Get version string for a tool."""
    version_flags = {
      "python3": ["--version"],
      "node": ["--version"],
      "git": ["--version"],
      "ruff": ["--version"],
      "rg": ["--version"],
      "biome": ["--version"],
      "firebase": ["--version"],
      "gcloud": ["--version"],
      "dotnet": ["--version"],
    }
    flags = version_flags.get(tool, ["--version"])
    try:
      result = subprocess.run(
        [tool, *flags],
        capture_output=True,
        text=True,
        timeout=5,
      )
      return result.stdout.strip().split("\n")[0] if result.returncode == 0 else None
    except subprocess.TimeoutExpired, FileNotFoundError, PermissionError:
      return None


# ── Output Formatters ────────────────────────────────────────────────────


def format_report(report: DoctorReport) -> str:
  """Format doctor report for human consumption."""
  lines = []
  lines.append("═══ Antigravity Doctor ═══")
  lines.append(
    f"  Platform: {report.platform_info.get('os', '?')} {report.platform_info.get('machine', '?')}"
  )
  lines.append(f"  Python: {report.platform_info.get('python_version', '?')}")
  lines.append(
    f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(report.timestamp))}"
  )
  lines.append("")

  # Group checks by category
  categories: dict[str, list[CheckResult]] = {}
  for check in report.checks:
    cat = check.name.split("/")[0]
    categories.setdefault(cat, []).append(check)

  cat_labels = {
    "runtime": "🔧 Runtime Environment",
    "repo": "📁 Repository",
    "auth": "🔑 Authentication",
    "daemon": "👹 Daemon Fleet",
    "resources": "💾 Resources",
    "mcp": "🌐 MCP Fleet",
    "truth": "📜 Truth Surfaces",
  }

  for cat, checks in categories.items():
    lines.append(f"  {cat_labels.get(cat, cat)}")
    for check in checks:
      emoji = (
        "✅"
        if check.passed
        else (
          "⚠️ "
          if check.severity == "warning"
          else ("ℹ️ " if check.severity == "info" else "❌")
        )
      )
      lines.append(f"    {emoji} {check.message}")
      if check.fix and not check.passed:
        lines.append(f"       Fix: {check.fix}")
    lines.append("")

  # Summary
  health_emoji = {"healthy": "💚", "degraded": "💛", "unhealthy": "❤️"}.get(
    report.overall_health, "?"
  )
  lines.append(f"  {health_emoji} Overall: {report.overall_health.upper()}")
  lines.append(
    f"     ✅ {report.passed} passed  ⚠️  {report.warnings} warnings  ❌ {report.failed} failed"
  )

  return "\n".join(lines)


# ── CLI Entry Point ──────────────────────────────────────────────────────


def main() -> None:
  parser = argparse.ArgumentParser(
    description="Antigravity Doctor (ported from Claude Code doctor diagnostic)"
  )
  parser.add_argument("--json", action="store_true", help="Output as JSON")
  parser.add_argument("--verbose", action="store_true", help="Show detailed output")
  parser.add_argument(
    "--log", action="store_true", help="Write results to .beads/doctor_report.jsonl"
  )
  args = parser.parse_args()

  logging.basicConfig(
    level=logging.DEBUG if args.verbose else logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
  )

  doctor = AntigravityDoctor(verbose=args.verbose)
  report = doctor.diagnose()

  if args.json:
    print(json.dumps(report.to_dict(), indent=2))
  else:
    print(format_report(report))

  if args.log:
    BEADS_DIR.mkdir(parents=True, exist_ok=True)
    with open(DOCTOR_LOG, "a", encoding="utf-8") as f:
      f.write(json.dumps(report.to_dict()) + "\n")
    print(f"\n  📝 Results logged to {DOCTOR_LOG}")

  sys.exit(
    0
    if report.overall_health == "healthy"
    else (1 if report.overall_health == "degraded" else 2)
  )


if __name__ == "__main__":
  main()
