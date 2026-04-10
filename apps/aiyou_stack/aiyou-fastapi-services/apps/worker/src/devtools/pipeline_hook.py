import argparse
import os
import subprocess
import sys

from src.devtools.security.scanner import GeminiSecurityScanner

# Ensure the project root is in the Python path for robust module resolution.
# This is crucial for pre-commit hooks that run from different directories.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Add apps/n-autoresearch/Kosmos/BioAgents-server to path to find src.memory if needed,
# or ensure src/memory is reachable.
# The user's snippet imports from src.memory, implying src is a root.
# We'll make sure we can import from src.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


from apps.n-autoresearch/Kosmos/BioAgents_server.src.memory import (
    get_memory_storage,  # Adjusted path based on previous file exploration
)

from src.governance.judge_six.core import JudgeSixEngine


class DevSecOpsPipeline:
    """
    Integrates security scanning and Judge 6 governance into the development lifecycle.
    """

    def __init__(self) -> None:
        """
        Initializes the pipeline with a security scanner and Judge 6 as the
        central authority, conceptually powered by Gemini 2.5 Pro.
        """
        self.scanner = GeminiSecurityScanner()
        self.judge6 = JudgeSixEngine()
        self.memory = get_memory_storage()

    def pre_commit_check(self, code_diff: str) -> str:
        """
        Runs a series of checks on a given code diff.

        Args:
            code_diff: A string containing the code changes (diff format).

        Returns:
            A string indicating the result of the check.
        """
        # Gate 1: Security Scan (Fast pre-check)
        print("🔍 Running preliminary security scan...")
        sec_result = self.scanner.scan_secrets(code_diff)
        if sec_result.get("status") == "FAIL":
            print("❌ BLOCKED: Security Violation (Hardcoded Secret detected)")
            return "BLOCK_COMMIT_SECURITY"

        # Gate 2: Judge 6 Oversight (Comprehensive review)
        print("🤖 Engaging Judge 6 for pre-commit oversight...")
        try:
            context = self.memory.load_from_firestore()
        except Exception as e:
            print(
                f"⚠️ Warning: Could not load context from Firestore. Proceeding without it. Error: {e}"
            )
            context = {}

        mission_id = context.get("current_mission_id", "PRE_COMMIT_REVIEW")
        telemetry = context.get("telemetry", {"source": "pre-commit-hook"})

        decision = self.judge6.execute_mission(
            mission_id=mission_id, telemetry=telemetry, priority="ROUTINE", payload=code_diff
        )

        if not decision.approved:
            print(
                f"🛑 COMMIT BLOCKED by Judge 6. Risk Tier: {decision.risk_tier}, Authority: {decision.authority}"
            )
            return "BLOCK_COMMIT_JUDGE6"

        print(f"✅ COMMIT AUTHORIZED by Judge 6. Hash: {decision.shadowtag_hash}")
        return "COMMIT_AUTHORIZED"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DevSecOps Pipeline Hook for Pre-Commit and CI.")
    parser.add_argument(
        "--ci", action="store_true", help="Run in CI mode, diffing against the main branch."
    )
    parser.add_argument("filenames", nargs="*", help="Filenames passed by pre-commit hook.")
    args = parser.parse_args()

    pipeline = DevSecOpsPipeline()
    diff_to_check = ""

    if args.ci:
        print("🚀 Running Judge 6 validation in CI mode...")
        try:
            # In CI, we compare the current commit against the main branch.
            # Cloud Build may do a shallow clone, so we fetch more history.
            print("Fetching git history to compare with main branch...")
            subprocess.run(
                ["git", "fetch", "origin", "main", "--unshallow"], check=False, capture_output=True
            )
            diff_to_check = subprocess.check_output(["git", "diff", "origin/main...HEAD"]).decode(
                "utf-8"
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Error getting git diff in CI mode: {e.stderr.decode()}")
            sys.exit(1)
    elif args.filenames:
        print("🔍 Running pre-commit check on staged files...")
        try:
            # For pre-commit, get the full staged diff. The hook is already filtered by the `files` pattern.
            diff_to_check = subprocess.check_output(["git", "diff", "--staged"]).decode("utf-8")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error getting git diff for staged files: {e.stderr.decode()}")
            sys.exit(1)

    if not diff_to_check.strip():
        print("✅ No diff content to analyze. Skipping Judge 6.")
        sys.exit(0)

    result = pipeline.pre_commit_check(diff_to_check)
    sys.exit(0 if "AUTHORIZED" in result else 1)
