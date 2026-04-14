"""Guardian - Self-Healing Code Loop & Watchdog
Part of the Omega Protocol.

Monitors execution, catches errors, and prompts Gemini for fixes.
"""

import subprocess
import sys

# Configuration
MAX_RETRIES = 3
GEMINI_MODEL = "gemini-3.0-flash"  # Fast model for quick fixes


def run_with_guardian(command: str):
    """Run a command with Guardian monitoring.
    """
    print(f"🛡️ Guardian watching: {command}")

    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            # Execute command
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            print(f"✅ Execution successful.\n{result.stdout}")
            return True

        except subprocess.CalledProcessError as e:
            attempts += 1
            print(f"❌ Error detected (Attempt {attempts}/{MAX_RETRIES})")
            print(f"   Exit Code: {e.returncode}")
            print(f"   Stderr: {e.stderr[:500]}...")  # truncate for brevity

            if attempts < MAX_RETRIES:
                print("🏥 Initiating Self-Healing Protocol...")
                fix_suggestion = _ask_gemini_for_fix(command, e.stderr)
                # In a fully autonomous loop, we might apply the fix.
                # For safety, we currently log it.
                print(f"   Gemini Suggestion: {fix_suggestion}")
                # TODO: Implement auto-apply of patches if safe

            else:
                print("💀 Max retries reached. Guardian aborting.")
                return False


def _ask_gemini_for_fix(command: str, error_log: str) -> str:
    """Simulate asking Gemini for a fix.
    In production, this would call the actual Vertex AI/Gemini API.
    """
    # Mock response for now
    return (
        f"Check dependencies or syntax in script related to '{command}'. Error indicates failure."
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python guardian.py '<command_to_run>'")
        sys.exit(1)

    cmd = sys.argv[1]
    run_with_guardian(cmd)
