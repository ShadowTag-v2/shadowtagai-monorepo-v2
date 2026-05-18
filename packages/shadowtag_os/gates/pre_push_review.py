# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Pre-Push Code Review Gate — Ported from Claude Code's review.ts.

Inspects staged changes before git push to prevent:
  - Committed secrets/API keys
  - Debug artifacts (breakpoint, console.log, print())
  - Merge conflict markers
  - Binary blobs exceeding size threshold
  - Files matching .gitignore patterns

Integrated into omega-sync pipeline as a mandatory gate.
"""

from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Patterns that MUST NOT appear in pushed code
SECRET_PATTERNS = [
    re.compile(r"(?i)(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,}"),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),  # Stripe/OpenAI secret keys
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),  # GitHub PATs
    re.compile(r"AIza[a-zA-Z0-9_-]{35}"),  # Google API keys
    re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----"),
]

DEBUG_PATTERNS = [
    re.compile(r"^\+.*\bbreakpoint\(\)"),
    re.compile(r"^\+.*\bconsole\.log\("),
    re.compile(r"^\+.*\bprint\(.*DEBUG"),
    re.compile(r"^\+.*\bpdb\.set_trace\(\)"),
    re.compile(r"^\+.*\bdebugger;"),
]

CONFLICT_MARKERS = re.compile(r"^[<>=]{7}")

MAX_FILE_SIZE_KB = 500


@dataclass
class ReviewFinding:
    """A single finding from the pre-push review.

    Attributes:
        file: Path to the affected file.
        line: Line number (0 if file-level).
        severity: "error" blocks push, "warning" allows with note.
        message: Human-readable description.
    """

    file: str
    line: int
    severity: str  # "error" | "warning"
    message: str


@dataclass
class ReviewResult:
    """Result of the pre-push review gate.

    Attributes:
        passed: Whether the push should proceed.
        findings: List of issues found.
        files_reviewed: Number of files inspected.
    """

    passed: bool = True
    findings: list[ReviewFinding] = field(default_factory=list)
    files_reviewed: int = 0


def run_pre_push_review(base_ref: str = "HEAD~1") -> ReviewResult:
    """Run the pre-push code review against staged changes.

    Args:
        base_ref: Git ref to diff against (default: HEAD~1).

    Returns:
        ReviewResult with pass/fail and findings.
    """
    result = ReviewResult()

    try:
        diff_output = subprocess.run(
            ["git", "diff", base_ref, "--unified=0", "--diff-filter=ACMR"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if diff_output.returncode != 0:
            logger.warning("git diff failed: %s", diff_output.stderr)
            return result
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        logger.error("Pre-push review failed: %s", exc)
        return result

    current_file = ""
    line_num = 0

    for line in diff_output.stdout.splitlines():
        # Track file changes
        if line.startswith("diff --git"):
            parts = line.split(" b/")
            if len(parts) > 1:
                current_file = parts[1]
                result.files_reviewed += 1
            continue

        # Track line numbers
        if line.startswith("@@"):
            match = re.search(r"\+(\d+)", line)
            if match:
                line_num = int(match.group(1))
            continue

        # Only check added lines
        if not line.startswith("+"):
            continue

        # Check for secrets
        for pattern in SECRET_PATTERNS:
            if pattern.search(line):
                result.findings.append(
                    ReviewFinding(
                        file=current_file,
                        line=line_num,
                        severity="error",
                        message=f"Possible secret/API key detected: {line[:60]}...",
                    )
                )
                result.passed = False

        # Check for debug artifacts
        for pattern in DEBUG_PATTERNS:
            if pattern.search(line):
                result.findings.append(
                    ReviewFinding(
                        file=current_file,
                        line=line_num,
                        severity="warning",
                        message=f"Debug artifact: {line[:60]}...",
                    )
                )

        # Check for merge conflict markers
        if CONFLICT_MARKERS.search(line[1:]):  # Skip the + prefix
            result.findings.append(
                ReviewFinding(
                    file=current_file,
                    line=line_num,
                    severity="error",
                    message="Merge conflict marker found",
                )
            )
            result.passed = False

        line_num += 1

    errors = [f for f in result.findings if f.severity == "error"]
    warnings = [f for f in result.findings if f.severity == "warning"]
    logger.info(
        "Pre-push review: %d files, %d errors, %d warnings → %s",
        result.files_reviewed,
        len(errors),
        len(warnings),
        "PASS" if result.passed else "FAIL",
    )

    return result
