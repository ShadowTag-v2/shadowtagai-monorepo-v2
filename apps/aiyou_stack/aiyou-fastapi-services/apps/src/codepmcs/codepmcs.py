# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from .remediator import RemediationResult, Remediator
from .scanner import CodeScanner, ScanResult


class CodePMCS:
    """Code Preventive Maintenance Checks and Services (PMCS).
    Orchestrates scanning, remediation, and reporting for code quality.
    """

    def __init__(self):
        self.scanner = CodeScanner()
        self.remediator = Remediator()

    def perform_pmcs(self, target_dir: str = ".") -> list[ScanResult]:
        """Runs the full PMCS cycle: Scan -> Report -> (Optional) Fix."""
        print(f"🔧 CodePMCS: Starting scan of {target_dir}...")
        findings = self.scanner.scan_directory(target_dir)
        return findings

    def fix_issue(self, issue_description: str, code_context: str) -> RemediationResult:
        """Attempts to fix a specific issue using the Remediator."""
        return self.remediator.remediate(code_context, issue_description)
