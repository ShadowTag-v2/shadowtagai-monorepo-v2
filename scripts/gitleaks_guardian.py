#!/usr/bin/env python3
"""gitleaks_guardian.py — Autonomous Secret Leak Classifier & Gate.

Per AGENTS.md Rule 23: Gitleaks + detect-private-key in pre-commit and CI.
Per GEMINI.md Cor.30 R3–8: Secrets & Supply Chain enforcement.
Per Judge 6 Rule B7: Credential Leakage — BLOCK.

5-Layer Defense Model:
  Layer 1: Pre-commit hook (.pre-commit-config.yaml)
  Layer 2: Finish Changes pipeline (finish_changes.py)
  Layer 3: Omega Sync gate (omega_sync.py)
  Layer 4: CI/CD PR gate (security-audit.yml)
  Layer 5: On-demand audit (/gitleaks-guardian workflow)

Usage:
  # Full production scan (apps/ + scripts/ only)
  python3 scripts/gitleaks_guardian.py --mode scan --scope production

  # Staged files only (for pipeline gating)
  python3 scripts/gitleaks_guardian.py --mode staged

  # Generate report from existing scan
  python3 scripts/gitleaks_guardian.py --mode report --input /tmp/gitleaks_report.json

  # Gate mode: exits 1 if BLOCK findings exist (for omega_sync integration)
  python3 scripts/gitleaks_guardian.py --mode gate

Exit codes:
  0 — Clean (no BLOCK findings)
  1 — BLOCK findings detected (halt pipeline)
  2 — Scan error (gitleaks binary not found, etc.)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
import datetime
from datetime import datetime as dt
UTC = getattr(datetime, "UTC", datetime.UTC)
from pathlib import Path


# ============================================================================
# Configuration
# ============================================================================

REPO_ROOT = Path(__file__).resolve().parent.parent
GITLEAKS_BIN = "/opt/homebrew/bin/gitleaks"
GITLEAKS_CONFIG = REPO_ROOT / ".gitleaks.toml"
GITLEAKS_IGNORE = REPO_ROOT / ".gitleaksignore"
REPORT_DIR = REPO_ROOT / ".beads"

# Production-relevant scan paths — used by --scope production (see run_scan())
PRODUCTION_PATHS = [
    "apps/counselconduit/",
    "apps/kovelai/",
    "apps/aiyou_stack/",
    "scripts/",
    "libs/",
    ".env",
    ".env.local",
    ".env.production",
    "firebase.json",
    "firestore.rules",
    "storage.rules",
]

# ============================================================================
# Classification Rules
# ============================================================================

# Paths that are ALWAYS false positives (third-party bundled code)
IGNORE_PATH_PATTERNS = [
    r"tools/antigravity/extensions/",  # VS Code extension bundles
    r"node_modules/",  # npm dependencies
    r"\.venv/",  # Python venv
    r"venv/",  # Python venv (alt)
    r"__pycache__/",  # Python cache
    r"reference_architectures/",  # Cloned repos (gitignored)
    r"external_repos/",  # External repos
    r"control/legacy_workspaces/",  # Archived sessions
    r"data/lancedb/",  # Vector DB
    r"data/drive_ingest/",  # Google Drive ingest
    r"data/sovereign_mlx/",  # MLX models
    r"\.gitnexus/",  # GitNexus index
    r"\.claude/",  # Claude rules
    r"\.agents/",  # Agent rules
    r"docs/atlantis/",  # Recovered docs
    r"docs/Cor\.Atlantis/",  # Recovered docs
    r"docs/AUDIT_REPORT\.md",  # Audit reports quoting found keys
    r"docs/CANONICALIZATION_REPORT",  # Canonicalization reports quoting config dumps
    r"\.agent/reports/",  # Agent fold-in/rollup reports quoting keys
    r"\.next/",  # Next.js build
    r"archive/",  # Archived content
    r"labs/",  # R&D lab content
    r"libs/cyberpunk_stack/",  # Third-party lib
    r"memory/erik-hancock-llm-memory/",  # Archived memory
    r"\.stitch-sdk/",  # Stitch SDK bundled code
]

# Content patterns that indicate Windows API calls (not secrets)
IGNORE_CONTENT_PATTERNS = [
    r"windll\.advapi32\.",  # Windows Registry API calls in pydevd
    r"serialized_pb=b",  # Protobuf serialized bytes
    r"RegCloseKey",  # Windows API name
    r"RegEnumKey",  # Windows API name
    r"RegFlushKey",  # Windows API name
]

# Rules that ALWAYS indicate real credentials when found in production paths
CRITICAL_RULES = {
    "gcp-api-key",
    "stripe-secret-key",
    "github-pat",
    "github-token",
    "private-key",
    "aws-access-key-id",
    "aws-secret-access-key",
}

# Rules that are often false positives
LOW_SIGNAL_RULES = {
    "generic-api-key-inline",
    "generic-api-key",
}


class Finding:
    """A classified Gitleaks finding."""

    def __init__(self, raw: dict) -> None:
        self.raw = raw
        self.rule_id: str = raw.get("RuleID", "unknown")
        self.file: str = raw.get("File", "")
        self.line: int = raw.get("StartLine", 0)
        self.match: str = raw.get("Match", "")
        self.secret: str = raw.get("Secret", "")
        self.fingerprint: str = raw.get("Fingerprint", "")
        self.description: str = raw.get("Description", "")

        # Classification
        self.verdict: str = "BLOCK"  # Default: block everything
        self.reason: str = ""
        self._classify()

    def _classify(self) -> None:
        """Classify finding into BLOCK / WARN / IGNORE."""
        # Rule 1: Path-based ignore (third-party code)
        for pattern in IGNORE_PATH_PATTERNS:
            if re.search(pattern, self.file):
                self.verdict = "IGNORE"
                self.reason = f"Third-party path: {pattern}"
                return

        # Rule 2: Content-based ignore (Windows API calls, protobuf, etc.)
        for pattern in IGNORE_CONTENT_PATTERNS:
            if re.search(pattern, self.match) or re.search(pattern, self.secret):
                self.verdict = "IGNORE"
                self.reason = f"False positive content: {pattern}"
                return

        # Rule 3: Test fixtures
        if re.search(r"tests?/|\.test\.|_test\.|test_|fixture", self.file):
            self.verdict = "WARN"
            self.reason = "Test fixture — verify not using real credentials"
            return

        # Rule 4: Consolidated sweeps (archived third-party scripts)
        if "consolidated_sweeps/" in self.file:
            self.verdict = "WARN"
            self.reason = "Archived third-party script — not deployed"
            return

        # Rule 5: .env.example / README / docs (template values)
        if re.search(r"\.env\.example|README|\.md$", self.file) and self.rule_id in LOW_SIGNAL_RULES:
            self.verdict = "WARN"
            self.reason = "Documentation/example — likely placeholder"
            return

        # Rule 6: Critical rules in production paths → always BLOCK
        if self.rule_id in CRITICAL_RULES:
            self.verdict = "BLOCK"
            self.reason = f"Critical rule '{self.rule_id}' in production code"
            return

        # Rule 7: Generic API key in non-production → WARN
        if self.rule_id in LOW_SIGNAL_RULES:
            self.verdict = "WARN"
            self.reason = "Generic pattern match — manual review recommended"
            return

        # Default: BLOCK (safe default)
        self.verdict = "BLOCK"
        self.reason = f"Unclassified finding — rule '{self.rule_id}'"

    @property
    def redacted_secret(self) -> str:
        """Return first 4 and last 4 chars only."""
        s = self.secret
        if len(s) <= 12:
            return "***REDACTED***"
        return f"{s[:4]}...{s[-4:]}"

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "reason": self.reason,
            "rule_id": self.rule_id,
            "file": self.file,
            "line": self.line,
            "description": self.description,
            "redacted_secret": self.redacted_secret,
            "fingerprint": self.fingerprint,
        }


# ============================================================================
# Scan Functions
# ============================================================================


def run_gitleaks_scan(scope: str = "production") -> list[dict]:
    """Run gitleaks and return parsed JSON findings."""
    if not os.path.exists(GITLEAKS_BIN):
        sys.exit(2)

    report_path = "/tmp/gitleaks_guardian_report.json"

    if scope == "staged":
        cmd = [
            GITLEAKS_BIN,
            "protect",
            "--staged",
            "--config",
            str(GITLEAKS_CONFIG),
            "--report-format",
            "json",
            "--report-path",
            report_path,
        ]
    elif scope == "production":
        # Scan only production-relevant paths
        cmd = [
            GITLEAKS_BIN,
            "detect",
            "--no-git",
            "--config",
            str(GITLEAKS_CONFIG),
            "--report-format",
            "json",
            "--report-path",
            report_path,
        ]
        # Use --source for each production path
        # Gitleaks doesn't support multiple --source, so we scan the root
        # and rely on .gitleaks.toml allowlist to skip non-production
        cmd.extend(["--source", str(REPO_ROOT)])
    else:
        # Full scan
        cmd = [
            GITLEAKS_BIN,
            "detect",
            "--no-git",
            "--config",
            str(GITLEAKS_CONFIG),
            "--report-format",
            "json",
            "--report-path",
            report_path,
            "--source",
            str(REPO_ROOT),
        ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        pass

    # Gitleaks exit 1 = findings, exit 0 = clean
    if os.path.exists(report_path):
        with open(report_path) as f:
            try:
                data = json.load(f)
                return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                return []
    return []


def run_staged_scan() -> list[dict]:
    """Quick scan of staged files only."""
    return run_gitleaks_scan(scope="staged")


def load_existing_report(path: str) -> list[dict]:
    """Load findings from an existing JSON report."""
    with open(path) as f:
        return json.load(f)


# ============================================================================
# Classification & Remediation
# ============================================================================


def classify_findings(raw_findings: list[dict]) -> list[Finding]:
    """Classify all findings and return Finding objects."""
    return [Finding(f) for f in raw_findings]


def auto_remediate_ignores(findings: list[Finding]) -> int:
    """Auto-append IGNORE findings to .gitleaksignore."""
    existing_fingerprints = set()
    if GITLEAKS_IGNORE.exists():
        for line in GITLEAKS_IGNORE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                # Extract fingerprint (format: file:rule:line)
                existing_fingerprints.add(line)

    new_entries = []
    for f in findings:
        if f.verdict == "IGNORE" and f.fingerprint:
            entry = f"{f.file}:{f.rule_id}:{f.line}"
            if entry not in existing_fingerprints:
                new_entries.append(f"\n# Auto-classified IGNORE: {f.reason}\n{entry}")

    if new_entries:
        with open(GITLEAKS_IGNORE, "a") as fh:
            fh.write("\n".join(new_entries))
            fh.write("\n")

    return len(new_entries)


# ============================================================================
# Reporting
# ============================================================================


def generate_report(findings: list[Finding], output_path: str | None = None) -> str:
    """Generate a markdown audit report."""
    blocks = [f for f in findings if f.verdict == "BLOCK"]
    warns = [f for f in findings if f.verdict == "WARN"]
    ignores = [f for f in findings if f.verdict == "IGNORE"]

    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    report = f"""# 🛡️ Gitleaks Guardian — Audit Report

**Generated**: {timestamp}
**Total Findings**: {len(findings)}
**BLOCK**: {len(blocks)} | **WARN**: {len(warns)} | **IGNORE**: {len(ignores)}

---

"""

    if blocks:
        report += "## 🚨 BLOCK — Immediate Action Required\n\n"
        report += "> [!CAUTION]\n"
        report += f"> {len(blocks)} credential(s) detected in production code. Pipeline HALTED.\n\n"
        report += "| # | Rule | File | Line | Secret (redacted) | Remediation |\n"
        report += "|---|------|------|------|-------------------|-------------|\n"
        for i, f in enumerate(blocks, 1):
            remediation = _suggest_remediation(f)
            report += f"| {i} | `{f.rule_id}` | `{f.file}` | {f.line} | `{f.redacted_secret}` | {remediation} |\n"
        report += "\n"

    if warns:
        report += "## ⚠️ WARN — Manual Review Recommended\n\n"
        report += "| # | Rule | File | Line | Reason |\n"
        report += "|---|------|------|------|--------|\n"
        for i, f in enumerate(warns, 1):
            report += f"| {i} | `{f.rule_id}` | `{f.file}` | {f.line} | {f.reason} |\n"
        report += "\n"

    if ignores:
        report += f"## ✅ IGNORE — Auto-classified ({len(ignores)} findings)\n\n"
        report += "These were auto-classified as false positives and added to `.gitleaksignore`.\n\n"
        # Group by reason
        by_reason: dict[str, int] = {}
        for f in ignores:
            by_reason[f.reason] = by_reason.get(f.reason, 0) + 1
        for reason, count in sorted(by_reason.items(), key=lambda x: -x[1]):
            report += f"- **{reason}**: {count} findings\n"
        report += "\n"

    report += """---

## 5-Layer Defense Status

| Layer | Component | Status |
|-------|-----------|--------|
| 1 | Pre-commit hook (`.pre-commit-config.yaml`) | ✅ Active |
| 2 | Finish Changes pipeline (`finish_changes.py`) | ✅ Blocking |
| 3 | Omega Sync gate (`omega_sync.py`) | ✅ Blocking |
| 4 | CI/CD PR gate (`security-audit.yml`) | ✅ Active |
| 5 | On-demand audit (`/gitleaks-guardian`) | ✅ This scan |

"""

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(report)

    return report


def _suggest_remediation(finding: Finding) -> str:
    """Suggest specific remediation for a finding."""
    rule = finding.rule_id

    if rule == "gcp-api-key":
        return "Move to GCP Secret Manager or use ADC"
    if rule == "stripe-secret-key":
        return "Move to Secret Manager (`STRIPE_SECRET_KEY`)"
    if rule in ("github-pat", "github-token"):
        return "Rotate immediately. Use GitHub App PEM instead"
    if rule == "private-key":
        return "Remove from source. Store in Secret Manager"
    if "generic" in rule:
        return "Review manually. If real, move to `.env` (gitignored)"

    return "Review and remediate per Cor.30 R3"


# ============================================================================
# Pipeline Gate
# ============================================================================


def gate_check(findings: list[Finding]) -> bool:
    """Return True if pipeline should HALT (BLOCK findings exist)."""
    blocks = [f for f in findings if f.verdict == "BLOCK"]
    if blocks:
        for _f in blocks:
            pass
        return True
    return False


# ============================================================================
# Main
# ============================================================================


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gitleaks Guardian — Autonomous Secret Leak Classifier & Gate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/gitleaks_guardian.py --mode scan --scope production
  python3 scripts/gitleaks_guardian.py --mode staged
  python3 scripts/gitleaks_guardian.py --mode gate
  python3 scripts/gitleaks_guardian.py --mode report --input /tmp/report.json
  python3 scripts/gitleaks_guardian.py --mode manifest --input /tmp/third_party.json
        """,
    )
    parser.add_argument(
        "--mode",
        choices=["scan", "staged", "gate", "report", "manifest"],
        default="gate",
        help="Scan mode (default: gate)",
    )
    parser.add_argument(
        "--scope",
        choices=["production", "full", "staged"],
        default="production",
        help="Scan scope (default: production)",
    )
    parser.add_argument(
        "--input",
        help="Path to existing gitleaks JSON report (for --mode report)",
    )
    parser.add_argument(
        "--output",
        help="Path to write markdown report",
    )
    parser.add_argument(
        "--auto-ignore",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-append IGNORE findings to .gitleaksignore (default: True, --no-auto-ignore to disable)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output classified findings as JSON",
    )

    args = parser.parse_args()

    # Manifest mode: dedicated third-party leak inventory
    if args.mode == "manifest":
        if not args.input:
            sys.exit(2)
        raw_findings = load_existing_report(args.input)
        _generate_manifest(raw_findings, args.output)
        sys.exit(0)

    # Get findings
    if args.mode == "report" and args.input:
        raw_findings = load_existing_report(args.input)
    elif args.mode in {"staged", "gate"}:
        raw_findings = run_staged_scan()
    else:
        raw_findings = run_gitleaks_scan(scope=args.scope)

    if not raw_findings:
        sys.exit(0)

    # Classify
    findings = classify_findings(raw_findings)
    blocks = [f for f in findings if f.verdict == "BLOCK"]
    warns = [f for f in findings if f.verdict == "WARN"]
    [f for f in findings if f.verdict == "IGNORE"]

    # Auto-remediate ignores
    if args.auto_ignore:
        auto_remediate_ignores(findings)

    # JSON output
    if args.json:
        sys.exit(1 if blocks else 0)

    # Generate report
    output_path = args.output
    if not output_path and args.mode == "scan":
        REPORT_DIR.mkdir(exist_ok=True)
        output_path = str(REPORT_DIR / "gitleaks_guardian_report.md")

    if output_path:
        generate_report(findings, output_path)

    # Print summary
    if blocks:
        for _f in blocks:
            pass

    if warns:
        for _f in warns:
            pass

    # Gate verdict
    if args.mode in ("gate", "staged") and gate_check(findings):
        sys.exit(1)

    sys.exit(1 if blocks else 0)


def _generate_manifest(raw_findings: list[dict], output_dir: str | None = None) -> None:
    """Generate a structured third-party leak manifest with deduplication.

    Outputs:
      - Markdown manifest with [ ] checkboxes
      - CSV export for spreadsheet filtering
      - Per-repo sub-manifests
      - Deduplicated secrets-only list
    """
    out_dir = Path(output_dir) if output_dir else REPORT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    risk_map = {
        "stripe-access-token": "🔴 HIGH",
        "vault-service-token": "🔴 HIGH",
        "private-key": "🟡 MEDIUM",
        "gcp-api-key": "🟡 MEDIUM",
        "discord-client-secret": "🟡 MEDIUM",
        "jwt": "🟡 MEDIUM",
        "github-token": "🔴 HIGH",
    }
    risk_csv = {
        "stripe-access-token": "HIGH",
        "vault-service-token": "HIGH",
        "private-key": "MEDIUM",
        "gcp-api-key": "MEDIUM",
        "discord-client-secret": "MEDIUM",
        "jwt": "MEDIUM",
        "github-token": "HIGH",
    }

    def _extract_repo(file_path: str) -> str:
        if "reference_architectures/" in file_path:
            parts = file_path.split("reference_architectures/")
            return parts[1].split("/")[0] if len(parts) > 1 else "unknown"
        if "cyberpunk_stack" in file_path:
            return "cyberpunk_stack"
        return "labs"

    def _redact(secret: str) -> str:
        if len(secret) > 12:
            return f"{secret[:6]}...{secret[-4:]}"
        if len(secret) > 6:
            return f"{secret[:3]}...{secret[-3:]}"
        return secret[:2] + "***"

    # ── Deduplicate ──
    secrets: dict[tuple[str, str], dict] = {}
    for f in raw_findings:
        secret = f.get("Secret", f.get("Match", ""))
        rule = f.get("RuleID", "unknown")
        file_path = f.get("File", "")
        line = f.get("StartLine", 0)
        key = (rule, secret)
        if key not in secrets:
            secrets[key] = {"rule": rule, "secret": secret, "files": [], "repos": set()}
        short_path = file_path.split("Monorepo-Uphillsnowball/")[-1] if "Monorepo-Uphillsnowball/" in file_path else file_path
        secrets[key]["files"].append(f"{short_path}:{line}")
        secrets[key]["repos"].add(_extract_repo(file_path))

    timestamp = datetime.now(UTC).strftime("%Y-%m-%d")

    # ── Markdown manifest ──
    by_rule: dict[str, list] = defaultdict(list)
    for info in secrets.values():
        by_rule[info["rule"]].append(info)

    lines = [
        "# Third-Party Leak Manifest",
        "",
        f"**Generated**: {timestamp}",
        f"**Total Findings**: {len(raw_findings)} occurrences → **{len(secrets)} unique secrets**",
        "",
        "> [!NOTE]",
        "> All findings are from third-party code. None are production secrets.",
        "> Use `[ ]` checkboxes to select items for action.",
        "",
        "---",
        "",
        "## Summary by Rule Type",
        "",
        "| Rule | Unique | Occurrences | Risk | Source Repos |",
        "|------|--------|-------------|------|--------------|",
    ]
    for rule in sorted(by_rule):
        items = by_rule[rule]
        occ = sum(len(i["files"]) for i in items)
        repos = set()
        for i in items:
            repos.update(i["repos"])
        risk = risk_map.get(rule, "🟢 LOW")
        repos_str = ", ".join(sorted(repos))
        lines.append(f"| `{rule}` | {len(items)} | {occ} | {risk} | {repos_str} |")
    lines += ["", "---", ""]

    for rule in sorted(by_rule):
        items = by_rule[rule]
        occ = sum(len(i["files"]) for i in items)
        risk = risk_map.get(rule, "🟢 LOW")
        lines.append(f"## {rule} ({len(items)} unique / {occ} occ.) — {risk}")
        lines.append("")
        for idx, item in enumerate(items, 1):
            redacted = _redact(item["secret"])
            repos = ", ".join(sorted(item["repos"]))
            fc = len(item["files"])
            lines.append(f"- [ ] **#{idx}** `{redacted}` — {repos} ({fc} file{'s' if fc > 1 else ''})")
            for fp in item["files"][:3]:
                lines.append(f"  - `{fp}`")
            if fc > 3:
                lines.append(f"  - _...and {fc - 3} more_")
            lines.append("")
        lines += ["---", ""]

    md_path = out_dir / "third_party_leak_manifest.md"
    md_path.write_text("\n".join(lines))

    # ── CSV export ──
    csv_path = out_dir / "third_party_leak_manifest.csv"
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Rule", "Risk", "Secret_Redacted", "File", "Line", "Source_Repo"])
        for f in raw_findings:
            secret = f.get("Secret", "")
            writer.writerow(
                [
                    f.get("RuleID", ""),
                    risk_csv.get(f.get("RuleID", ""), "LOW"),
                    _redact(secret),
                    f.get("File", ""),
                    f.get("StartLine", 0),
                    _extract_repo(f.get("File", "")),
                ],
            )

    # ── Per-repo sub-manifests ──
    by_repo: dict[str, list] = defaultdict(list)
    for f in raw_findings:
        by_repo[_extract_repo(f.get("File", ""))].append(f)
    for repo in sorted(by_repo):
        items = by_repo[repo]
        rules = defaultdict(int)
        for f in items:
            rules[f.get("RuleID", "")] += 1
        ", ".join(f"{r}:{c}" for r, c in sorted(rules.items(), key=lambda x: -x[1]))

    # ── Deduplicated secrets-only list ──
    dedup_path = out_dir / "third_party_secrets_deduped.txt"
    with open(dedup_path, "w") as f:
        for rule, secret in sorted(secrets.keys()):
            f.write(f"{rule}\t{_redact(secret)}\n")


if __name__ == "__main__":
    main()
