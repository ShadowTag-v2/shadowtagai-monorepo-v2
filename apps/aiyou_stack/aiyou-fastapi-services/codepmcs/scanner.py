"""CodePMCS Scanner - Gemini-powered code quality scanner.

Uses Gemini function calling for intelligent issue detection:
- Security vulnerabilities (OWASP Top 10)
- Code quality issues (TODO/FIXME, dead code, complexity)
- Style violations (linting, formatting)
"""

import asyncio
import json
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class Severity(Enum):
    """Issue severity levels."""

    CRITICAL = "critical"  # Security vulnerabilities, data exposure
    HIGH = "high"  # Bugs, performance issues
    MEDIUM = "medium"  # Code smells, maintainability
    LOW = "low"  # Style, minor improvements
    INFO = "info"  # Suggestions, best practices


class IssueType(Enum):
    """Types of detected issues."""

    SECURITY = "security"
    BUG = "bug"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    STYLE = "style"
    TODO = "todo"
    DEAD_CODE = "dead_code"
    COMPLEXITY = "complexity"


@dataclass
class Issue:
    """A detected code issue."""

    id: str
    file_path: str
    line_start: int
    line_end: int
    severity: Severity
    issue_type: IssueType
    title: str
    description: str
    suggestion: str | None = None
    code_snippet: str | None = None
    rule_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "severity": self.severity.value,
            "issue_type": self.issue_type.value,
            "title": self.title,
            "description": self.description,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet,
            "rule_id": self.rule_id,
        }


@dataclass
class ScanResult:
    """Result of a code scan."""

    repo_path: str
    scan_id: str
    timestamp: str
    issues: list[Issue] = field(default_factory=list)
    files_scanned: int = 0
    scan_duration_ms: float = 0.0
    rules_applied: list[str] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.HIGH)

    def to_dict(self) -> dict:
        return {
            "repo_path": self.repo_path,
            "scan_id": self.scan_id,
            "timestamp": self.timestamp,
            "issues": [i.to_dict() for i in self.issues],
            "files_scanned": self.files_scanned,
            "scan_duration_ms": self.scan_duration_ms,
            "rules_applied": self.rules_applied,
            "summary": {
                "total": len(self.issues),
                "critical": self.critical_count,
                "high": self.high_count,
            },
        }

    def to_sarif(self) -> dict:
        """Export to SARIF format for GitHub Security tab."""
        return {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "CodePMCS",
                            "version": "1.0.0",
                            "informationUri": "https://github.com/ShadowTag-v2/shadowtag_v4-fastapi-services",
                        },
                    },
                    "results": [
                        {
                            "ruleId": issue.rule_id or issue.issue_type.value,
                            "level": self._severity_to_sarif(issue.severity),
                            "message": {"text": issue.description},
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {"uri": issue.file_path},
                                        "region": {
                                            "startLine": issue.line_start,
                                            "endLine": issue.line_end,
                                        },
                                    },
                                },
                            ],
                        }
                        for issue in self.issues
                    ],
                },
            ],
        }

    @staticmethod
    def _severity_to_sarif(severity: Severity) -> str:
        mapping = {
            Severity.CRITICAL: "error",
            Severity.HIGH: "error",
            Severity.MEDIUM: "warning",
            Severity.LOW: "note",
            Severity.INFO: "note",
        }
        return mapping.get(severity, "note")


class CodeScanner:
    """Gemini-powered code scanner."""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self._setup_gemini()
        self._issue_counter = 0

    def _load_config(self, config_path: str) -> dict:
        """Load scanner configuration."""
        default_config = {
            "extensions": [".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".java"],
            "exclude_dirs": [
                "node_modules",
                ".git",
                "__pycache__",
                "venv",
                ".venv",
                "dist",
                "build",
            ],
            "max_file_size_kb": 500,
            "gemini_model": "gemini-3.1-flash-lite-preview-preview-06-05",
            "enable_security": True,
            "enable_quality": True,
            "enable_style": True,
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

    def _generate_issue_id(self) -> str:
        """Generate unique issue ID."""
        self._issue_counter += 1
        return f"CODEPMCS-{self._issue_counter:04d}"

    async def scan(self, repo_path: str, rules: list[str] = None) -> ScanResult:
        """Scan repository for issues."""
        start_time = datetime.now()
        scan_id = f"scan-{start_time.strftime('%Y%m%d-%H%M%S')}"

        result = ScanResult(
            repo_path=repo_path,
            scan_id=scan_id,
            timestamp=start_time.isoformat(),
            rules_applied=rules or ["security", "quality", "style"],
        )

        # Collect files to scan
        files = self._collect_files(repo_path)
        result.files_scanned = len(files)

        # Run scanners
        all_issues = []

        # 1. Static analysis (fast, local)
        static_issues = await self._run_static_analysis(repo_path, files)
        all_issues.extend(static_issues)

        # 2. TODO/FIXME detection (fast, local)
        todo_issues = await self._scan_todos(files)
        all_issues.extend(todo_issues)

        # 3. Gemini AI analysis (intelligent, API)
        if self.enabled and self.config.get("enable_ai_scan", True):
            ai_issues = await self._run_gemini_analysis(files)
            all_issues.extend(ai_issues)

        result.issues = all_issues
        result.scan_duration_ms = (datetime.now() - start_time).total_seconds() * 1000

        return result

    def _collect_files(self, repo_path: str) -> list[Path]:
        """Collect files to scan based on config."""
        files = []
        repo = Path(repo_path)

        for ext in self.config["extensions"]:
            for file_path in repo.rglob(f"*{ext}"):
                # Skip excluded directories
                if any(excluded in file_path.parts for excluded in self.config["exclude_dirs"]):
                    continue

                # Skip large files
                if file_path.stat().st_size > self.config["max_file_size_kb"] * 1024:
                    continue

                files.append(file_path)

        return files

    async def _run_static_analysis(self, repo_path: str, files: list[Path]) -> list[Issue]:
        """Run static analysis tools (ruff, eslint, etc.)."""
        issues = []

        # Check for Python files -> run ruff
        py_files = [f for f in files if f.suffix == ".py"]
        if py_files:
            try:
                result = subprocess.run(
                    ["ruff", "check", "--output-format=json", repo_path],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.stdout:
                    ruff_issues = json.loads(result.stdout)
                    for ri in ruff_issues:
                        issues.append(
                            Issue(
                                id=self._generate_issue_id(),
                                file_path=ri.get("filename", ""),
                                line_start=ri.get("location", {}).get("row", 1),
                                line_end=ri.get("end_location", {}).get("row", 1),
                                severity=self._ruff_severity(ri.get("code", "")),
                                issue_type=IssueType.STYLE,
                                title=ri.get("code", "Style Issue"),
                                description=ri.get("message", ""),
                                rule_id=ri.get("code"),
                            ),
                        )
            except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
                pass  # ruff not available or failed

        return issues

    def _ruff_severity(self, code: str) -> Severity:
        """Map ruff error code to severity."""
        if code.startswith("S"):  # Security
            return Severity.HIGH
        if code.startswith("E") or code.startswith("F"):  # Errors
            return Severity.MEDIUM
        return Severity.LOW

    async def _scan_todos(self, files: list[Path]) -> list[Issue]:
        """Scan for TODO, FIXME, HACK, XXX comments."""
        issues = []
        patterns = ["TODO", "FIXME", "HACK", "XXX", "BUG"]

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    for pattern in patterns:
                        if pattern in line.upper():
                            issues.append(
                                Issue(
                                    id=self._generate_issue_id(),
                                    file_path=str(file_path),
                                    line_start=line_num,
                                    line_end=line_num,
                                    severity=Severity.LOW if pattern == "TODO" else Severity.MEDIUM,
                                    issue_type=IssueType.TODO,
                                    title=f"{pattern} found",
                                    description=line.strip(),
                                    code_snippet=line.strip(),
                                ),
                            )
                            break  # Only report once per line
            except Exception:
                continue

        return issues

    async def _run_gemini_analysis(self, files: list[Path]) -> list[Issue]:
        """Run Gemini AI analysis on code files."""
        if not self.enabled:
            return []

        issues = []

        # Batch files for analysis (to reduce API calls)
        batch_size = 5
        for i in range(0, min(len(files), 20), batch_size):  # Limit to 20 files
            batch = files[i : i + batch_size]
            batch_issues = await self._analyze_batch(batch)
            issues.extend(batch_issues)

        return issues

    async def _analyze_batch(self, files: list[Path]) -> list[Issue]:
        """Analyze a batch of files with Gemini."""
        if not self.enabled:
            return []

        # Build prompt with file contents
        file_contents = []
        for f in files:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                if len(content) < 50000:  # Skip very large files
                    file_contents.append(f"### File: {f}\n```\n{content[:10000]}\n```\n")
            except Exception:
                continue

        if not file_contents:
            return []

        prompt = f"""Analyze the following code files for:
1. Security vulnerabilities (SQL injection, XSS, secrets, etc.)
2. Bugs and potential runtime errors
3. Performance issues
4. Code quality problems

Files:
{"".join(file_contents)}

Return a JSON array of issues found. Each issue should have:
- file_path: string
- line_start: number
- line_end: number
- severity: "critical" | "high" | "medium" | "low"
- issue_type: "security" | "bug" | "performance" | "quality"
- title: string (short)
- description: string (detailed)
- suggestion: string (how to fix)

Return ONLY the JSON array, no other text. If no issues found, return [].
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

            issues = []
            for item in parsed:
                issues.append(
                    Issue(
                        id=self._generate_issue_id(),
                        file_path=item.get("file_path", ""),
                        line_start=item.get("line_start", 1),
                        line_end=item.get("line_end", 1),
                        severity=Severity(item.get("severity", "medium")),
                        issue_type=IssueType(item.get("issue_type", "quality")),
                        title=item.get("title", "Issue detected"),
                        description=item.get("description", ""),
                        suggestion=item.get("suggestion"),
                    ),
                )

            return issues

        except Exception as e:
            print(f"Gemini analysis failed: {e}")
            return []
