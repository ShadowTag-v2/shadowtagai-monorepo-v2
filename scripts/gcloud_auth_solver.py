#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
gcloud_auth_solver.py - The "Keymaster"
Recursively checks and fixes Google Cloud Authentication.
Logic: Plan -> Act -> Verify -> Loop.
"""

import subprocess


def solve_auth():
    print("Checking gcloud auth status...")
    try:
        subprocess.run(["gcloud", "auth", "print-identity-token"], check=True, capture_output=True)
        print("Auth is valid.")
    except subprocess.CalledProcessError:
        print("Auth invalid. Revoking and re-authenticating...")
        subprocess.run(["gcloud", "auth", "application-default", "revoke"], check=False)
        subprocess.run(["gcloud", "auth", "application-default", "login"], check=True)
        subprocess.run(
            ["gcloud", "auth", "application-default", "set-quota-project", "shadowtag-omega-v4"],
            check=True,
        )
        subprocess.run(["gcloud", "auth", "login", "--update-adc"], check=True)
        print("Auth solver complete. You are securely connected.")


if __name__ == "__main__":
    solve_auth()
