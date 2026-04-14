#!/usr/bin/env python3
"""ArchLint: Detects GPU/CPU sync issues and dtype problems
Catches .item(), .to(device) ordering, etc.

Part of Dual-Model CI Pipeline
Cost: $0 (local regex)
"""

import re
import subprocess
import sys
from pathlib import Path

RULES = [
    {
        "name": "gpu_cpu_sync",
        "pattern": r"\.item\(\)",
        "message": "GPU→CPU sync detected. Use .detach() if possible, or ensure this is intentional.",
        "severity": "warning",
        "context": "Calling .item() forces GPU→CPU synchronization which can hurt performance in tight loops.",
    },
    {
        "name": "dtype_cast_order",
        "pattern": r"\.to\(device\)\.to\(['\"]?(float|half|int|double|bfloat)",
        "message": "dtype cast after device move. Cast dtype first for efficiency.",
        "severity": "warning",
        "context": "Moving to device then casting dtype wastes memory. Cast dtype first: tensor.to(dtype).to(device)",
    },
    {
        "name": "cuda_sync_in_loop",
        "pattern": r"for\s+.*:\s*\n(?:.*\n)*?.*\.cuda\(\)",
        "message": "CUDA transfer inside loop. Move outside loop if possible.",
        "severity": "warning",
        "context": "Repeated .cuda() calls in loops can severely impact performance.",
    },
    {
        "name": "hardcoded_cuda",
        "pattern": r"\.to\(['\"]cuda['\"](?:\)|:)",
        "message": "Hardcoded 'cuda' device. Use torch.device() or config for flexibility.",
        "severity": "info",
        "context": "Hardcoding 'cuda' breaks on CPU-only systems. Use a device variable.",
    },
    {
        "name": "no_grad_missing",
        "pattern": r"model\.eval\(\)\s*\n(?:(?!torch\.no_grad|with\s+torch\.no_grad).)*\n.*model\(",
        "message": "eval() without no_grad() context nearby.",
        "severity": "info",
        "context": "Using eval() without no_grad() still builds computation graphs, wasting memory during inference.",
    },
    {
        "name": "secrets_in_code",
        "pattern": r"(?:api_key|password|secret|token)\s*=\s*['\"][^'\"]{8,}['\"]",
        "message": "Potential hardcoded secret detected.",
        "severity": "critical",
        "context": "Never hardcode secrets. Use environment variables or secret managers.",
    },
    {
        "name": "sql_injection",
        "pattern": r"f['\"].*(?:SELECT|INSERT|UPDATE|DELETE).*\{.*\}",
        "message": "Potential SQL injection via f-string.",
        "severity": "critical",
        "context": "Use parameterized queries instead of string formatting for SQL.",
    },
    {
        "name": "eval_usage",
        "pattern": r"\beval\s*\(",
        "message": "eval() usage detected - potential security risk.",
        "severity": "warning",
        "context": "eval() can execute arbitrary code. Use ast.literal_eval() for safe parsing or avoid entirely.",
    },
]


def get_changed_files(diff_range: str) -> list:
    """Get list of changed Python files."""
    try:
        result = subprocess.run(
            ["git", "diff", diff_range, "--name-only"], capture_output=True, text=True, check=True,
        )
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        return [f for f in files if f.endswith(".py")]
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Git diff failed: {e}", file=sys.stderr)
        return []


def check_file(filepath: str) -> list:
    """Check a single file against all rules."""
    issues = []

    try:
        path = Path(filepath)
        if not path.exists():
            return []

        content = path.read_text()
        lines = content.split("\n")

        for rule in RULES:
            # Use MULTILINE and DOTALL for multi-line patterns
            flags = re.MULTILINE | re.IGNORECASE
            if "\\n" in rule["pattern"]:
                flags |= re.DOTALL

            for match in re.finditer(rule["pattern"], content, flags):
                # Calculate line number
                line_no = content[: match.start()].count("\n") + 1

                # Get the matched line for context
                matched_line = lines[line_no - 1] if line_no <= len(lines) else ""

                issues.append(
                    {
                        "file": filepath,
                        "line": line_no,
                        "rule": rule["name"],
                        "message": rule["message"],
                        "severity": rule["severity"],
                        "context": rule.get("context", ""),
                        "matched": matched_line.strip()[:80],
                    },
                )

    except Exception as e:
        print(f"⚠️  Error checking {filepath}: {e}", file=sys.stderr)

    return issues


def main(diff_range: str = "origin/main...HEAD"):
    """Run ArchLint on changed files."""
    files = get_changed_files(diff_range)

    if not files:
        print("✅ No Python files changed")
        return

    print(f"Checking {len(files)} Python file(s)...")

    all_issues = []
    for filepath in files:
        issues = check_file(filepath)
        all_issues.extend(issues)

    # Group and display issues
    critical_count = 0
    warning_count = 0
    info_count = 0

    for issue in all_issues:
        severity = issue["severity"]
        emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}[severity]

        if severity == "critical":
            critical_count += 1
        elif severity == "warning":
            warning_count += 1
        else:
            info_count += 1

        print(f"\n{emoji} {issue['file']}:{issue['line']} [{issue['rule']}]")
        print(f"   {issue['message']}")
        if issue.get("matched"):
            print(f"   Code: {issue['matched']}")
        if issue.get("context"):
            print(f"   ℹ️  {issue['context']}")

    # Summary
    print(f"\n{'─' * 60}")
    print(f"Summary: {critical_count} critical, {warning_count} warnings, {info_count} info")

    # Fail on critical issues
    if critical_count > 0:
        print(f"\n❌ FAILED: {critical_count} critical issue(s) found")
        sys.exit(1)

    if warning_count > 0:
        print(f"\n⚠️  PASSED with {warning_count} warning(s)")
    else:
        print("\n✅ PASSED: No issues found")


if __name__ == "__main__":
    diff_range = sys.argv[1] if len(sys.argv) > 1 else "origin/main...HEAD"
    main(diff_range)
