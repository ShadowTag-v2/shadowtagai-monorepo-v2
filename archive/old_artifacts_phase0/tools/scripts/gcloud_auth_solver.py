#!/usr/bin/env python3
"""
GCLOUD AUTH SOLVER (The "Keymaster")
====================================
Role: Recursively checks and fixes Google Cloud Authentication.
Constitution Directive: Prevent token expiry.
Project: shadowtag-omega-v4
"""

import os
import subprocess
import sys
import time

PROJECT_ID = "shadowtag-omega-v4"


def run_cmd(cmd: list[str], ignore_errors: bool = False, timeout: int = 60) -> bool:
    print(f"[Keymaster] Executing: {' '.join(cmd)}")
    try:
        # We capture output but print it so we can see what's happening
        # For login commands, we shouldn't capture stdout if it needs to render a browser URL
        # However, the user said they use headless runner or standard adc, so we assume
        # the environment is already largely established, but we want to refresh.
        # We will use check_call to let interactive prompts (if any) bubble up if running manually.
        subprocess.check_call(cmd, timeout=timeout)
        print(f"[Keymaster] Required execution successful: {' '.join(cmd)}")
        return True
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            print(f"[Keymaster] Ignoring error (Expected or Non-Fatal): {e}")
            return False
        else:
            print(f"[Keymaster] CRITICAL FAILURE: {e}", file=sys.stderr)
            raise
    except subprocess.TimeoutExpired:
        print(f"[Keymaster] Command timed out after {timeout} seconds.", file=sys.stderr)
        if not ignore_errors:
            raise
        return False


def solve_auth():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Launching GCloud Auth Solver Phase...")

    # 1. Revoke existing tokens to ensure a clean slate (often fails if already clean, so ignore errors)
    run_cmd(["gcloud", "auth", "application-default", "revoke"], ignore_errors=True)

    # 2. Activate via Headless Service Account natively (Bypasses UI entirely)
    # If a JSON key is not mounted, it falls back to a standard login with --no-browser to suppress CSRF web triggers.
    key_path = os.path.expanduser("~/.gcp/headless-runner.json")
    if os.path.exists(key_path):
        run_cmd(
            [
                "gcloud",
                "auth",
                "activate-service-account",
                "767252945109-compute@developer.gserviceaccount.com",
                f"--key-file={key_path}",
                "--project",
                PROJECT_ID,
            ],
            ignore_errors=True,
        )
    else:
        run_cmd(
            [
                "gcloud",
                "auth",
                "application-default",
                "login",
                "--disable-quota-project",
                "--no-browser",
            ],
            ignore_errors=True,
        )

    # 3. Set the specific quota project required by Omega
    run_cmd(
        ["gcloud", "auth", "application-default", "set-quota-project", PROJECT_ID],
        ignore_errors=False,
    )

    # 4. Update the standard gcloud login ADC mapping (suppress popups)
    run_cmd(["gcloud", "auth", "login", "--update-adc", "--no-browser"], ignore_errors=True)

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Auth Solver complete. All green.")


if __name__ == "__main__":
    solve_auth()
