#!/usr/bin/env python3
"""
Doctrine Critique Daemon — Ported from Claude Code's doctorDiagnostic.ts + config.ts

Grounded in:
  - Claude_Source_Code/utils/doctorDiagnostic.ts (626 lines, health diagnostics)
  - Claude_Source_Code/utils/config.ts (63K, configuration validation)
  - Claude_Source_Code/utils/doctorContextWarnings.ts (context drift detection)
  - Claude_Source_Code/utils/markdownConfigLoader.ts (21K, CLAUDE.md hierarchy)

Architecture:
  Audits AGENTS.md, GEMINI.md, and all SKILL.md files for doctrinal drift,
  contradictions, and staleness. Modeled after Claude Code's doctor diagnostic
  that checks installation health, config mismatches, and ripgrep status.

Usage:
  python scripts/doctrine_critique_daemon.py [--full] [--fix] [--json]

Integration:
  Scheduled via KAIROS daemon (daily 3-5AM window) or invoked manually.
  Results written to .beads/doctrine_audit.jsonl.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BEADS_DIR = PROJECT_ROOT / ".beads"
AUDIT_LOG = BEADS_DIR / "doctrine_audit.jsonl"

# Truth hierarchy from AGENTS.md canonical_truth_hierarchy
TRUTH_SURFACES = {
    "AGENTS.md": PROJECT_ROOT / ".ruler" / "AGENTS.md",
    "CLAUDE.md": PROJECT_ROOT / "CLAUDE.md",
    "GEMINI.md": PROJECT_ROOT / "GEMINI.md",
    "monorepo_manifest.yaml": PROJECT_ROOT / "monorepo_manifest.yaml",
    "antigravity-mcp-config.json": PROJECT_ROOT / "antigravity-mcp-config.json",
    "BUSINESS_CONTEXT_LOCKED.md": PROJECT_ROOT / "BUSINESS_CONTEXT_LOCKED.md",
    "RISK_REGISTER.md": PROJECT_ROOT / "RISK_REGISTER.md",
}

# Skill directories to audit
SKILL_DIRS = [
    PROJECT_ROOT / ".agents" / "skills",
    Path.home() / ".gemini" / "antigravity" / "skills",
]


# ── Diagnostic Types (from doctorDiagnostic.ts DiagnosticInfo) ────────────


@dataclass
class DoctrineWarning:
    """Maps to Claude Code's { issue: string; fix: string } pattern."""

    issue: str
    fix: str
    severity: str = "warning"  # info, warning, error, critical
    file: str = ""
    line: int = 0

    def to_dict(self) -> dict:
        return {
            "issue": self.issue,
            "fix": self.fix,
            "severity": self.severity,
            "file": self.file,
            "line": self.line,
        }


@dataclass
class DoctrineAuditResult:
    """
    Full audit result, modeled after doctorDiagnostic.ts DiagnosticInfo.
    """

    timestamp: float = field(default_factory=time.time)
    version: str = ""
    truth_surfaces_found: list[str] = field(default_factory=list)
    truth_surfaces_missing: list[str] = field(default_factory=list)
    warnings: list[DoctrineWarning] = field(default_factory=list)
    skill_count: int = 0
    skill_issues: list[DoctrineWarning] = field(default_factory=list)
    contradictions: list[DoctrineWarning] = field(default_factory=list)
    staleness_flags: list[DoctrineWarning] = field(default_factory=list)
    hash_fingerprint: str = ""

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "version": self.version,
            "truth_surfaces_found": self.truth_surfaces_found,
            "truth_surfaces_missing": self.truth_surfaces_missing,
            "warnings": [w.to_dict() for w in self.warnings],
            "skill_count": self.skill_count,
            "skill_issues": [w.to_dict() for w in self.skill_issues],
            "contradictions": [w.to_dict() for w in self.contradictions],
            "staleness_flags": [w.to_dict() for w in self.staleness_flags],
            "hash_fingerprint": self.hash_fingerprint,
            "total_issues": len(self.warnings) + len(self.skill_issues) + len(self.contradictions) + len(self.staleness_flags),
        }


# ── Audit Engine ─────────────────────────────────────────────────────────


class DoctrineCritiqueEngine:
    """
    Port of Claude Code's getDoctorDiagnostic() with additions for
    doctrinal drift detection specific to the AGNT ecosystem.

    Matches the Claude Code diagnostic pattern:
      1. Check installation type → check truth surface presence
      2. Detect multiple installations → detect contradictions
      3. Detect configuration issues → detect staleness + drift
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger("doctrine_critique")

    def run_full_audit(self) -> DoctrineAuditResult:
        """Execute the complete diagnostic pipeline."""
        result = DoctrineAuditResult()

        # Phase 1: Truth Surface Verification (maps to getCurrentInstallationType)
        self._check_truth_surfaces(result)

        # Phase 2: Version Extraction
        self._extract_version(result)

        # Phase 3: Configuration Issues (maps to detectConfigurationIssues)
        self._check_config_issues(result)

        # Phase 4: Contradiction Detection (maps to detectMultipleInstallations)
        self._check_contradictions(result)

        # Phase 5: Staleness Detection (maps to doctorContextWarnings)
        self._check_staleness(result)

        # Phase 6: Skill Fleet Audit
        self._audit_skills(result)

        # Phase 7: Generate fingerprint
        result.hash_fingerprint = self._generate_fingerprint(result)

        return result

    def _check_truth_surfaces(self, result: DoctrineAuditResult) -> None:
        """Verify all canonical truth surfaces exist."""
        for name, path in TRUTH_SURFACES.items():
            if path.exists():
                result.truth_surfaces_found.append(name)
            else:
                result.truth_surfaces_missing.append(name)
                result.warnings.append(
                    DoctrineWarning(
                        issue=f"Truth surface missing: {name}",
                        fix=f"Create or restore {path}",
                        severity="error",
                        file=str(path),
                    )
                )

    def _extract_version(self, result: DoctrineAuditResult) -> None:
        """Extract AGENTS.md version number."""
        agents_path = TRUTH_SURFACES.get("AGENTS.md")
        if agents_path and agents_path.exists():
            content = agents_path.read_text(encoding="utf-8", errors="replace")
            match = re.search(r"version:\s*([\d.]+)", content)
            if match:
                result.version = match.group(1)

    def _check_config_issues(self, result: DoctrineAuditResult) -> None:
        """
        Check for configuration issues across truth surfaces.
        Maps to detectConfigurationIssues() in doctorDiagnostic.ts.
        """
        # Check AGENTS.md and GEMINI.md version alignment
        versions: dict[str, str] = {}
        for name in ("AGENTS.md", "GEMINI.md"):
            path = TRUTH_SURFACES.get(name)
            if path and path.exists():
                content = path.read_text(encoding="utf-8", errors="replace")
                match = re.search(r"version:\s*([\d.]+)", content)
                if match:
                    versions[name] = match.group(1)

        if len(versions) == 2:
            v_agents = versions.get("AGENTS.md", "")
            v_gemini = versions.get("GEMINI.md", "")
            if v_agents != v_gemini:
                result.warnings.append(
                    DoctrineWarning(
                        issue=f"Version mismatch: AGENTS.md={v_agents}, GEMINI.md={v_gemini}",
                        fix="Synchronize version numbers across both files",
                        severity="warning",
                    )
                )

        # Check for prohibited patterns in doctrine files
        for name in ("AGENTS.md", "GEMINI.md"):
            path = TRUTH_SURFACES.get(name)
            if not (path and path.exists()):
                continue
            content = path.read_text(encoding="utf-8", errors="replace")

            # Check for .env references (banned per secrets_manager_doctrine)
            if re.search(r"\b\.env\b", content) and "DEPRECATED" not in content[:500]:
                result.warnings.append(
                    DoctrineWarning(
                        issue=f"{name} references .env files (banned since 2026-04-22)",
                        fix="Replace with scripts/load_mcp_secrets.sh references",
                        severity="warning",
                        file=str(path),
                    )
                )

            # Check for BullMQ references (banned per queue_doctrine)
            if "bullmq" in content.lower() or "bull" in content.lower():
                if "banned" not in content.lower():
                    result.warnings.append(
                        DoctrineWarning(
                            issue=f"{name} references BullMQ (banned — use Google Cloud Tasks)",
                            fix="Replace all queue references with Google Cloud Tasks",
                            severity="warning",
                            file=str(path),
                        )
                    )

    def _check_contradictions(self, result: DoctrineAuditResult) -> None:
        """
        Detect contradictions between truth surfaces.
        Maps to detectMultipleInstallations() pattern.
        """
        # Load content of primary truth surfaces
        contents: dict[str, str] = {}
        for name in ("AGENTS.md", "GEMINI.md"):
            path = TRUTH_SURFACES.get(name)
            if path and path.exists():
                contents[name] = path.read_text(encoding="utf-8", errors="replace")

        if len(contents) < 2:
            return

        agents = contents.get("AGENTS.md", "")
        gemini = contents.get("GEMINI.md", "")

        # Check for conflicting App IDs
        agents_app_ids = set(re.findall(r"App ID[:\s]*(\d+)", agents))
        gemini_app_ids = set(re.findall(r"App ID[:\s]*(\d+)", gemini))
        if agents_app_ids and gemini_app_ids and agents_app_ids != gemini_app_ids:
            result.contradictions.append(
                DoctrineWarning(
                    issue=f"App ID mismatch: AGENTS.md={agents_app_ids}, GEMINI.md={gemini_app_ids}",
                    fix="Ensure both files reference the same GitHub App ID",
                    severity="error",
                )
            )

        # Check for conflicting model references
        agents_models = set(re.findall(r"gemini-[\w.-]+", agents))
        gemini_models = set(re.findall(r"gemini-[\w.-]+", gemini))
        if agents_models and gemini_models and agents_models != gemini_models:
            diff = agents_models.symmetric_difference(gemini_models)
            if diff:
                result.contradictions.append(
                    DoctrineWarning(
                        issue=f"Model reference divergence: {diff}",
                        fix="Synchronize model references across truth surfaces",
                        severity="info",
                    )
                )

    def _check_staleness(self, result: DoctrineAuditResult) -> None:
        """
        Detect stale doctrine files.
        Maps to doctorContextWarnings.ts pattern.
        """
        now = time.time()
        stale_threshold = 7 * 24 * 3600  # 7 days

        for name, path in TRUTH_SURFACES.items():
            if not path.exists():
                continue
            mtime = path.stat().st_mtime
            age_days = (now - mtime) / 86400

            if age_days > 30:
                result.staleness_flags.append(
                    DoctrineWarning(
                        issue=f"{name} not modified in {age_days:.0f} days",
                        fix=f"Review and update {name} for currency",
                        severity="warning",
                        file=str(path),
                    )
                )
            elif age_days > stale_threshold / 86400:
                result.staleness_flags.append(
                    DoctrineWarning(
                        issue=f"{name} last modified {age_days:.1f} days ago",
                        fix="Consider reviewing for staleness",
                        severity="info",
                        file=str(path),
                    )
                )

    def _audit_skills(self, result: DoctrineAuditResult) -> None:
        """Audit all SKILL.md files for structural issues."""
        skill_count = 0
        for skill_dir in SKILL_DIRS:
            if not skill_dir.exists():
                continue
            for skill_path in skill_dir.rglob("SKILL.md"):
                skill_count += 1
                self._audit_single_skill(skill_path, result)

        result.skill_count = skill_count

    def _audit_single_skill(self, path: Path, result: DoctrineAuditResult) -> None:
        """Check a single SKILL.md for structural compliance."""
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError, PermissionError:
            return

        skill_name = path.parent.name

        # Check for YAML frontmatter
        if not content.startswith("---"):
            result.skill_issues.append(
                DoctrineWarning(
                    issue=f"Skill '{skill_name}' missing YAML frontmatter",
                    fix="Add --- delimited frontmatter with name and description",
                    severity="warning",
                    file=str(path),
                )
            )

        # Check for empty files
        if len(content.strip()) < 50:
            result.skill_issues.append(
                DoctrineWarning(
                    issue=f"Skill '{skill_name}' appears empty or stub ({len(content)} chars)",
                    fix="Populate with skill instructions or archive to _archive_redundant",
                    severity="warning",
                    file=str(path),
                )
            )

        # Check for name field in frontmatter
        if "---" in content:
            frontmatter = content.split("---")[1] if content.count("---") >= 2 else ""
            if "name:" not in frontmatter.lower() and "description:" not in frontmatter.lower():
                result.skill_issues.append(
                    DoctrineWarning(
                        issue=f"Skill '{skill_name}' frontmatter missing name/description",
                        fix="Add name: and description: fields to YAML frontmatter",
                        severity="info",
                        file=str(path),
                    )
                )

    def _generate_fingerprint(self, result: DoctrineAuditResult) -> str:
        """Generate a hash fingerprint of all truth surfaces for drift detection."""
        hasher = hashlib.sha256()
        for name in sorted(TRUTH_SURFACES.keys()):
            path = TRUTH_SURFACES[name]
            if path.exists():
                content = path.read_bytes()
                hasher.update(f"{name}:{len(content)}:".encode())
                hasher.update(content)
        return hasher.hexdigest()[:16]


# ── Output Formatters ────────────────────────────────────────────────────


def format_human_readable(result: DoctrineAuditResult) -> str:
    """Format audit results for human consumption."""
    lines = []
    lines.append("═══ Doctrine Critique Audit ═══")
    lines.append(f"  Version: {result.version or 'unknown'}")
    lines.append(f"  Fingerprint: {result.hash_fingerprint}")
    lines.append(f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result.timestamp))}")
    lines.append("")

    # Truth surfaces
    lines.append(f"  Truth Surfaces: {len(result.truth_surfaces_found)}/{len(TRUTH_SURFACES)} found")
    if result.truth_surfaces_missing:
        lines.append(f"  ⚠️  Missing: {', '.join(result.truth_surfaces_missing)}")
    lines.append("")

    # Skills
    lines.append(f"  Skills Audited: {result.skill_count}")
    lines.append("")

    # Issues summary
    all_issues = result.warnings + result.skill_issues + result.contradictions + result.staleness_flags

    severity_counts = {}
    for issue in all_issues:
        severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

    if all_issues:
        lines.append(f"  Issues Found: {len(all_issues)}")
        for sev, count in sorted(severity_counts.items()):
            emoji = {"critical": "⛔", "error": "🔴", "warning": "⚠️ ", "info": "ℹ️ "}.get(sev, "?")
            lines.append(f"    {emoji} {sev}: {count}")
        lines.append("")

        for issue in all_issues:
            emoji = {"critical": "⛔", "error": "🔴", "warning": "⚠️ ", "info": "ℹ️ "}.get(issue.severity, "?")
            lines.append(f"  {emoji} {issue.issue}")
            lines.append(f"     Fix: {issue.fix}")
            if issue.file:
                lines.append(f"     File: {issue.file}")
            lines.append("")
    else:
        lines.append("  ✅ No issues found — doctrine is healthy!")

    return "\n".join(lines)


# ── CLI Entry Point ──────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Doctrine Critique Daemon (ported from Claude Code doctorDiagnostic.ts)")
    parser.add_argument("--full", action="store_true", help="Run full audit (default)")
    parser.add_argument("--fix", action="store_true", help="Auto-fix simple issues")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--log", action="store_true", help="Write results to .beads/doctrine_audit.jsonl")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    engine = DoctrineCritiqueEngine()
    result = engine.run_full_audit()

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(format_human_readable(result))

    if args.log:
        BEADS_DIR.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(result.to_dict()) + "\n")
        print(f"\n  📝 Results logged to {AUDIT_LOG}")

    # Exit code: 0 if healthy, 1 if warnings, 2 if errors/critical
    total = result.to_dict()["total_issues"]
    has_critical = any(w.severity in ("error", "critical") for w in (result.warnings + result.contradictions))
    sys.exit(2 if has_critical else (1 if total > 0 else 0))


if __name__ == "__main__":
    main()
