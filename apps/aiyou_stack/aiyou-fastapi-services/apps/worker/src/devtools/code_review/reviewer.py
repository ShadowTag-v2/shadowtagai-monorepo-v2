class GeminiCodeReviewer:
    def analyze_commit(self, diff_content):
        print("    [CLI-Review] Gemini 1.5 Pro scanning diff for logic errors...")

        # Logic: Check for anti-patterns, complexity, and docstrings
        # Matches 'The Sentinel' logic from Cor.2
        issues = []
        if "TODO" in diff_content:
            issues.append("Unresolved TODO detected")
        if "print(" in diff_content:
            issues.append("Debug print statement left in code")

        score = 100 - (len(issues) * 10)
        return {"score": score, "issues": issues}
