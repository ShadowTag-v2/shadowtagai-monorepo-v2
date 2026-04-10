#!/usr/bin/env python3
"""
gcloud_auth_solver.py
---------------------
Implements the "Loop & Review" methodology for reliable GCloud Authentication.
Optimized for headless-runner service account in ShadowTag Omega V4.
"""

import json
import os
import subprocess
import sys
import time

# --- Configuration ---
SA_EMAIL = "redacted@shadowtag-v4.local"
KEY_FILE_PATH = os.path.expanduser("~/.gcp/headless-runner-key.json")

# --- Environment Setup ---
WORKSPACE_CONFIG = "/Users/pikeymickey/.gemini/antigravity/playground/ultraviolet-zodiac/.gcloud_config"
os.environ["CLOUDSDK_CONFIG"] = WORKSPACE_CONFIG


def log(message: str, level: str = "INFO"):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}", file=sys.stderr)


def run_command(command: str) -> subprocess.CompletedProcess:
    return subprocess.run(command, shell=True, text=True, capture_output=True, env=os.environ)


def verify_token() -> bool:
    """Verifies if the current active credential can hit a Google API."""
    token_proc = run_command("gcloud auth print-access-token")
    if token_proc.returncode != 0:
        return False

    token = token_proc.stdout.strip()
    if not token:
        return False

    # Verify against tokeninfo with 5s timeout to avoid hanging
    verify_cmd = f"curl -s --max-time 5 -o /dev/null -w '%{{http_code}}' https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={token}"
    result = run_command(verify_cmd)

    return result.stdout.strip() == "200"


def attempt_auth_strategy(strategy_name: str) -> bool:
    log(f"Attempting Strategy: {strategy_name}")

    if strategy_name == "service_account_key":
        if not os.path.exists(KEY_FILE_PATH):
            log(f"Critique: Key file not found at {KEY_FILE_PATH}", "WARN")
            return False
        cmd = f"gcloud auth activate-service-account {SA_EMAIL} --key-file={KEY_FILE_PATH}"

    elif strategy_name == "application_default":
        cmd = "gcloud auth application-default login --quiet --no-launch-browser"

    else:
        log("Unknown strategy", "ERROR")
        return False

    result = run_command(cmd)
    if result.returncode == 0:
        log(f"Strategy {strategy_name} check command executed successfully.")
        return True
    else:
        log(f"Strategy {strategy_name} failed: {result.stderr}", "ERROR")
        return False


def solve_auth():
    """Recursive Auth Solver Loop."""
    log("🔵 [SOLVER] Starting Auth Loop...")

    if verify_token():
        log("✅ [SOLVER] Auth is already valid.")
        print(json.dumps({"status": "success", "method": "unchanged", "timestamp": time.time()}))
        return

    for strategy in ["service_account_key", "application_default"]:
        log(f"🔄 [SOLVER] Loop Step: Trying {strategy}...")

        if attempt_auth_strategy(strategy):
            if verify_token():
                log(f"✅ [SOLVER] Success via {strategy}.")
                print(json.dumps({"status": "success", "method": strategy, "timestamp": time.time()}))
                return
            else:
                log("⚠️ [SOLVER] Critique: Strategy succeeded, but token is still invalid.")

    log("⛔ [SOLVER] All strategies exhausted. Auth is BROKEN.", "CRITICAL")
    print(json.dumps({"status": "failed", "error": "All strategies failed", "timestamp": time.time()}))
    sys.exit(1)


if __name__ == "__main__":
    solve_auth()
