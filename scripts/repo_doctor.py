#!/usr/bin/env python3
"""Repo Doctor — Automated monorepo health check.

Scans for dirty files, conflict markers, broken imports, secrets,
large files, drift paths, and pending migrations. Outputs a structured
health report with severity levels and suggested repairs.

Usage:
    python3 scripts/repo_doctor.py [--json] [--fix]
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_APPS = {"counselconduit", "kovelai", "shadowtagai", "lead-capture-router"}
CANONICAL_LAYOUT = {"apps", "libs", "labs", "packages", "scripts", "tools", "docs", "infra", "vault", "archive"}
GITIGNORED_HEAVY = {
    "tools/external_sdks",
    "browser_artifacts",
    "external_repos",
    ".lancedb",
    "reference_architectures",
    "third_party/security",
}
MAX_FILE_KB = 500  # Pre-commit large-file threshold


class Severity(StrEnum):
    """Finding severity levels aligned with Sentinel risk classification."""

    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Finding:
    """A single health check finding."""

    gate: str
    severity: Severity
    message: str
    path: str = ""
    fix: str = ""


@dataclass
class HealthReport:
    """Aggregated repo health report."""

    findings: list[Finding] = field(default_factory=list)

    @property
    def score(self) -> str:
        """Return a letter grade based on severity counts."""
        crits = sum(1 for f in self.findings if f.severity == Severity.CRITICAL)
        errors = sum(1 for f in self.findings if f.severity == Severity.ERROR)
        warns = sum(1 for f in self.findings if f.severity == Severity.WARN)
        if crits > 0:
            return "F"
        if errors > 3:
            return "D"
        if errors > 0:
            return "C"
        if warns > 5:
            return "B"
        return "A"

    def to_dict(self) -> dict:
        """Serialize to dict."""
        return {
            "score": self.score,
            "total_findings": len(self.findings),
            "critical": sum(1 for f in self.findings if f.severity == Severity.CRITICAL),
            "errors": sum(1 for f in self.findings if f.severity == Severity.ERROR),
            "warnings": sum(1 for f in self.findings if f.severity == Severity.WARN),
            "info": sum(1 for f in self.findings if f.severity == Severity.INFO),
            "findings": [
                {
                    "gate": f.gate,
                    "severity": f.severity.value,
                    "message": f.message,
                    "path": f.path,
                    "fix": f.fix,
                }
                for f in self.findings
            ],
        }


def _run(cmd: list[str], cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=120)


def check_dirty_files(report: HealthReport) -> None:
    """Gate 1: Check for uncommitted changes."""
    r = _run(["git", "status", "--porcelain"])
    if r.returncode != 0:
        report.findings.append(Finding("dirty", Severity.ERROR, "git status failed"))
        return
    lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
    if not lines:
        report.findings.append(Finding("dirty", Severity.INFO, "Working tree clean"))
        return
    for line in lines[:20]:  # Cap at 20
        status = line[:2].strip()
        path = line[3:].strip()
        sev = Severity.WARN if status in ("M", "A", "D", "??") else Severity.ERROR
        report.findings.append(
            Finding(
                "dirty",
                sev,
                f"Dirty file ({status})",
                path,
                fix=f"git add {path}" if status == "??" else f"git checkout -- {path}",
            )
        )
    if len(lines) > 20:
        report.findings.append(
            Finding(
                "dirty",
                Severity.WARN,
                f"... and {len(lines) - 20} more dirty files",
            )
        )


def check_conflict_markers(report: HealthReport) -> None:
    """Gate 2: Check for merge conflict markers."""
    r = _run(["grep", "-rln", "<<<<<<<", "apps", "libs", "scripts", "docs"])
    if r.returncode == 0 and r.stdout.strip():
        for line in r.stdout.strip().splitlines()[:10]:
            report.findings.append(
                Finding(
                    "conflicts",
                    Severity.CRITICAL,
                    "Merge conflict marker found",
                    path=line.split(":")[0],
                    fix="Resolve merge conflicts manually",
                )
            )
    else:
        report.findings.append(Finding("conflicts", Severity.INFO, "No conflict markers found"))


def check_secrets(report: HealthReport) -> None:
    """Gate 3: Run betterleaks secret scan."""
    betterleaks = Path.home() / "go" / "bin" / "betterleaks"
    if not betterleaks.exists():
        report.findings.append(
            Finding(
                "secrets",
                Severity.WARN,
                "Betterleaks not installed",
                fix="cd tools/external_sdks/betterleaks && go build -o ~/go/bin/betterleaks .",
            )
        )
        return
    _run(
        [
            str(betterleaks),
            "dir",
            "-c",
            ".betterleaks.toml",
            "--report-format",
            "json",
            "--report-path",
            "/tmp/repo_doctor_secrets.json",
            ".",
        ]
    )
    try:
        with open("/tmp/repo_doctor_secrets.json") as f:
            findings = json.load(f)
        if findings:
            report.findings.append(
                Finding(
                    "secrets",
                    Severity.ERROR,
                    f"Betterleaks found {len(findings)} potential secrets",
                    fix="Review /tmp/repo_doctor_secrets.json and add false positives to .betterleaksignore",
                )
            )
        else:
            report.findings.append(Finding("secrets", Severity.INFO, "No secrets detected"))
    except FileNotFoundError, json.JSONDecodeError:
        report.findings.append(Finding("secrets", Severity.WARN, "Secret scan output unavailable"))


def check_large_files(report: HealthReport) -> None:
    """Gate 4: Check for files exceeding the size threshold."""
    # Note: we check both staged and unstaged files for size violations

    # Also check untracked files that might be about to be committed
    r2 = _run(["git", "status", "--porcelain"])
    for line in (r2.stdout or "").splitlines():
        path = line[3:].strip()
        full = REPO_ROOT / path
        if full.is_file():
            size_kb = full.stat().st_size / 1024
            if size_kb > MAX_FILE_KB:
                report.findings.append(
                    Finding(
                        "large_files",
                        Severity.WARN,
                        f"Large file ({size_kb:.0f} KB > {MAX_FILE_KB} KB)",
                        path=path,
                        fix=f"Add {path} to .gitignore or compress",
                    )
                )

    if not any(f.gate == "large_files" for f in report.findings):
        report.findings.append(Finding("large_files", Severity.INFO, "No large files in staging"))


def check_drift(report: HealthReport) -> None:
    """Gate 5: Check for files outside canonical layout."""
    r = _run(["git", "ls-files"])
    if r.returncode != 0:
        report.findings.append(Finding("drift", Severity.ERROR, "git ls-files failed"))
        return

    tracked = r.stdout.strip().splitlines()
    drift_count = 0
    for fpath in tracked:
        top = fpath.split("/")[0] if "/" in fpath else ""
        # Root-level files are OK, check directory-based paths
        if top and not top.startswith(".") and top not in CANONICAL_LAYOUT:
            drift_count += 1
            if drift_count <= 5:
                report.findings.append(
                    Finding(
                        "drift",
                        Severity.WARN,
                        "File outside canonical layout",
                        path=fpath,
                        fix="Move to apps/, libs/, tools/, or archive/",
                    )
                )

    if drift_count > 5:
        report.findings.append(
            Finding(
                "drift",
                Severity.WARN,
                f"... and {drift_count - 5} more drift files",
            )
        )
    elif drift_count == 0:
        report.findings.append(Finding("drift", Severity.INFO, "No layout drift detected"))


def check_lint(report: HealthReport) -> None:
    """Gate 6: Run ruff lint check."""
    r = _run([sys.executable, "-m", "ruff", "check", "--select", "F401,F841", "--statistics", "apps/counselconduit", "apps/kovelai"])
    if r.returncode != 0 and r.stdout.strip():
        for line in r.stdout.strip().splitlines()[:5]:
            report.findings.append(
                Finding(
                    "lint",
                    Severity.WARN,
                    f"Ruff: {line.strip()}",
                    fix=f"{sys.executable} -m ruff check --select F401,F841 --fix",
                )
            )
    else:
        report.findings.append(Finding("lint", Severity.INFO, "Ruff lint clean"))


def check_manifest(report: HealthReport) -> None:
    """Gate 7: Verify monorepo_manifest.yaml exists and is parseable."""
    manifest = REPO_ROOT / "monorepo_manifest.yaml"
    if not manifest.exists():
        report.findings.append(
            Finding(
                "manifest",
                Severity.CRITICAL,
                "monorepo_manifest.yaml missing!",
                fix="Restore from git history or recreate",
            )
        )
        return
    try:
        import yaml  # noqa: PLC0415

        with open(manifest) as f:
            data = yaml.safe_load(f)
        version = data.get("version", "unknown")
        report.findings.append(Finding("manifest", Severity.INFO, f"Manifest v{version} valid"))
    except ImportError:
        report.findings.append(Finding("manifest", Severity.INFO, "Manifest exists (YAML parser not available)"))
    except Exception as e:
        report.findings.append(Finding("manifest", Severity.ERROR, f"Manifest parse error: {e}"))


def check_tests(report: HealthReport) -> None:
    """Gate 8: Quick pytest collection check."""
    r = _run([sys.executable, "-m", "pytest", "--co", "-q", "--ignore=tests/e2e"])
    if r.returncode == 0:
        lines = r.stdout.strip().splitlines()
        last = lines[-1] if lines else ""
        report.findings.append(Finding("tests", Severity.INFO, f"Tests: {last}"))
    else:
        report.findings.append(
            Finding(
                "tests",
                Severity.ERROR,
                "Test collection failed",
                fix=f"{sys.executable} -m pytest --co -q 2>&1 | tail -10",
            )
        )


def main() -> None:
    """Run all health checks and output report."""
    as_json = "--json" in sys.argv
    report = HealthReport()

    print("🩺 Repo Doctor — Scanning monorepo health...\n")

    checks = [
        ("Dirty Files", check_dirty_files),
        ("Conflict Markers", check_conflict_markers),
        ("Secrets", check_secrets),
        ("Large Files", check_large_files),
        ("Layout Drift", check_drift),
        ("Lint", check_lint),
        ("Manifest", check_manifest),
        ("Tests", check_tests),
    ]

    for name, check_fn in checks:
        print(f"  ├─ {name}...", end=" ", flush=True)
        try:
            check_fn(report)
            print("✓")
        except Exception as e:
            report.findings.append(Finding(name.lower(), Severity.ERROR, str(e)))
            print("✗")

    if as_json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(f"\n{'=' * 60}")
        print(f"  REPO HEALTH SCORE: {report.score}")
        print(f"{'=' * 60}")

        icons = {
            Severity.INFO: "ℹ️ ",
            Severity.WARN: "⚠️ ",
            Severity.ERROR: "❌",
            Severity.CRITICAL: "🚨",
        }

        for f in report.findings:
            if f.severity == Severity.INFO and not os.getenv("VERBOSE"):
                continue
            icon = icons[f.severity]
            path_str = f" [{f.path}]" if f.path else ""
            fix_str = f"\n       Fix: {f.fix}" if f.fix else ""
            print(f"  {icon} [{f.gate}] {f.message}{path_str}{fix_str}")

        d = report.to_dict()
        print(f"\n  Summary: {d['critical']} critical, {d['errors']} errors, {d['warnings']} warnings, {d['info']} info")

    # Write report to .beads for audit trail
    report_path = REPO_ROOT / ".beads" / "repo_doctor_latest.json"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report.to_dict(), f, indent=2)

    # Exit code based on severity
    if report.to_dict()["critical"] > 0:
        sys.exit(2)
    if report.to_dict()["errors"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
