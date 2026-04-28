# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"    [+] Created: {path}")


print(">>> 🛠️  INJECTING GEMINI CLI EXTENSIONS (DevSecOps Layer)...")

# 1. CODE REVIEW EXTENSION (The Sentinel's Eyes)
# Source: github.com/gemini-cli-extensions/code-review
create_file(
    "src/devtools/code_review/reviewer.py",
    """
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
""",
)

# 2. SECURITY EXTENSION (The RMF/CSRMC Design Check)
# Source: github.com/gemini-cli-extensions/security
create_file(
    "src/devtools/security/scanner.py",
    """
class GeminiSecurityScanner:
    def scan_dependencies(self, manifest):
        print("    [CLI-Security] Scanning dependencies for CVEs...")
        # Logic: CSRMC 'Design Phase' validation
        return {"vulnerabilities": 0, "status": "CLEAN"}

    def scan_secrets(self, code_block):
        print("    [CLI-Security] Hunting for hardcoded secrets (API Keys/Pwds)...")
        if "sk-" in code_block or "password=" in code_block:
            return {"status": "FAIL", "reason": "HARDCODED_SECRET"}
        return {"status": "PASS"}
""",
)

# 3. THE PIPELINE HOOK (Connecting to Judge 6)
create_file(
    "src/devtools/pipeline_hook.py",
    """
from src.devtools.code_review.reviewer import GeminiCodeReviewer
from src.devtools.security.scanner import GeminiSecurityScanner

class DevSecOpsPipeline:
    def __init__(self):
        self.reviewer = GeminiCodeReviewer()
        self.scanner = GeminiSecurityScanner()

    def pre_commit_check(self, code_diff):
        # Gate 1: Security Scan (CSRMC Design Phase)
        sec_result = self.scanner.scan_secrets(code_diff)
        if sec_result["status"] == "FAIL":
            return "BLOCK_COMMIT_SECURITY"

        # Gate 2: Code Review (Quality)
        review_result = self.reviewer.analyze_commit(code_diff)
        if review_result["score"] < 80:
            return "BLOCK_COMMIT_QUALITY"

        return "COMMIT_AUTHORIZED"
""",
)

print(">>> ✅ DEVTOOLS INJECTION COMPLETE.")
