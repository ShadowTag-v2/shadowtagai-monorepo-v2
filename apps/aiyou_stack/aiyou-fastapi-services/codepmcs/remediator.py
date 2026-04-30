"""CodePMCS Remediator - AI-powered auto-fix generator.

Uses Gemini to generate fixes for detected issues:
- Security patches
- Bug fixes
- Code quality improvements
"""

import asyncio
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .scanner import Issue, ScanResult, Severity

try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


@dataclass
class Fix:
    """A code fix for an issue."""

    issue_id: str
    file_path: str
    original_code: str
    fixed_code: str
    description: str
    confidence: float  # 0.0 - 1.0
    breaking_change: bool = False
    requires_review: bool = True

    def to_dict(self) -> dict:
        return {
            "issue_id": self.issue_id,
            "file_path": self.file_path,
            "original_code": self.original_code,
            "fixed_code": self.fixed_code,
            "description": self.description,
            "confidence": self.confidence,
            "breaking_change": self.breaking_change,
            "requires_review": self.requires_review,
        }


@dataclass
class RemediationResult:
    """Result of remediation process."""

    scan_id: str
    timestamp: str
    fixes: list[Fix] = field(default_factory=list)
    skipped_issues: list[str] = field(default_factory=list)
    duration_ms: float = 0.0

    @property
    def total_fixes(self) -> int:
        return len(self.fixes)

    @property
    def high_confidence_fixes(self) -> int:
        return sum(1 for f in self.fixes if f.confidence >= 0.8)

    def to_dict(self) -> dict:
        return {
            "scan_id": self.scan_id,
            "timestamp": self.timestamp,
            "fixes": [f.to_dict() for f in self.fixes],
            "skipped_issues": self.skipped_issues,
            "duration_ms": self.duration_ms,
            "summary": {
                "total_fixes": self.total_fixes,
                "high_confidence": self.high_confidence_fixes,
                "skipped": len(self.skipped_issues),
            },
        }


class Remediator:
    """Gemini-powered code remediator."""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self._setup_gemini()

    def _load_config(self, config_path: str) -> dict:
        """Load remediator configuration."""
        default_config = {
            "gemini_model": "gemini-3.1-flash-lite-preview-preview-06-05",
            "min_severity": "medium",  # Only fix medium+ severity
            "auto_fix_types": ["style", "quality", "todo"],
            "review_required_types": ["security", "bug"],
            "max_fixes_per_run": 50,
            "confidence_threshold": 0.7,
        }

        if config_path and Path(config_path).exists():
            import yaml

            with open(config_path) as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)

        return default_config

    def _setup_gemini(self):
        """Setup Gemini API client."""
        if GEMINI_AVAILABLE:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(self.config["gemini_model"])
                self.enabled = True
            else:
                self.enabled = False
        else:
            self.enabled = False

    def _should_fix(self, issue: Issue) -> bool:
        """Determine if an issue should be auto-fixed."""
        severity_order = [
            Severity.INFO,
            Severity.LOW,
            Severity.MEDIUM,
            Severity.HIGH,
            Severity.CRITICAL,
        ]
        min_severity = Severity(self.config["min_severity"])

        return not severity_order.index(issue.severity) < severity_order.index(min_severity)

    def _requires_review(self, issue: Issue) -> bool:
        """Determine if a fix requires human review."""
        return issue.issue_type.value in self.config["review_required_types"]

    async def remediate(self, scan_result: ScanResult, auto_fix: bool = True) -> RemediationResult:
        """Generate fixes for scan issues."""
        start_time = datetime.now()

        result = RemediationResult(
            scan_id=scan_result.scan_id,
            timestamp=start_time.isoformat(),
        )

        # Filter issues to fix
        issues_to_fix = []
        for issue in scan_result.issues:
            if not self._should_fix(issue):
                result.skipped_issues.append(f"{issue.id}: Below severity threshold")
                continue
            issues_to_fix.append(issue)

        # Limit number of fixes
        issues_to_fix = issues_to_fix[: self.config["max_fixes_per_run"]]

        # Generate fixes
        if self.enabled and auto_fix:
            for issue in issues_to_fix:
                fix = await self._generate_fix(issue, scan_result.repo_path)
                if fix:
                    result.fixes.append(fix)
                else:
                    result.skipped_issues.append(f"{issue.id}: Could not generate fix")

        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        return result

    async def _generate_fix(self, issue: Issue, repo_path: str) -> Fix | None:
        """Generate a fix for a single issue using Gemini."""
        if not self.enabled:
            return None

        # Read the file
        file_path = (
            Path(repo_path) / issue.file_path
            if not Path(issue.file_path).is_absolute()
            else Path(issue.file_path)
        )

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Get context around the issue
            start = max(0, issue.line_start - 5)
            end = min(len(lines), issue.line_end + 5)
            context_lines = lines[start:end]
            original_code = "\n".join(lines[issue.line_start - 1 : issue.line_end])

        except Exception as e:
            print(f"Could not read file {file_path}: {e}")
            return None

        prompt = f"""Fix the following code issue:

Issue Type: {issue.issue_type.value}
Severity: {issue.severity.value}
Title: {issue.title}
Description: {issue.description}
{f"Suggestion: {issue.suggestion}" if issue.suggestion else ""}

File: {issue.file_path}
Lines: {issue.line_start}-{issue.line_end}

Code Context (with line numbers):
```
{chr(10).join(f"{start + i + 1}: {line}" for i, line in enumerate(context_lines))}
```

Original Code to Fix:
```
{original_code}
```

Generate a fix. Return JSON with:
- fixed_code: the corrected code (only the lines that need changing)
- description: brief explanation of the fix
- confidence: 0.0-1.0 how confident you are this fix is correct
- breaking_change: true/false if this could break existing functionality

Return ONLY valid JSON, no other text.
"""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
            )

            # Parse response
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                text = text.removeprefix("json")

            parsed = json.loads(text)

            confidence = parsed.get("confidence", 0.5)
            if confidence < self.config["confidence_threshold"]:
                return None

            return Fix(
                issue_id=issue.id,
                file_path=issue.file_path,
                original_code=original_code,
                fixed_code=parsed.get("fixed_code", ""),
                description=parsed.get("description", "AI-generated fix"),
                confidence=confidence,
                breaking_change=parsed.get("breaking_change", False),
                requires_review=self._requires_review(issue),
            )

        except Exception as e:
            print(f"Fix generation failed for {issue.id}: {e}")
            return None

    async def apply_fixes(self, result: RemediationResult, repo_path: str) -> dict[str, bool]:
        """Apply fixes to files (use with caution)."""
        applied = {}

        for fix in result.fixes:
            if fix.requires_review and fix.confidence < 0.9:
                applied[fix.issue_id] = False
                continue

            file_path = (
                Path(repo_path) / fix.file_path
                if not Path(fix.file_path).is_absolute()
                else Path(fix.file_path)
            )

            try:
                content = file_path.read_text(encoding="utf-8")
                new_content = content.replace(fix.original_code, fix.fixed_code)
                file_path.write_text(new_content, encoding="utf-8")
                applied[fix.issue_id] = True
            except Exception as e:
                print(f"Failed to apply fix {fix.issue_id}: {e}")
                applied[fix.issue_id] = False

        return applied
