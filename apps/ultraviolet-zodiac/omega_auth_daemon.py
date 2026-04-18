#!/usr/bin/env python3
"""omega_auth_daemon.py
--------------------
A persistent daemon that ensures the "headless-runner" service account
remains authenticated by triggering the `gcloud_auth_solver.py` every 3 minutes.

Rationale:
- Service accounts are reported to be detokenized every 3 minutes.
- Renewing at 180 seconds ensures we stay ahead of the expiry.
"""

import os
import subprocess
import sys
import time

SOLVER_SCRIPT = os.path.join(os.path.dirname(__file__), "gcloud_auth_solver.py")
REFRESH_INTERVAL_SECONDS = 180  # 3 minutes

# --- Environment Setup ---
# Force gcloud to use the workspace config to avoid Seatbelt issues
WORKSPACE_CONFIG = "/Users/pikeymickey/.gemini/antigravity/playground/ultraviolet-zodiac/.gcloud_config"
os.environ["CLOUDSDK_CONFIG"] = WORKSPACE_CONFIG


def log(message: str):
    print(
        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [DAEMON] {message}",
        file=sys.stderr,
        flush=True,
    )


def run_command(command: str) -> subprocess.CompletedProcess:
    # Ensure environment is passed to subprocess
    return subprocess.run(command, shell=True, text=True, capture_output=True, env=os.environ)


def verify_token() -> bool:
    """Independent verification of token health."""
    # Using tokeninfo endpoint is a lightweight way to verify the token works.
    token_proc = run_command("gcloud auth print-access-token")
    if token_proc.returncode != 0:
        return False

    token = token_proc.stdout.strip()
    if not token:
        return False

    # Verify against tokeninfo (harmless read)
    # We use curl with a 5s timeout to avoid hanging
    verify_cmd = f"curl -s --max-time 5 -o /dev/null -w '%{{http_code}}' https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={token}"
    result = run_command(verify_cmd)

    return result.stdout.strip() == "200"


def main():
    log("🔵 Omega Auth Daemon Started. PID: " + str(os.getpid()))

    while True:
        log("🔄 Triggering Auth Solver...")
        try:
            # Run the solver synchronously
            # Use sys.executable to ensure we use the same Python environment
            result = subprocess.run(
                [sys.executable, SOLVER_SCRIPT],
                capture_output=True,
                text=True,
                check=False,
                env=os.environ,
            )

            if result.returncode == 0:
                log("✅ Solver Success: " + result.stdout.strip())
                # Independent verification
                if verify_token():
                    log("✅ Token Health Verified.")
                else:
                    log("❌ CRITICAL: Solver reported success, but token verification failed!")
            else:
                log("⚠️ Solver Exit Code " + str(result.returncode) + ": " + result.stderr.strip())

        except Exception as e:
            log(f"⛔ Exception running solver: {e}")

        log(f"💤 Sleeping for {REFRESH_INTERVAL_SECONDS} seconds...")
        time.sleep(REFRESH_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
