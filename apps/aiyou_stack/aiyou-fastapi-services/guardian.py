# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Guardian - Self-Healing Code Loop & Watchdog
Part of the Omega Protocol.

ARCHITECTURE NOTE (2026-04-18):
    guardian.py provides a basic retry-with-LLM-suggestion pattern.
    It is a VALID lab artifact for local experimentation.
    Production workloads MUST use Google Cloud Tasks (see GEMINI.md queue doctrine).
    This file is NOT a production component — it is a local developer utility.

Status: Lab utility (not production). Retained as operational tooling.
Queue Doctrine: Google Cloud Tasks is the EXCLUSIVE production queue broker.
"""

import subprocess
import sys
import time

# Configuration
MAX_RETRIES = 3


def run_with_guardian(command: str) -> bool:
    """Run a command with Guardian monitoring.

    This is a LOCAL DEVELOPER UTILITY for retry-with-suggestion.
    Production workloads use Google Cloud Tasks for orchestration.
    """
    print(f"🛡️ Guardian watching: {command}")

    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            print(f"✅ Execution successful.\n{result.stdout}")
            return True

        except subprocess.CalledProcessError as e:
            attempts += 1
            print(f"❌ Error detected (Attempt {attempts}/{MAX_RETRIES})")
            print(f"   Exit Code: {e.returncode}")
            stderr_preview = e.stderr[:500] if e.stderr else "(no stderr)"
            print(f"   Stderr: {stderr_preview}")

            if attempts < MAX_RETRIES:
                print("🏥 Initiating Self-Healing Protocol...")
                fix_suggestion = _ask_gemini_for_fix(command, e.stderr)
                print(f"   Gemini Suggestion: {fix_suggestion}")
                # Backoff before retry
                time.sleep(2**attempts)
            else:
                print("💀 Max retries reached. Guardian aborting.")
                return False

    return False


def _ask_gemini_for_fix(command: str, error_log: str) -> str:
    """Ask Gemini for a fix suggestion.

    NOTE: In a full implementation, this calls Vertex AI / Gemini API.
    Currently returns a heuristic suggestion for local dev use.
    Production error analysis uses the CounselConduit Oracle Studio pipeline.
    """
    # Heuristic suggestion for local development
    error_preview = error_log[:200] if error_log else "(no error log)"
    return (
        f"Check dependencies or syntax in script related to '{command}'. "
        f"Error preview: {error_preview}. Consider running with --verbose for more detail."
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python guardian.py '<command_to_run>'")
        sys.exit(1)

    cmd = sys.argv[1]
    success = run_with_guardian(cmd)
    sys.exit(0 if success else 1)
