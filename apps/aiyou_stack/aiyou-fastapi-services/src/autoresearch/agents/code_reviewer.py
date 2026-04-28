# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""CodeReviewer - Automated code review agent.
Uses Jura for risk assessment + BugBot for static analysis.
"""

import json

from agents.bugbot import BugBot
from agents.jura_protocol import JuraProtocol


class CodeReviewer:
    """Automated code review combining static analysis and AI assessment."""

    def __init__(self, project_id: str = None):
        self.jura = JuraProtocol(project_id=project_id)
        self.bugbot = BugBot()

    def review_file(self, file_path: str) -> dict:
        """Review a single file."""
        print(f"///▞ CODE REVIEWER :: Reviewing {file_path}")

        try:
            with open(file_path) as f:
                code = f.read()
        except Exception as e:
            return {"status": "error", "message": str(e)}

        # Get Jura risk assessment
        jura_result = self.jura.quick_assess(code)

        return {
            "file": file_path,
            "jura_assessment": jura_result,
            "recommendation": jura_result.get("recommendation", "UNKNOWN"),
        }

    def review_pr(self, changed_files: list[str]) -> dict:
        """Review a pull request's changed files."""
        print(f"///▞ CODE REVIEWER :: Reviewing PR with {len(changed_files)} files")

        results = []
        issues = []

        for file_path in changed_files:
            if file_path.endswith(".py"):
                review = self.review_file(file_path)
                results.append(review)

                if review.get("jura_assessment", {}).get("risk_tier", 0) >= 4:
                    issues.append(
                        {
                            "file": file_path,
                            "risk_tier": review["jura_assessment"]["risk_tier"],
                            "issues": review["jura_assessment"].get("issues", []),
                        },
                    )

        # Run BugBot on the whole project
        bugbot_results = self.bugbot.full_scan("src/")

        overall_recommendation = "APPROVE"
        if issues or bugbot_results.get("health_score", 100) < 70:
            overall_recommendation = "REQUEST_CHANGES"

        return {
            "files_reviewed": len(results),
            "high_risk_files": len(issues),
            "bugbot_health_score": bugbot_results.get("health_score", 0),
            "recommendation": overall_recommendation,
            "details": {"file_reviews": results, "issues": issues, "bugbot": bugbot_results},
        }

    def generate_review_comment(self, review_results: dict) -> str:
        """Generate a PR review comment."""
        rec = review_results["recommendation"]
        health = review_results["bugbot_health_score"]

        comment = "## 🤖 Code Review by ShadowTagAi\n\n"
        comment += f"**Recommendation:** {rec}\n"
        comment += f"**Health Score:** {health}/100\n\n"

        if review_results["high_risk_files"] > 0:
            comment += "### ⚠️ High Risk Files\n"
            for issue in review_results["details"]["issues"]:
                comment += f"- `{issue['file']}` (Risk Tier: {issue['risk_tier']})\n"
                for i in issue.get("issues", []):
                    comment += f"  - {i}\n"
            comment += "\n"

        if health < 70:
            comment += "### 📊 BugBot Analysis\n"
            details = review_results["details"]["bugbot"]["details"]
            comment += f"- Pylint issues: {details['pylint'].get('issues', 0)}\n"
            comment += f"- Type errors: {details['mypy'].get('issues', 0)}\n"
            comment += f"- Security issues: {details['security'].get('issues', 0)}\n"

        comment += "\n---\n*Reviewed by Jura (ATP 5-19) + BugBot*"

        return comment


if __name__ == "__main__":
    reviewer = CodeReviewer()
    # Example usage
    result = reviewer.review_pr(["src/ShadowTag-v2/services/gemini_core.py"])
    print(json.dumps(result, indent=2))
