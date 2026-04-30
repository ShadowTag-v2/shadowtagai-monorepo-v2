"""CodePMCS - AI-Powered Code Quality & Remediation Platform

Part of the n-autoresearch/Kosmos/BioAgents Cavalry Squadron.
Provides automated code scanning, remediation, and PR generation.

Usage:
    from codepmcs import CodePMCS

    scanner = CodePMCS()
    issues = await scanner.scan("/path/to/repo")
    fixes = await scanner.remediate(issues)
    pr_url = await scanner.create_pr(fixes)
"""

__version__ = "1.0.0"
__author__ = "n-autoresearch/Kosmos/BioAgents Squadron"

from .pr_generator import PRGenerator, PRResult
from .remediator import Fix, RemediationResult, Remediator
from .scanner import CodeScanner, Issue, ScanResult, Severity

__all__ = [
    "CodeScanner",
    "Fix",
    "Issue",
    "PRGenerator",
    "PRResult",
    "RemediationResult",
    "Remediator",
    "ScanResult",
    "Severity",
]


class CodePMCS:
    """Main CodePMCS orchestrator - integrates scanning, remediation, and PR creation."""

    def __init__(self, config_path: str = None):
        self.scanner = CodeScanner(config_path)
        self.remediator = Remediator(config_path)
        self.pr_generator = PRGenerator()

    async def scan(self, repo_path: str, rules: list = None) -> "ScanResult":
        """Scan a repository for code quality issues."""
        return await self.scanner.scan(repo_path, rules)

    async def remediate(
        self,
        scan_result: "ScanResult",
        auto_fix: bool = True,
    ) -> "RemediationResult":
        """Generate fixes for detected issues."""
        return await self.remediator.remediate(scan_result, auto_fix)

    async def create_pr(self, remediation: "RemediationResult", title: str = None) -> "PRResult":
        """Create a PR with the fixes."""
        return await self.pr_generator.create(remediation, title)

    async def full_pipeline(self, repo_path: str, rules: list = None) -> dict:
        """Run full scan -> remediate -> PR pipeline."""
        scan_result = await self.scan(repo_path, rules)
        if not scan_result.issues:
            return {"status": "clean", "issues": 0, "pr_url": None}

        remediation = await self.remediate(scan_result)
        if not remediation.fixes:
            return {"status": "no_fixes", "issues": len(scan_result.issues), "pr_url": None}

        pr_result = await self.create_pr(remediation)
        return {
            "status": "pr_created",
            "issues": len(scan_result.issues),
            "fixes": len(remediation.fixes),
            "pr_url": pr_result.url,
        }
