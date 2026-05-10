#!/usr/bin/env python3
"""gcloud_auth_solver.py - The "Keymaster"
Recursively checks and fixes Google Cloud Authentication.
Logic: Plan -> Act -> Verify -> Loop.
"""

import subprocess


def solve_auth() -> None:
  try:
    subprocess.run(
      ["gcloud", "auth", "print-identity-token"], check=True, capture_output=True
    )
  except subprocess.CalledProcessError:
    subprocess.run(["gcloud", "auth", "application-default", "revoke"], check=False)
    subprocess.run(["gcloud", "auth", "application-default", "login"], check=True)
    subprocess.run(
      [
        "gcloud",
        "auth",
        "application-default",
        "set-quota-project",
        "shadowtag-omega-v4",
      ],
      check=True,
    )
    subprocess.run(["gcloud", "auth", "login", "--update-adc"], check=True)


if __name__ == "__main__":
  solve_auth()
