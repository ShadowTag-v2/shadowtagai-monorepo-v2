#!/usr/bin/env python3
"""GitHub Script Discovery Agent
Scans project for scripts that should be tracked in GitHub.
Produces structured JSON output for pipeline integration.
"""

import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class ScriptCandidate:
    """Candidate script for GitHub."""

    path: str
    language: str
    purpose: str
    category: str
    dependencies: dict[str, list[str]]
    status: str
    sensitive: bool
    issues: list[str]
    tests_present: bool
    usage_evidence: list[str]
    recommended_repo_group: str


@dataclass
class RepoProposal:
    """Proposed GitHub repository."""

    repo_name: str
    repo_purpose: str
    scripts_included: list[str]
    suggested_structure: list[str]
    minimal_files_to_add: list[str]
    security_notes: list[str]
    initial_commit_plan: list[dict[str, str]]
    priority: str


class GitHubDiscoveryAgent:
    """Automated code discovery and packaging agent.

    Searches project for scripts that should be tracked in GitHub.
    Produces actionable export plan with security scanning.
    """

    # File extensions to scan
    CODE_EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "zsh",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".java": "java",
        ".sql": "sql",
        ".tf": "terraform",
        ".yaml": "yaml",
        ".yml": "yaml",
    }

    # Directories to skip
    SKIP_DIRS = {
        "node_modules",
        "dist",
        "build",
        "__pycache__",
        ".pytest_cache",
        ".git",
        "venv",
        "env",
        ".venv",
        ".env",
        "vendor",
        "target",
    }

    # Sensitive patterns
    SENSITIVE_PATTERNS = [
        r'(?i)api[_-]?key\s*[=:]\s*["\']?[\w-]{20,}',
        r'(?i)secret\s*[=:]\s*["\']?[\w-]{20,}',
        r'(?i)password\s*[=:]\s*["\']?[^\s"\']{8,}',
        r'(?i)token\s*[=:]\s*["\']?[\w-]{20,}',
        r"-----BEGIN.*PRIVATE.*KEY-----",
    ]

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.candidates: list[ScriptCandidate] = []

    def scan(self) -> dict[str, Any]:
        """Scan project for script candidates.

        Returns:
            Dictionary with scripts and repo proposals

        """
        self._discover_scripts()
        repos = self._propose_repos()

        return {
            "summary": {
                "total_scanned": len(self.candidates),
                "candidates": len([c for c in self.candidates if not c.sensitive]),
                "sensitive": len([c for c in self.candidates if c.sensitive]),
                "repos_proposed": len(repos),
            },
            "scripts": [asdict(c) for c in self.candidates],
            "repos": [asdict(r) for r in repos],
            "handoff": {
                "thread_id": "ATOMIC-DISCOVERY",
                "next_action": "safety_scanner.py --input discovery.json",
                "tier": "FREE",
            },
        }

    def _discover_scripts(self):
        """Walk project tree and identify script candidates."""
        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]

            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()

                if ext in self.CODE_EXTENSIONS:
                    candidate = self._analyze_file(file_path)
                    if candidate:
                        self.candidates.append(candidate)

    def _analyze_file(self, file_path: Path) -> ScriptCandidate | None:
        """Analyze a single file for candidacy."""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Skip trivial files (< 20 lines)
            lines = content.split("\n")
            if len(lines) < 20:
                return None

            # Detect language
            language = self.CODE_EXTENSIONS.get(file_path.suffix.lower(), "unknown")

            # Check for sensitivity
            sensitive = any(re.search(p, content) for p in self.SENSITIVE_PATTERNS)

            # Analyze purpose
            purpose = self._infer_purpose(file_path, content)

            # Categorize
            category = self._categorize(file_path, content)

            # Find dependencies
            deps = self._find_dependencies(content, language)

            # Check for issues
            issues = self._find_issues(content, file_path)

            # Check for tests
            tests_present = self._has_tests(file_path)

            # Usage evidence
            usage = self._find_usage_evidence(file_path)

            # Repo group
            repo_group = self._suggest_repo_group(file_path, category)

            return ScriptCandidate(
                path=str(file_path.relative_to(self.project_root)),
                language=language,
                purpose=purpose,
                category=category,
                dependencies=deps,
                status=self._infer_status(content, issues),
                sensitive=sensitive,
                issues=issues,
                tests_present=tests_present,
                usage_evidence=usage,
                recommended_repo_group=repo_group,
            )

        except Exception:
            return None

    def _infer_purpose(self, file_path: Path, content: str) -> str:
        """Infer script purpose from docstring or comments."""
        # Check for docstring
        docstring_match = re.search(r'"""(.+?)"""', content, re.DOTALL)
        if docstring_match:
            doc = docstring_match.group(1).strip().split("\n")[0]
            return doc[:200]

        # Check for header comment
        for line in content.split("\n")[:10]:
            if line.strip().startswith("#") and len(line) > 10:
                return line.strip("# ").strip()[:200]

        return f"Script: {file_path.name}"

    def _categorize(self, file_path: Path, content: str) -> str:
        """Categorize script by type."""
        name = file_path.name.lower()
        path_str = str(file_path).lower()

        if "test" in name or "test" in path_str:
            return "test-util"
        if "cli" in name or "argparse" in content or "click" in content:
            return "cli"
        if "deploy" in path_str or "k8s" in path_str or "docker" in name:
            return "infra"
        if "pipeline" in name or "etl" in name:
            return "data-pipeline"
        if "scrape" in name or "crawler" in name:
            return "scraper"
        if "def " in content and "import " in content:
            return "library"
        return "other"

    def _find_dependencies(self, content: str, language: str) -> dict[str, list[str]]:
        """Extract dependencies from imports."""
        internal = []
        external = []

        if language == "python":
            # Find imports
            for match in re.finditer(r"^(?:from|import)\s+(\w+)", content, re.MULTILINE):
                pkg = match.group(1)
                if pkg in ["src", "app", "lib", "utils"]:
                    internal.append(pkg)
                elif pkg not in ["os", "sys", "re", "json", "datetime", "typing", "pathlib"]:
                    external.append(pkg)

        return {"internal": list(set(internal)), "external": list(set(external))}

    def _find_issues(self, content: str, file_path: Path) -> list[str]:
        """Find potential issues in code."""
        issues = []

        # Hardcoded paths
        if re.search(r"/Users/|/home/|C:\\", content):
            issues.append("hardcoded paths")

        # Missing error handling
        if "try:" not in content and "except" not in content:  # noqa: SIM102
            if "open(" in content or "requests." in content:
                issues.append("missing error handling")

        # TODO/FIXME
        if "TODO" in content or "FIXME" in content:
            issues.append("contains TODOs")

        return issues

    def _has_tests(self, file_path: Path) -> bool:
        """Check if tests exist for this file."""
        test_patterns = [
            f"test_{file_path.stem}.py",
            f"{file_path.stem}_test.py",
            f"tests/test_{file_path.stem}.py",
        ]
        return any((self.project_root / p).exists() for p in test_patterns)

    def _find_usage_evidence(self, file_path: Path) -> list[str]:
        """Find evidence of script usage."""
        evidence = []
        name = file_path.stem

        # Check if imported elsewhere
        for other in self.project_root.rglob("*.py"):
            if other != file_path:
                try:
                    if f"import {name}" in other.read_text(errors="ignore"):
                        evidence.append(f"imported by {other.name}")
                        break
                except Exception:
                    pass

        # Check if in CI
        ci_files = list(self.project_root.glob(".github/workflows/*.yml"))
        for ci in ci_files:
            try:
                if name in ci.read_text(errors="ignore"):
                    evidence.append("referenced in CI")
                    break
            except Exception:
                pass

        return evidence[:3]

    def _suggest_repo_group(self, file_path: Path, category: str) -> str:
        """Suggest repo grouping for script."""
        path_parts = file_path.parts

        if "services" in path_parts:
            return "shadowtag_v4-services"
        if "scripts" in path_parts:
            return "shadowtag_v4-scripts"
        if "infra" in path_parts or "k8s" in path_parts:
            return "shadowtag_v4-infra"
        if category == "test-util":
            return "shadowtag_v4-tests"
        return "shadowtag_v4-core"

    def _infer_status(self, content: str, issues: list[str]) -> str:
        """Infer production readiness."""
        if len(issues) > 2:
            return "experiment"
        if len(issues) > 0:
            return "prototype"
        return "production-ready"

    def _propose_repos(self) -> list[RepoProposal]:
        """Generate repository proposals from candidates."""
        # Group by recommended repo
        groups: dict[str, list[str]] = {}
        for c in self.candidates:
            if not c.sensitive:
                if c.recommended_repo_group not in groups:
                    groups[c.recommended_repo_group] = []
                groups[c.recommended_repo_group].append(c.path)

        repos = []
        for repo_name, scripts in groups.items():
            repos.append(
                RepoProposal(
                    repo_name=repo_name,
                    repo_purpose=f"Collection of {repo_name.replace('shadowtag_v4-', '')} for ShadowTag-v4 platform",
                    scripts_included=scripts,
                    suggested_structure=["src/", "scripts/", "tests/", "docs/"],
                    minimal_files_to_add=["README.md", "LICENSE", ".gitignore", "pyproject.toml"],
                    security_notes=["Review for hardcoded credentials", "Add .env.example"],
                    initial_commit_plan=[
                        {
                            "title": "chore: bootstrap repo",
                            "description": "Initial structure and config",
                        },
                        {
                            "title": "feat: add core scripts",
                            "description": "Import main functionality",
                        },
                        {"title": "docs: add README", "description": "Basic documentation"},
                    ],
                    priority="now" if len(scripts) > 3 else "later",
                ),
            )

        return sorted(repos, key=lambda r: len(r.scripts_included), reverse=True)


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="GitHub Script Discovery Agent")
    parser.add_argument("--root", help="Project root (default: cwd)")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--summary", action="store_true", help="Print summary only")

    args = parser.parse_args()

    agent = GitHubDiscoveryAgent(args.root)
    result = agent.scan()

    if args.summary:
        print(f"Total scanned: {result['summary']['total_scanned']}")
        print(f"Candidates: {result['summary']['candidates']}")
        print(f"Sensitive: {result['summary']['sensitive']}")
        print(f"Repos proposed: {result['summary']['repos_proposed']}")
    else:
        output = json.dumps(result, indent=2)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Output saved to: {args.output}")
        else:
            print(output)


if __name__ == "__main__":
    main()
