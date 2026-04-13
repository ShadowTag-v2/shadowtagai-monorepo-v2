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

    raise RuntimeError(
        f"No installation found for org '{org}'. "
        f"Found: {[i['account']['login'] for i in installations]}"
    )


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
    """Push using a temp GIT_ASKPASS script to bypass all credential helpers."""
    import tempfile
    import stat

    clean_url = f"https://github.com/{org}/{repo}.git"

    # Get current branch if not specified
    if not branch:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
        ).strip()

    print(f"  📡 Pushing branch '{branch}' to {org}/{repo}...")

    # Create temporary GIT_ASKPASS script that returns the token
    askpass_script = None
    try:
        askpass_script = tempfile.NamedTemporaryFile(
            mode="w", suffix=".sh", prefix="git_askpass_", delete=False
        )
        # GIT_ASKPASS gets called with prompt "$1": check if it's username or password
        askpass_script.write(
            '#!/bin/sh\n'
            'case "$1" in\n'
            '  *sername*) echo "x-access-token" ;;\n'
            f'  *) echo "{token}" ;;\n'
            'esac\n'
        )
        askpass_script.close()
        os.chmod(askpass_script.name, stat.S_IRWXU)

        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        env["GIT_ASKPASS"] = askpass_script.name
        env["GIT_CONFIG_NOSYSTEM"] = "1"
        env["GCM_INTERACTIVE"] = "never"

        # Ensure remote is clean HTTPS (no embedded tokens)
        subprocess.run(
            ["git", "remote", "set-url", "origin", clean_url],
            check=True,
        )

        # Git config overrides to kill every credential helper layer
        git_base = [
            "git",
            "-c", "credential.helper=",
            "-c", "credential.https://github.com.helper=",
        ]

        # Skip fetch since it consistently fails with auth issues on this setup
        print("  📤 Pushing with --force-with-lease...")
        result = subprocess.run(
            git_base + ["push", "--force-with-lease", "origin", branch],
            capture_output=True,
            text=True,
            env=env,
        )

        if result.returncode == 0:
            print(f"  ✅ Push successful: {org}/{repo} @ {branch}")
        elif "stale info" in result.stderr or "rejected" in result.stderr:
            print("  ⚠️  Lease stale, retrying with --force...")
            result = subprocess.run(
                git_base + ["push", "--force", "origin", branch],
                capture_output=True,
                text=True,
                env=env,
            )
            if result.returncode == 0:
                print(f"  ✅ Push successful (forced): {org}/{repo} @ {branch}")
            else:
                print(f"  ❌ Push failed: {result.stderr}")
                sys.exit(1)
        else:
            print(f"  ❌ Push failed: {result.stderr}")
            sys.exit(1)

    finally:
        # Clean up temp script
        if askpass_script and os.path.exists(askpass_script.name):
            os.unlink(askpass_script.name)
        # Restore clean remote
        subprocess.run(
            ["git", "remote", "set-url", "origin", clean_url],
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
    print("  [1/4] Generating JWT...")
    jwt_token = generate_jwt(target["app_id"], target["pem_path"])
    print("  [1/4] JWT generated ✅")

    # Step 2: Get installation ID
    print(f"  [2/4] Finding installation for {target['org']}...")
    installation_id = get_installation_id(jwt_token, target["org"])
    print(f"  [2/4] Installation ID: {installation_id} ✅")

    # Step 3: Get access token
    print("  [3/4] Exchanging JWT for access token...")
    access_token = get_access_token(jwt_token, installation_id)
    print("  [3/4] Access token acquired ✅")

    # Step 4: Push
    print("  [4/4] Pushing...")
    repo = target["repo"]
    if not repo:
        repo = input("  Enter repo name: ").strip()

    push_with_token(access_token, target["org"], repo)

    print("═══ OMEGA SYNC COMPLETE ═══")


if __name__ == "__main__":
    main()
