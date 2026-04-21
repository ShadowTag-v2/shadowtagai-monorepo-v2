#!/usr/bin/env python3
"""Cor.30 Security Audit — Phase 2.5 New Files.

Validates security compliance of recently added files against
the Cor.30 Anti-Vibe Security Enforcer checklist.

Usage:
    python scripts/security_audit_phase25.py
"""

from __future__ import annotations

import ast
import os
import re
import sys

# Files to audit
AUDIT_FILES = [
    "apps/counselconduit/api/gdpr.py",
    "apps/counselconduit/api/sandbox_router.py",
    "apps/counselconduit/api/fastapi_kovel_enclave.py",
    "tests/unit/test_rate_limiting.py",
    "tests/unit/test_cloud_tasks_scheduling.py",
    "tests/integration/test_hard_delete_cascade.py",
    "tests/e2e/test_billing_flow.py",
]

# Security patterns to check
CHECKS = {
    "no_hardcoded_keys": {
        "pattern": r'(sk_live_|sk_test_|AIza|AKIA|ghp_|gho_|glpat-)',
        "severity": "CRITICAL",
        "description": "Hardcoded API keys detected",
    },
    "no_eval_exec": {
        "pattern": r'\beval\s*\(|\bexec\s*\(',
        "severity": "HIGH",
        "description": "Dynamic code execution (eval/exec)",
    },
    "no_sql_concat": {
        "pattern": r'f".*SELECT.*\{|f".*INSERT.*\{|f".*UPDATE.*\{|f".*DELETE.*\{',
        "severity": "CRITICAL",
        "description": "SQL injection via f-string concatenation",
    },
    "no_pickle": {
        "pattern": r'\bpickle\.loads?\b',
        "severity": "HIGH",
        "description": "Unsafe deserialization (pickle)",
    },
    "no_shell_true": {
        "pattern": r'subprocess\.\w+\(.*shell\s*=\s*True',
        "severity": "HIGH",
        "description": "Shell injection via subprocess(shell=True)",
    },
    "no_debug_true": {
        "pattern": r'debug\s*=\s*True',
        "severity": "MEDIUM",
        "description": "Debug mode enabled in production",
    },
    "input_validation": {
        "pattern": r'BaseModel|Field\(|validator|field_validator',
        "severity": "INFO",
        "description": "Input validation present (Pydantic)",
        "want_match": True,
    },
}


def audit_file(filepath: str) -> list[dict]:
    """Audit a single file against security patterns."""
    findings = []

    if not os.path.exists(filepath):
        findings.append({
            "file": filepath,
            "severity": "WARNING",
            "check": "file_exists",
            "message": "File not found",
            "line": 0,
        })
        return findings

    with open(filepath) as f:
        content = f.read()
        lines = content.split("\n")

    for check_name, check in CHECKS.items():
        want_match = check.get("want_match", False)
        matches = list(re.finditer(check["pattern"], content, re.IGNORECASE))

        if want_match and not matches:
            findings.append({
                "file": filepath,
                "severity": "WARNING",
                "check": check_name,
                "message": f"Missing: {check['description']}",
                "line": 0,
            })
        elif not want_match and matches:
            for m in matches:
                line_num = content[:m.start()].count("\n") + 1
                findings.append({
                    "file": filepath,
                    "severity": check["severity"],
                    "check": check_name,
                    "message": check["description"],
                    "line": line_num,
                })

    return findings


def main():
    print("=" * 72)
    print("Cor.30 Security Audit — Phase 2.5 Files")
    print("=" * 72)

    all_findings = []
    for filepath in AUDIT_FILES:
        findings = audit_file(filepath)
        all_findings.extend(findings)

    # Report
    critical = [f for f in all_findings if f["severity"] == "CRITICAL"]
    high = [f for f in all_findings if f["severity"] == "HIGH"]
    medium = [f for f in all_findings if f["severity"] == "MEDIUM"]
    warnings = [f for f in all_findings if f["severity"] == "WARNING"]

    for f in all_findings:
        icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "WARNING": "⚠️", "INFO": "ℹ️"}.get(f["severity"], "•")
        print(f"{icon} [{f['severity']}] {f['file']}:{f['line']} — {f['message']}")

    print()
    print(f"Files audited: {len(AUDIT_FILES)}")
    print(f"Critical: {len(critical)} | High: {len(high)} | Medium: {len(medium)} | Warnings: {len(warnings)}")

    if critical:
        print("\n🔴 AUDIT FAILED — Critical findings must be resolved before deploy")
        sys.exit(1)
    elif high:
        print("\n🟠 AUDIT WARNING — High-severity findings should be reviewed")
        sys.exit(0)
    else:
        print("\n✅ AUDIT PASSED — No critical or high-severity findings")
        sys.exit(0)


if __name__ == "__main__":
    main()
