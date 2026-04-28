# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""BugBot - Static analysis agent.
Runs without LLM - pure code analysis.
"""

import json
import subprocess
from pathlib import Path


class BugBot:
    """Automated bug detection agent - no LLM required."""

    def __init__(self, repo_path: str = "./"):
        self.repo_path = Path(repo_path)
        self.results = {"pylint": [], "mypy": [], "security": [], "complexity": []}

    def run_pylint(self, target: str = "src/") -> dict:
        """Run pylint for code quality."""
        print("///▞ BUGBOT :: Running pylint analysis")
        try:
            result = subprocess.run(
                ["python3", "-m", "pylint", target, "--output-format=json"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=120,
            )
            if result.stdout:
                issues = json.loads(result.stdout)
                self.results["pylint"] = issues
                return {"status": "complete", "issues": len(issues)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return {"status": "clean", "issues": 0}

    def run_mypy(self, target: str = "src/") -> dict:
        """Run mypy for type checking."""
        print("///▞ BUGBOT :: Running mypy type check")
        try:
            result = subprocess.run(
                ["python3", "-m", "mypy", target, "--ignore-missing-imports"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=120,
            )
            issues = result.stdout.strip().split("\n") if result.stdout else []
            self.results["mypy"] = [i for i in issues if i]
            return {"status": "complete", "issues": len(self.results["mypy"])}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def run_security_scan(self, target: str = "src/") -> dict:
        """Run bandit for security issues."""
        print("///▞ BUGBOT :: Running security scan")
        try:
            result = subprocess.run(
                ["python3", "-m", "bandit", "-r", target, "-f", "json"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=120,
            )
            if result.stdout:
                data = json.loads(result.stdout)
                self.results["security"] = data.get("results", [])
                return {
                    "status": "complete",
                    "issues": len(self.results["security"]),
                    "severity": {
                        "high": sum(
                            1 for r in self.results["security"] if r.get("issue_severity") == "HIGH"
                        ),
                        "medium": sum(
                            1
                            for r in self.results["security"]
                            if r.get("issue_severity") == "MEDIUM"
                        ),
                        "low": sum(
                            1 for r in self.results["security"] if r.get("issue_severity") == "LOW"
                        ),
                    },
                }
        except FileNotFoundError:
            return {"status": "skipped", "message": "bandit not installed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_complexity(self, target: str = "src/") -> dict:
        """Check cyclomatic complexity with radon."""
        print("///▞ BUGBOT :: Checking code complexity")
        try:
            result = subprocess.run(
                ["python3", "-m", "radon", "cc", target, "-j"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=120,
            )
            if result.stdout:
                data = json.loads(result.stdout)
                high_complexity = []
                for file, functions in data.items():
                    for func in functions:
                        if func.get("complexity", 0) > 10:
                            high_complexity.append(
                                {
                                    "file": file,
                                    "function": func.get("name"),
                                    "complexity": func.get("complexity"),
                                },
                            )
                self.results["complexity"] = high_complexity
                return {"status": "complete", "high_complexity_functions": len(high_complexity)}
        except FileNotFoundError:
            return {"status": "skipped", "message": "radon not installed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def full_scan(self, target: str = "src/") -> dict:
        """Run all analysis tools."""
        print("///▞ BUGBOT :: Starting full scan")

        results = {
            "pylint": self.run_pylint(target),
            "mypy": self.run_mypy(target),
            "security": self.run_security_scan(target),
            "complexity": self.check_complexity(target),
        }

        # Calculate overall health score
        total_issues = (
            results["pylint"].get("issues", 0)
            + results["mypy"].get("issues", 0)
            + results["security"].get("issues", 0) * 2  # Security weighted 2x
            + results["complexity"].get("high_complexity_functions", 0)
        )

        health_score = max(0, 100 - total_issues)

        print(f"///▞ BUGBOT :: Scan complete. Health score: {health_score}/100")

        return {
            "health_score": health_score,
            "total_issues": total_issues,
            "details": results,
            "recommendation": "PASS" if health_score >= 70 else "NEEDS_WORK",
        }

    def get_report(self) -> str:
        """Generate markdown report."""
        report = "# BugBot Analysis Report\n\n"

        if self.results["pylint"]:
            report += f"## Pylint Issues: {len(self.results['pylint'])}\n"
            for issue in self.results["pylint"][:10]:
                report += f"- {issue.get('path')}:{issue.get('line')} - {issue.get('message')}\n"

        if self.results["security"]:
            report += f"\n## Security Issues: {len(self.results['security'])}\n"
            for issue in self.results["security"][:5]:
                report += f"- [{issue.get('issue_severity')}] {issue.get('issue_text')}\n"

        if self.results["complexity"]:
            report += f"\n## High Complexity: {len(self.results['complexity'])}\n"
            for item in self.results["complexity"]:
                report += (
                    f"- {item['file']}:{item['function']} (complexity: {item['complexity']})\n"
                )

        return report


if __name__ == "__main__":
    bot = BugBot()
    results = bot.full_scan("src/")
    print(json.dumps(results, indent=2))
