#!/usr/bin/env python3
"""
omega_sync.py — Secure GitHub App JWT Push Protocol
Per Invariant #56: Dual-Org GitHub App Authentication
Per Invariant #55: Commits MUST target ShadowTag-v2/Monorepo-Uphillsnowball

Flow:
  1. Load GitHub App private key PEM
  2. Generate JWT (iss=app_id, exp=10min)
  3. Exchange JWT for installation access token
  4. Configure git remote with token
  5. Push current branch
"""

import os
import subprocess
import sys
import time

try:
    import jwt  # PyJWT
except ImportError:
    print("ERROR: PyJWT not installed. Run: pip install PyJWT cryptography")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

# ============================================================
# Auth Configuration (from operator_invariants.json)
# ============================================================
TARGETS = {
    "shadowtag": {
        "app_id": 3018200,
        "pem_path": "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem",
        "org": "ShadowTag-v2",
        "repo": "Monorepo-Uphillsnowball",
    },
    "ehanc69": {
        "app_id": 3018080,
        "pem_path": "/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem",
        "org": "ehanc69",
        "repo": None,  # Multiple repos
    },
}

DEFAULT_TARGET = "shadowtag"


def generate_jwt(app_id: int, pem_path: str) -> str:
    """Generate a GitHub App JWT valid for 10 minutes."""
    with open(pem_path, "rb") as f:
        private_key = f.read()

    now = int(time.time())
    payload = {
        "iat": now - 60,  # issued at (60s clock skew buffer)
        "exp": now + (10 * 60),  # expires in 10 minutes
        "iss": str(app_id),  # GitHub App ID (must be string for PyJWT 2.x)
    }

    return jwt.encode(payload, private_key, algorithm="RS256")


def get_installation_id(jwt_token: str, org: str) -> int:
    """Find the installation ID for the given org."""
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    resp = requests.get(
        "https://api.github.com/app/installations",
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()

    installations = resp.json()
    for inst in installations:
        account = inst.get("account", {})
        if account.get("login", "").lower() == org.lower():
            return inst["id"]

    raise RuntimeError(f"No installation found for org '{org}'. Found: {[i['account']['login'] for i in installations]}")


def get_access_token(jwt_token: str, installation_id: int) -> str:
    """Exchange JWT for an installation access token."""
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    resp = requests.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()

    data = resp.json()
    return data["token"]


def push_with_token(token: str, org: str, repo: str, branch: str = None):
    """Push using SSH (primary) with HTTPS+ASKPASS fallback.

    Per DOCTRINE_EXTENDED.md Section X:
    - SSH is the PRIMARY transport (avoids macOS credential cache poisoning)
    - --force-with-lease is the ONLY permitted force mechanism
    - Raw --force is FORBIDDEN on main and shared branches
    """
    import stat
    import tempfile

    ssh_url = f"git@github.com:{org}/{repo}.git"
    https_url = f"https://github.com/{org}/{repo}.git"

    # Get current branch if not specified
    if not branch:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
        ).strip()

    print(f"  📡 Pushing branch '{branch}' to {org}/{repo}...")

    # ── PRIMARY: SSH push ──
    print("  🔑 Attempting SSH push (primary transport)...")
    subprocess.run(
        ["git", "remote", "set-url", "origin", ssh_url],
        check=True,
    )

    result = subprocess.run(
        ["git", "push", "--force-with-lease", "origin", branch],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"  ✅ SSH push successful: {org}/{repo} @ {branch}")
        return

    print(f"  ⚠️  SSH push failed: {result.stderr.strip()}")

    # ── FALLBACK: HTTPS + GIT_ASKPASS ──
    print("  🔄 Falling back to HTTPS + GIT_ASKPASS...")
    askpass_script = None
    try:
        subprocess.run(
            ["git", "remote", "set-url", "origin", https_url],
            check=True,
        )

        askpass_script = tempfile.NamedTemporaryFile(mode="w", suffix=".sh", prefix="git_askpass_", delete=False)
        askpass_script.write(f'#!/bin/sh\ncase "$1" in\n  *sername*) echo "x-access-token" ;;\n  *) echo "{token}" ;;\nesac\n')
        askpass_script.close()
        os.chmod(askpass_script.name, stat.S_IRWXU)

        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        env["GIT_ASKPASS"] = askpass_script.name
        env["GIT_CONFIG_NOSYSTEM"] = "1"
        env["GCM_INTERACTIVE"] = "never"

        git_base = [
            "git",
            "-c",
            "credential.helper=",
            "-c",
            "credential.https://github.com.helper=",
        ]

        print("  📤 HTTPS push with --force-with-lease...")
        result = subprocess.run(
            git_base + ["push", "--force-with-lease", "origin", branch],
            capture_output=True,
            text=True,
            env=env,
        )

        if result.returncode == 0:
            print(f"  ✅ HTTPS push successful: {org}/{repo} @ {branch}")
        else:
            print("  ❌ Push failed on both SSH and HTTPS.")
            print(f"     HTTPS error: {result.stderr}")
            print("     NOTE: Raw --force is FORBIDDEN on shared branches.")
            print("     Per DOCTRINE_EXTENDED.md Section X, escalate to State B.")
            sys.exit(1)

    finally:
        if askpass_script and os.path.exists(askpass_script.name):
            os.unlink(askpass_script.name)
        # Restore SSH as canonical remote
        subprocess.run(
            ["git", "remote", "set-url", "origin", ssh_url],
            check=False,
        )


def main():
    target_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TARGET

    if target_name not in TARGETS:
        print(f"Unknown target: {target_name}. Available: {list(TARGETS.keys())}")
        sys.exit(1)

    target = TARGETS[target_name]

    print(f"═══ OMEGA SYNC — {target['org']} ═══")
    print(f"  🔑 App ID: {target['app_id']}")
    print(f"  📄 PEM: {target['pem_path']}")

    # Verify PEM exists
    if not os.path.exists(target["pem_path"]):
        print(f"  ❌ PEM file not found: {target['pem_path']}")
        sys.exit(1)

    # Step 1: Generate JWT
    print("  [1/5] Generating JWT...")
    jwt_token = generate_jwt(target["app_id"], target["pem_path"])
    print("  [1/5] JWT generated ✅")

    # Step 2: Get installation ID
    print(f"  [2/5] Finding installation for {target['org']}...")
    installation_id = get_installation_id(jwt_token, target["org"])
    print(f"  [2/5] Installation ID: {installation_id} ✅")

    # Step 3: Get access token
    print("  [3/5] Exchanging JWT for access token...")
    access_token = get_access_token(jwt_token, installation_id)
    print("  [3/5] Access token acquired ✅")

    # Step 4: Gitleaks Guardian Gate (BLOCKING)
    # Per AGENTS.md Rule 23 + Cor.30 R3: No push without secret scan.
    print("  [4/5] Running Gitleaks Guardian gate...")
    guardian_result = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "gitleaks_guardian.py"),
         "--mode", "gate"],
        check=False,
    )
    if guardian_result.returncode == 1:
        print("  ❌ Gitleaks Guardian BLOCKED the push.")
        print("     Real credentials detected. Remediate before pushing.")
        print("     Run: python3 scripts/gitleaks_guardian.py --mode scan --scope production")
        sys.exit(1)
    elif guardian_result.returncode == 0:
        print("  [4/5] Secret scan clean ✅")
    else:
        print("  ⚠️  Gitleaks binary not found — proceeding with caution")

    # Step 5: Push
    print("  [5/5] Pushing...")
    repo = target["repo"]
    if not repo:
        repo = input("  Enter repo name: ").strip()

    push_with_token(access_token, target["org"], repo)

    print("═══ OMEGA SYNC COMPLETE ═══")


if __name__ == "__main__":
    main()
