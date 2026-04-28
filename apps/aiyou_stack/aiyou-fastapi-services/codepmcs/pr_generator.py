# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""CodePMCS PR Generator - Automated PR creation for fixes.

Uses GitHub CLI (gh) to create PRs with fixes.
"""

import asyncio
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime

from .remediator import Fix, RemediationResult


@dataclass
class PRResult:
    """Result of PR creation."""

    success: bool
    url: str | None = None
    pr_number: int | None = None
    branch_name: str | None = None
    title: str = ""
    body: str = ""
    files_changed: int = 0
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "url": self.url,
            "pr_number": self.pr_number,
            "branch_name": self.branch_name,
            "title": self.title,
            "files_changed": self.files_changed,
            "error": self.error,
        }


class PRGenerator:
    """GitHub PR generator using gh CLI."""

    def __init__(self):
        self._check_gh_cli()

    def _check_gh_cli(self) -> bool:
        """Check if gh CLI is available and authenticated."""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.gh_available = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.gh_available = False
        return self.gh_available

    def _generate_branch_name(self, scan_id: str) -> str:
        """Generate a branch name for the fix PR."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"codepmcs/auto-fix-{timestamp}"

    def _generate_pr_title(self, fixes: list[Fix]) -> str:
        """Generate PR title based on fixes."""
        if len(fixes) == 1:
            return f"CodePMCS: Fix {fixes[0].issue_id}"
        return f"CodePMCS: Auto-fix {len(fixes)} code quality issues"

    def _generate_pr_body(self, remediation: RemediationResult) -> str:
        """Generate PR body with fix details."""
        body_parts = [
            "## Summary",
            f"CodePMCS automated code quality fixes from scan `{remediation.scan_id}`.",
            "",
            "## Fixes Applied",
            "",
        ]

        # Group fixes by type
        by_type = {}
        for fix in remediation.fixes:
            # Extract issue type from description or default
            fix_type = "Code Quality"
            by_type.setdefault(fix_type, []).append(fix)

        for fix_type, fixes in by_type.items():
            body_parts.append(f"### {fix_type}")
            for fix in fixes:
                confidence_emoji = (
                    "" if fix.confidence >= 0.8 else "" if fix.confidence >= 0.6 else ""
                )
                review_tag = " [REVIEW REQUIRED]" if fix.requires_review else ""
                body_parts.append(
                    f"- {confidence_emoji} `{fix.issue_id}`: {fix.description}{review_tag}",
                )
            body_parts.append("")

        # Add statistics
        body_parts.extend(
            [
                "## Statistics",
                f"- Total fixes: {remediation.total_fixes}",
                f"- High confidence (>80%): {remediation.high_confidence_fixes}",
                f"- Skipped issues: {len(remediation.skipped_issues)}",
                "",
                "## Review Checklist",
                "- [ ] Verify fixes are correct",
                "- [ ] Run tests locally",
                "- [ ] Check for breaking changes",
                "",
                "---",
                " Generated with [CodePMCS](https://github.com/ShadowTag-v2/shadowtag_v4-fastapi-services)",
            ],
        )

        return "\n".join(body_parts)

    async def create(
        self,
        remediation: RemediationResult,
        title: str = None,
        repo_path: str = ".",
    ) -> PRResult:
        """Create a PR with the fixes."""
        if not self.gh_available:
            return PRResult(
                success=False,
                error="GitHub CLI (gh) not available or not authenticated",
            )

        if not remediation.fixes:
            return PRResult(
                success=False,
                error="No fixes to create PR for",
            )

        branch_name = self._generate_branch_name(remediation.scan_id)
        pr_title = title or self._generate_pr_title(remediation.fixes)
        pr_body = self._generate_pr_body(remediation)

        try:
            # Create and checkout new branch
            await self._run_git(["checkout", "-b", branch_name], cwd=repo_path)

            # Stage all changes
            await self._run_git(["add", "-A"], cwd=repo_path)

            # Commit
            commit_msg = f"{pr_title}\n\n Generated with CodePMCS\n\nCo-Authored-By: CodePMCS <codepmcs@n-autoresearch/Kosmos/BioAgents.ai>"
            await self._run_git(["commit", "-m", commit_msg], cwd=repo_path)

            # Push
            await self._run_git(["push", "-u", "origin", branch_name], cwd=repo_path)

            # Create PR
            pr_result = await self._create_pr(pr_title, pr_body, cwd=repo_path)

            return pr_result

        except Exception as e:
            return PRResult(
                success=False,
                branch_name=branch_name,
                title=pr_title,
                error=str(e),
            )

    async def _run_git(self, args: list[str], cwd: str = ".") -> subprocess.CompletedProcess:
        """Run a git command."""
        result = await asyncio.to_thread(
            subprocess.run,
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise Exception(f"Git command failed: {result.stderr}")
        return result

    async def _create_pr(self, title: str, body: str, cwd: str = ".") -> PRResult:
        """Create PR using gh CLI."""
        result = await asyncio.to_thread(
            subprocess.run,
            [
                "gh",
                "pr",
                "create",
                "--title",
                title,
                "--body",
                body,
                "--json",
                "url,number",
            ],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            raise Exception(f"PR creation failed: {result.stderr}")

        pr_data = json.loads(result.stdout)

        return PRResult(
            success=True,
            url=pr_data.get("url"),
            pr_number=pr_data.get("number"),
            title=title,
            body=body,
        )
