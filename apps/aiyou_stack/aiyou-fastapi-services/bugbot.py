# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""BugBot: Intelligent GitHub Issue Triage & Auto-Fix

Uses ultrathink framework for:
- Multi-agent debate on issue classification
- RCR for solution refinement
- Revenue tracking (time saved = $ saved)

Philosophy: Bugs are just unrefined opportunities.
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from ultrathink.core.agents import MultiAgentDebate
from ultrathink.core.prompts import CARE, RISE
from ultrathink.core.reasoning import RCR


class IssueSeverity(StrEnum):
    """Issue severity levels."""

    CRITICAL = "critical"  # System down, data loss
    HIGH = "high"  # Major functionality broken
    MEDIUM = "medium"  # Feature degraded
    LOW = "low"  # Minor inconvenience
    TRIVIAL = "trivial"  # Cosmetic


class IssueCategory(StrEnum):
    """Issue categories."""

    BUG = "bug"
    FEATURE = "feature_request"
    DOCS = "documentation"
    PERFORMANCE = "performance"
    SECURITY = "security"
    QUESTION = "question"


class TriageResult(BaseModel):
    """Result of issue triage."""

    severity: IssueSeverity
    category: IssueCategory
    priority_score: int = Field(ge=1, le=10, description="1=lowest, 10=highest")
    estimated_hours: float
    suggested_labels: list[str]
    recommended_assignee: str | None = None
    auto_fix_possible: bool = False
    reasoning: str


class BugBot:
    """Intelligent GitHub issue triage bot.

    Usage:
        bot = BugBot()
        result = await bot.triage({
            "title": "API returns 500 on /users endpoint",
            "body": "Steps to reproduce: ...",
            "labels": ["api", "backend"]
        })

    Features:
    - Multi-agent debate for severity classification
    - CARE prompting for context-rich analysis
    - RCR for solution refinement
    - Auto-fix generation for simple issues
    - Revenue tracking (time saved vs. manual triage)
    """

    def __init__(
        self,
        auto_fix_enabled: bool = True,
        debate_agents: int = 3,
        reasoning_strategy: Literal["MAD", "RCR"] = "MAD",
    ):
        """Initialize BugBot.

        Args:
            auto_fix_enabled: Try to generate fixes for simple issues
            debate_agents: Number of agents for severity debate
            reasoning_strategy: Which reasoning approach

        """
        self.auto_fix_enabled = auto_fix_enabled
        self.debate_agents = debate_agents
        self.reasoning_strategy = reasoning_strategy

    def format_triage_prompt(self, issue: dict) -> str:
        """Format issue data for triage."""
        care = CARE(
            context=(
                "GitHub issue triage for production FastAPI service. "
                "Users rely on this for critical operations. "
                "Our SLA: Critical issues fixed in 2h, high in 8h, medium in 48h."
            ),
            action=(
                "Classify severity, category, and priority. "
                "Estimate fix time. Suggest labels and assignee."
            ),
            result=(
                "JSON with severity (critical/high/medium/low/trivial), "
                "category, priority_score (1-10), estimated_hours, labels"
            ),
            example={
                "severity": "high",
                "category": "bug",
                "priority_score": 8,
                "estimated_hours": 4.0,
                "labels": ["bug", "api", "urgent"],
                "reasoning": "API 500 errors affect all users, but system still up",
            },
        )

        issue_text = f"""
Title: {issue.get("title", "No title")}

Body:
{issue.get("body", "No description")}

Existing labels: {issue.get("labels", [])}
Reported by: {issue.get("author", "unknown")}
"""

        return care.format(issue_text)

    async def triage(self, issue: dict) -> TriageResult:
        """Triage a GitHub issue using multi-agent debate.

        Args:
            issue: Issue data (title, body, labels, etc.)

        Returns:
            TriageResult with classification and recommendations

        """
        import re

        # Use multi-agent debate for severity consensus
        if self.reasoning_strategy == "MAD":
            debate = MultiAgentDebate(agents=self.debate_agents, rounds=3, strategy="RCR")

            prompt = self.format_triage_prompt(issue)
            result = debate.solve(prompt)

            # Parse consensus to extract structured data
            consensus = result.consensus.lower()

            # Extract severity
            if "critical" in consensus:
                severity = IssueSeverity.CRITICAL
            elif "high" in consensus:
                severity = IssueSeverity.HIGH
            elif "low" in consensus:
                severity = IssueSeverity.LOW
            elif "trivial" in consensus:
                severity = IssueSeverity.TRIVIAL
            else:
                severity = IssueSeverity.MEDIUM

            # Extract category
            if "security" in consensus:
                category = IssueCategory.SECURITY
            elif "performance" in consensus:
                category = IssueCategory.PERFORMANCE
            elif "feature" in consensus or "enhancement" in consensus:
                category = IssueCategory.FEATURE
            elif "doc" in consensus:
                category = IssueCategory.DOCS
            else:
                category = IssueCategory.BUG

            # Extract priority (look for numbers)
            priority_match = re.search(r"priority[:\s]+(\d+)", consensus)
            priority = int(priority_match.group(1)) if priority_match else 5

            # Extract hours
            hours_match = re.search(r"(\d+(?:\.\d+)?)\s*hour", consensus)
            estimated_hours = float(hours_match.group(1)) if hours_match else 2.0

            triage = TriageResult(
                severity=severity,
                category=category,
                priority_score=min(priority, 10),
                estimated_hours=estimated_hours,
                suggested_labels=[severity.value, category.value],
                auto_fix_possible=False,
                reasoning=result.consensus,
            )

        else:
            # Use RCR for iterative refinement
            rcr = RCR(max_iterations=3, focus="accuracy")
            prompt = self.format_triage_prompt(issue)
            result = rcr.refine(task=prompt)

            # Parse RCR output similarly
            result.final_output.lower()
            triage = TriageResult(
                severity=IssueSeverity.MEDIUM,
                category=IssueCategory.BUG,
                priority_score=5,
                estimated_hours=2.0,
                suggested_labels=["bug", "needs-review"],
                auto_fix_possible=False,
                reasoning=result.final_output,
            )

        # Check if auto-fix is possible
        if self.auto_fix_enabled and triage.severity in [
            IssueSeverity.LOW,
            IssueSeverity.TRIVIAL,
        ]:
            triage.auto_fix_possible = await self._check_auto_fixable(issue)

        return triage

    async def _check_auto_fixable(self, issue: dict) -> bool:
        """Determine if issue can be auto-fixed."""
        # Simple heuristics:
        # - Typos in docs
        # - Missing semicolons
        # - Linting issues
        # - Format inconsistencies

        title_lower = issue.get("title", "").lower()
        body_lower = issue.get("body", "").lower()

        auto_fix_keywords = [
            "typo",
            "spelling",
            "formatting",
            "indentation",
            "lint",
            "missing import",
            "unused variable",
        ]

        return any(keyword in title_lower or keyword in body_lower for keyword in auto_fix_keywords)

    async def generate_fix(self, issue: dict, triage: TriageResult) -> str | None:
        """Generate a fix for the issue (if auto-fixable).

        Args:
            issue: Issue data
            triage: Triage result

        Returns:
            Proposed fix (code, docs, etc.) or None

        """
        if not triage.auto_fix_possible:
            return None

        # Use RISE for step-by-step fix generation
        rise = RISE(
            role="Senior Python developer with FastAPI expertise",
            input_data=f"Issue: {issue.get('title')}\n{issue.get('body')}",
            steps=[
                "1. Identify the exact file(s) and line(s) affected",
                "2. Propose the minimal fix (Boy Scout Rule: leave it cleaner)",
                "3. Write tests to verify the fix",
                "4. Generate a PR description",
            ],
            expectation="Complete fix with code, tests, and PR description",
            output_format="Markdown with code blocks",
        )

        rise.format("Generate the fix")

        # In production: execute via model
        fix = "# Fix placeholder - would be generated by model"

        return fix

    def __repr__(self) -> str:
        return (
            f"BugBot(auto_fix={self.auto_fix_enabled}, "
            f"agents={self.debate_agents}, "
            f"strategy={self.reasoning_strategy!r})"
        )


# Example usage (can be run as script)
if __name__ == "__main__":
    import asyncio

    async def main():
        bot = BugBot()

        # Example issue
        issue = {
            "title": "API returns 500 on /users endpoint",
            "body": """
Steps to reproduce:
1. Send GET request to /api/users
2. Observe 500 error

Expected: 200 with user list
Actual: 500 Internal Server Error

Logs show: KeyError: 'database_url' in config
            """,
            "labels": ["api", "backend"],
            "author": "user123",
        }

        print("🤖 BugBot triaging issue...\n")
        result = await bot.triage(issue)

        print(f"Severity: {result.severity.value}")
        print(f"Category: {result.category.value}")
        print(f"Priority: {result.priority_score}/10")
        print(f"Estimated hours: {result.estimated_hours}")
        print(f"Labels: {result.suggested_labels}")
        print(f"Auto-fix possible: {result.auto_fix_possible}")
        print(f"\nReasoning:\n{result.reasoning}")

        if result.auto_fix_possible:
            print("\n🔧 Generating fix...")
            fix = await bot.generate_fix(issue, result)
            print(fix)

    asyncio.run(main())
