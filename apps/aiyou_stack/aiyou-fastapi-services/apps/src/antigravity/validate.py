# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""CodePMCS Client - Code Quality Validation

Scans and auto-fixes code before commit.
Monitors pipeline for updates and new tech.
"""

from typing import Any

import httpx


class CodePMCSClient:
    """CodePMCS Code Quality Client

    Functions:
    - Scan code for issues
    - Auto-fix detected problems
    - Monitor pipeline for updates
    - Update code with new tech
    """

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url
        # If no URL provided, use local scanning fallback
        self.use_local = base_url is None

    async def scan(self, code: str, language: str = "python") -> dict[str, Any]:
        """Scan code for quality issues.

        Returns:
            {
                "passed": bool,
                "issues": [{"type": str, "message": str, "line": int}],
                "fixes": [{"type": str, "original": str, "fixed": str}],
                "score": float
            }

        """
        if self.use_local:
            return self._local_scan(code, language)

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/codepmcs/scan",
                    json={"code": code, "language": language},
                )

                if response.status_code == 200:
                    return response.json()
            except Exception:
                pass

        return self._local_scan(code, language)

    def _local_scan(self, code: str, language: str) -> dict[str, Any]:
        """Local code scanning without external service"""
        issues = []
        fixes = []

        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for common issues
            if "TODO" in line or "FIXME" in line:
                issues.append(
                    {
                        "type": "todo",
                        "message": "Unresolved TODO/FIXME",
                        "line": i,
                        "severity": "low",
                    },
                )

            if "print(" in line and language == "python":
                issues.append(
                    {
                        "type": "debug",
                        "message": "Debug print statement",
                        "line": i,
                        "severity": "low",
                    },
                )

            if "password" in line.lower() and "=" in line:
                issues.append(
                    {
                        "type": "security",
                        "message": "Possible hardcoded password",
                        "line": i,
                        "severity": "high",
                    },
                )

            if len(line) > 120:
                issues.append(
                    {
                        "type": "style",
                        "message": "Line too long (>120 chars)",
                        "line": i,
                        "severity": "low",
                    },
                )

        # Calculate score
        high_issues = sum(1 for i in issues if i.get("severity") == "high")
        med_issues = sum(1 for i in issues if i.get("severity") == "medium")
        low_issues = sum(1 for i in issues if i.get("severity") == "low")

        score = max(0, 1.0 - (high_issues * 0.3) - (med_issues * 0.1) - (low_issues * 0.02))

        return {
            "passed": high_issues == 0,
            "issues": issues,
            "fixes": fixes,
            "score": round(score, 2),
        }

    async def fix(self, code: str, issues: list[dict[str, Any]]) -> dict[str, Any]:
        """Auto-fix detected issues.

        Returns:
            {
                "fixed_code": str,
                "fixes_applied": int,
                "remaining_issues": [...]
            }

        """
        if self.use_local:
            return self._local_fix(code, issues)

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/codepmcs/fix",
                    json={"code": code, "issues": issues},
                )

                if response.status_code == 200:
                    return response.json()
            except Exception:
                pass

        return self._local_fix(code, issues)

    def _local_fix(self, code: str, issues: list[dict[str, Any]]) -> dict[str, Any]:
        """Local auto-fixing without external service"""
        fixed_code = code
        fixes_applied = 0
        remaining = []

        for issue in issues:
            if issue.get("type") == "debug" and "print(" in code:
                # Remove print statements (simple fix)
                lines = fixed_code.split("\n")
                new_lines = []
                for line in lines:
                    if "print(" in line and not line.strip().startswith("#"):
                        new_lines.append(f"# {line}  # DEBUG DISABLED")
                        fixes_applied += 1
                    else:
                        new_lines.append(line)
                fixed_code = "\n".join(new_lines)
            else:
                remaining.append(issue)

        return {
            "fixed_code": fixed_code,
            "fixes_applied": fixes_applied,
            "remaining_issues": remaining,
        }

    async def check_pipeline_updates(self) -> dict[str, Any]:
        """Check pipeline for updates to apply to code.

        Returns:
            {
                "updates_available": bool,
                "updates": [{"type": str, "description": str}],
                "new_tech": [...]
            }

        """
        # TODO: Implement pipeline monitoring
        return {"updates_available": False, "updates": [], "new_tech": []}
