#!/usr/bin/env python3
"""
CodePMCS CLI - Command line interface for GitHub Actions and local use.

Usage:
    python -m codepmcs.cli scan [--format=json|sarif] [path]
    python -m codepmcs.cli fix [--auto-commit] [path]
    python -m codepmcs.cli pr [path]
    python -m codepmcs.cli full [path]
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from . import CodePMCS
from .scanner import CodeScanner, ScanResult


def parse_args():
    parser = argparse.ArgumentParser(
        description="CodePMCS - AI-Powered Code Quality Platform",
        prog="codepmcs",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan repository for issues")
    scan_parser.add_argument("path", nargs="?", default=".", help="Repository path")
    scan_parser.add_argument(
        "--format",
        choices=["json", "sarif", "text"],
        default="text",
        help="Output format",
    )
    scan_parser.add_argument(
        "--rules",
        nargs="+",
        default=["security", "quality", "style"],
        help="Rules to apply",
    )
    scan_parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: stdout)",
    )

    # Fix command
    fix_parser = subparsers.add_parser("fix", help="Generate and apply fixes")
    fix_parser.add_argument("path", nargs="?", default=".", help="Repository path")
    fix_parser.add_argument(
        "--auto-commit",
        action="store_true",
        help="Automatically commit fixes",
    )
    fix_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show fixes without applying",
    )

    # PR command
    pr_parser = subparsers.add_parser("pr", help="Create PR with fixes")
    pr_parser.add_argument("path", nargs="?", default=".", help="Repository path")
    pr_parser.add_argument("--title", help="PR title")

    # Full pipeline command
    full_parser = subparsers.add_parser("full", help="Run full scan -> fix -> PR pipeline")
    full_parser.add_argument("path", nargs="?", default=".", help="Repository path")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check CodePMCS status")

    return parser.parse_args()


async def cmd_scan(args):
    """Execute scan command."""
    scanner = CodeScanner()
    result = await scanner.scan(args.path, args.rules)

    if args.format == "json":
        output = json.dumps(result.to_dict(), indent=2)
    elif args.format == "sarif":
        output = json.dumps(result.to_sarif(), indent=2)
    else:
        output = format_scan_text(result)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Results written to {args.output}")
    else:
        print(output)

    # Exit with error if critical/high issues found
    if result.critical_count > 0 or result.high_count > 0:
        return 1
    return 0


def format_scan_text(result: ScanResult) -> str:
    """Format scan result as human-readable text."""
    lines = [
        "=" * 60,
        "CodePMCS Scan Results",
        "=" * 60,
        f"Repository: {result.repo_path}",
        f"Scan ID: {result.scan_id}",
        f"Files scanned: {result.files_scanned}",
        f"Duration: {result.scan_duration_ms:.0f}ms",
        "",
        f"Issues found: {len(result.issues)}",
        f"  Critical: {result.critical_count}",
        f"  High: {result.high_count}",
        "",
    ]

    if result.issues:
        lines.append("Issues:")
        lines.append("-" * 60)

        for issue in result.issues:
            severity_emoji = {
                "critical": "",
                "high": "",
                "medium": "",
                "low": "",
                "info": "",
            }.get(issue.severity.value, "")

            lines.extend(
                [
                    f"{severity_emoji} [{issue.severity.value.upper()}] {issue.title}",
                    f"   File: {issue.file_path}:{issue.line_start}",
                    f"   {issue.description}",
                    "",
                ]
            )

    lines.append("=" * 60)
    return "\n".join(lines)


async def cmd_fix(args):
    """Execute fix command."""
    codepmcs = CodePMCS()

    # First scan
    print("Scanning repository...")
    scan_result = await codepmcs.scan(args.path)

    if not scan_result.issues:
        print("No issues found!")
        return 0

    print(f"Found {len(scan_result.issues)} issues")

    # Generate fixes
    print("Generating fixes...")
    remediation = await codepmcs.remediate(scan_result, auto_fix=not args.dry_run)

    if args.dry_run:
        print("\nDry run - fixes not applied:")
        for fix in remediation.fixes:
            print(f"  - {fix.issue_id}: {fix.description} (confidence: {fix.confidence:.0%})")
        return 0

    # Apply fixes
    if remediation.fixes:
        print(f"Generated {len(remediation.fixes)} fixes")
        applied = await codepmcs.remediator.apply_fixes(remediation, args.path)
        applied_count = sum(1 for v in applied.values() if v)
        print(f"Applied {applied_count} fixes")

        if args.auto_commit:
            import subprocess

            subprocess.run(["git", "add", "-A"], cwd=args.path)
            subprocess.run(
                ["git", "commit", "-m", "CodePMCS: Auto-fix code quality issues"],
                cwd=args.path,
            )
            print("Changes committed")

    return 0


async def cmd_pr(args):
    """Execute PR command."""
    codepmcs = CodePMCS()

    print("Running full pipeline: scan -> fix -> PR")

    # Scan
    scan_result = await codepmcs.scan(args.path)
    if not scan_result.issues:
        print("No issues found!")
        return 0

    # Remediate
    remediation = await codepmcs.remediate(scan_result)
    if not remediation.fixes:
        print("No fixes generated")
        return 0

    # Apply fixes
    await codepmcs.remediator.apply_fixes(remediation, args.path)

    # Create PR
    pr_result = await codepmcs.create_pr(remediation, title=args.title)

    if pr_result.success:
        print(f"PR created: {pr_result.url}")
        return 0
    else:
        print(f"PR creation failed: {pr_result.error}")
        return 1


async def cmd_full(args):
    """Execute full pipeline command."""
    codepmcs = CodePMCS()

    print("Running full CodePMCS pipeline...")
    result = await codepmcs.full_pipeline(args.path)

    print(f"\nStatus: {result['status']}")
    print(f"Issues found: {result['issues']}")
    if result.get("fixes"):
        print(f"Fixes applied: {result['fixes']}")
    if result.get("pr_url"):
        print(f"PR URL: {result['pr_url']}")

    return 0 if result["status"] != "error" else 1


async def cmd_status(args):
    """Check CodePMCS status."""
    from .scanner import GEMINI_AVAILABLE

    print("CodePMCS Status")
    print("=" * 40)
    print(f"Gemini API: {'Available' if GEMINI_AVAILABLE else 'Not available'}")

    # Check gh CLI
    import subprocess

    try:
        result = subprocess.run(["gh", "auth", "status"], capture_output=True, timeout=5)
        gh_status = "Authenticated" if result.returncode == 0 else "Not authenticated"
    except:
        gh_status = "Not installed"
    print(f"GitHub CLI: {gh_status}")

    # Check ruff
    try:
        result = subprocess.run(["ruff", "--version"], capture_output=True, text=True, timeout=5)
        ruff_version = result.stdout.strip() if result.returncode == 0 else "Not available"
    except:
        ruff_version = "Not installed"
    print(f"Ruff: {ruff_version}")

    return 0


async def main():
    args = parse_args()

    if args.command == "scan":
        return await cmd_scan(args)
    elif args.command == "fix":
        return await cmd_fix(args)
    elif args.command == "pr":
        return await cmd_pr(args)
    elif args.command == "full":
        return await cmd_full(args)
    elif args.command == "status":
        return await cmd_status(args)
    else:
        print("Usage: codepmcs <command> [options]")
        print("Commands: scan, fix, pr, full, status")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
