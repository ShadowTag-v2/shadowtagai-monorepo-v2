#!/usr/bin/env python3
"""Deduplicate and post PR review comments via GitHub Pulls Review API.

Collects review outputs from multiple parallel Gemini agent jobs,
deduplicates findings, and posts inline line-level comments as a
single consolidated review.

Usage:
    python scripts/post_review.py \\
        --repo owner/repo \\
        --pr 42 \\
        --commit abc123 \\
        --reviews /tmp/reviews/*.json \\
        --ane-report /tmp/ane_report.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from glob import glob
from pathlib import Path


@dataclass
class ReviewComment:
    """A single inline review comment."""

    path: str
    line: int
    body: str
    severity: str = "info"  # info, warning, error
    agent: str = "unknown"

    @property
    def dedup_key(self) -> str:
        """Content-based dedup key: same file + line + normalized body."""
        normalized = re.sub(r"\s+", " ", self.body.strip().lower())
        content_hash = hashlib.sha256(normalized.encode()).hexdigest()[:12]
        return f"{self.path}:{self.line}:{content_hash}"

    def to_github_comment(self) -> dict:
        """Format for GitHub Pulls Review API."""
        severity_icons = {
            "error": "🔴",
            "warning": "⚠️",
            "info": "💡",
        }
        icon = severity_icons.get(self.severity, "💡")
        prefixed_body = f"{icon} **[{self.agent}]** {self.body}"

        return {
            "path": self.path,
            "line": self.line,
            "body": prefixed_body,
        }


@dataclass
class ConsolidatedReview:
    """Deduplicated review ready for posting."""

    comments: list[ReviewComment] = field(default_factory=list)
    summary_lines: list[str] = field(default_factory=list)
    ane_report: dict | None = None

    def add_comment(self, comment: ReviewComment) -> bool:
        """Add comment if not a duplicate. Returns True if added."""
        key = comment.dedup_key
        existing_keys = {c.dedup_key for c in self.comments}
        if key in existing_keys:
            return False
        self.comments.append(comment)
        return True

    @property
    def error_count(self) -> int:
        return sum(1 for c in self.comments if c.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for c in self.comments if c.severity == "warning")

    def build_summary(self) -> str:
        """Build the top-level review summary."""
        parts = ["## 🔍 GCA Review (Multi-Agent)\n"]

        # Agent breakdown
        agents = {}
        for c in self.comments:
            agents.setdefault(c.agent, []).append(c)

        parts.append("### Agent Findings\n")
        parts.append("| Agent | Findings | Errors | Warnings |")
        parts.append("|-------|----------|--------|----------|")
        for agent, findings in sorted(agents.items()):
            errors = sum(1 for f in findings if f.severity == "error")
            warnings = sum(1 for f in findings if f.severity == "warning")
            parts.append(f"| {agent} | {len(findings)} | {errors} | {warnings} |")

        parts.append("")

        # ANE report
        if self.ane_report:
            if self.ane_report.get("passed"):
                parts.append("### ✅ ANE Budget Gate: PASSED\n")
            else:
                parts.append("### 🔴 ANE Budget Gate: FAILED\n")
                for v in self.ane_report.get("violations", []):
                    ratio = v.get("ratio", 0)
                    parts.append(
                        f"- `{v['file']}:{v['line']}` — "
                        f"{ratio}x over budget ({v['estimated_bytes']:,} bytes)"
                    )
                parts.append("")

        # Summary stats
        parts.append(
            f"**Total:** {len(self.comments)} findings "
            f"({self.error_count} errors, {self.warning_count} warnings)"
        )

        for line in self.summary_lines:
            parts.append(line)

        return "\n".join(parts)

    def build_review_event(self) -> str:
        """Determine review event type based on findings."""
        if self.error_count > 0:
            return "REQUEST_CHANGES"
        if self.warning_count > 0:
            return "COMMENT"
        return "APPROVE"


def parse_gemini_output(text: str, agent_name: str) -> list[ReviewComment]:
    """Parse Gemini agent output into structured review comments.

    Expects output in a loose format like:
        FILE: path/to/file.py
        LINE: 42
        SEVERITY: warning
        COMMENT: This function lacks error handling...
    """
    comments = []
    current: dict = {}

    for line in text.splitlines():
        line = line.strip()

        if line.upper().startswith("FILE:"):
            if current.get("body"):
                comments.append(
                    ReviewComment(
                        path=current.get("path", ""),
                        line=current.get("line", 0),
                        body=current.get("body", ""),
                        severity=current.get("severity", "info"),
                        agent=agent_name,
                    )
                )
            current = {"path": line.split(":", 1)[1].strip()}

        elif line.upper().startswith("LINE:"):
            try:
                current["line"] = int(line.split(":", 1)[1].strip())
            except ValueError:
                current["line"] = 0

        elif line.upper().startswith("SEVERITY:"):
            sev = line.split(":", 1)[1].strip().lower()
            if sev in ("error", "warning", "info"):
                current["severity"] = sev

        elif line.upper().startswith("COMMENT:"):
            current["body"] = line.split(":", 1)[1].strip()

        elif current.get("body") and line:
            current["body"] += " " + line

    # Flush last comment
    if current.get("body"):
        comments.append(
            ReviewComment(
                path=current.get("path", ""),
                line=current.get("line", 0),
                body=current.get("body", ""),
                severity=current.get("severity", "info"),
                agent=agent_name,
            )
        )

    return comments


def post_review(
    repo: str,
    pr_number: int,
    commit_sha: str,
    review: ConsolidatedReview,
    token: str,
) -> bool:
    """Post the consolidated review via GitHub API."""
    import urllib.request

    owner, repo_name = repo.split("/")
    url = (
        f"https://api.github.com/repos/{owner}/{repo_name}"
        f"/pulls/{pr_number}/reviews"
    )

    github_comments = [c.to_github_comment() for c in review.comments if c.line > 0]

    payload = {
        "commit_id": commit_sha,
        "body": review.build_summary(),
        "event": review.build_review_event(),
        "comments": github_comments,
    }

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"Review posted: {result.get('html_url', 'OK')}", file=sys.stderr)
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"GitHub API error {e.code}: {body}", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Post consolidated PR review")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--pr", type=int, required=True, help="PR number")
    parser.add_argument("--commit", required=True, help="Commit SHA")
    parser.add_argument(
        "--reviews",
        nargs="+",
        required=True,
        help="Glob patterns for review JSON/text files",
    )
    parser.add_argument("--ane-report", help="Path to ANE budget report JSON")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print review without posting",
    )
    args = parser.parse_args()

    # Build consolidated review
    review = ConsolidatedReview()

    # Load agent reviews
    review_files = []
    for pattern in args.reviews:
        review_files.extend(glob(pattern))

    for review_file in review_files:
        path = Path(review_file)
        agent_name = path.stem.replace("review_", "").replace("_review", "")
        content = path.read_text()

        # Try JSON first, fall back to text parsing
        try:
            data = json.loads(content)
            if isinstance(data, list):
                for item in data:
                    comment = ReviewComment(
                        path=item.get("path", ""),
                        line=item.get("line", 0),
                        body=item.get("body", item.get("comment", "")),
                        severity=item.get("severity", "info"),
                        agent=agent_name,
                    )
                    review.add_comment(comment)
            continue
        except (json.JSONDecodeError, AttributeError):
            pass

        # Text parsing fallback
        comments = parse_gemini_output(content, agent_name)
        for comment in comments:
            review.add_comment(comment)

    # Load ANE report
    if args.ane_report:
        ane_path = Path(args.ane_report)
        if ane_path.exists():
            review.ane_report = json.loads(ane_path.read_text())

    # Output or post
    if args.dry_run:
        print(review.build_summary())
        print(f"\n--- {len(review.comments)} inline comments ---")
        for c in review.comments:
            print(f"  {c.path}:{c.line} [{c.severity}] {c.body[:80]}")
        return 0

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN not set", file=sys.stderr)
        return 1

    success = post_review(args.repo, args.pr, args.commit, review, token)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
