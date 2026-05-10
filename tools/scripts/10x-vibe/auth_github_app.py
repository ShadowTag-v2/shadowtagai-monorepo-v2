#!/usr/bin/env python3
"""
GitHub App Authentication Helper — TACSOP 5 Compliant
Generates short-lived Installation Access Tokens for secure pushes.
Supports: --push, --push-ref, --renew-token, --dry-run
"""

import os
import sys
import time
import subprocess
import argparse
import jwt  # PyJWT
import requests

# Config from TACSOP / operator invariants
APP_ID = os.getenv("GITHUB_APP_ID", "3018200")
CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "Iv23ctYqrxPQIt2ir8gY")
REPO = os.getenv("GITHUB_REPO", "ShadowTag-v2/shadowtagai-monorepo-v2")
DEFAULT_BRANCH = "main"

# 5-tier PEM fallback chain (AGENTS.md doctrine):
# 1. GITHUB_APP_PEM_PATH env var  2. $SHADOWTAG_PEM env var
# 3. ~/Downloads/ canonical location  4. keys/ directory  5. ~/.ssh/
_PEM_CANDIDATES = [
    os.getenv("GITHUB_APP_PEM_PATH", ""),
    os.getenv("SHADOWTAG_PEM", ""),
    os.path.expanduser("~/Downloads/antigravity-shadowtag-manager.2026-03-17.pem"),
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "keys", "github-app.pem"),
    os.path.expanduser("~/.ssh/github-app.pem"),
]


def _resolve_pem() -> str:
    """Resolve PEM path using 5-tier fallback chain."""
    for candidate in _PEM_CANDIDATES:
        if candidate and os.path.exists(candidate):
            return candidate
    return ""


def generate_jwt() -> str:
    """Generate JWT for GitHub App authentication (valid 10 min)."""
    pem_path = _resolve_pem()
    if not pem_path:
        print("❌ PEM file not found. Set GITHUB_APP_PEM_PATH or SHADOWTAG_PEM env var.")
        sys.exit(1)

    with open(pem_path, "r") as f:
        private_key = f.read()

    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + 600,  # 10 minutes
        "iss": APP_ID
    }
    token = jwt.encode(payload, private_key, algorithm="RS256")
    return token

def get_installation_id(jwt_token: str) -> int:
    """Get installation ID for the repo."""
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }
    url = "https://api.github.com/app/installations"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    installations = resp.json()
    
    for inst in installations:
        if inst.get("account", {}).get("login") in REPO.split("/")[0]:
            return inst["id"]
    # Fallback: try to find by repo
    print("⚠️ Could not auto-detect installation, trying repo-specific...")
    # For simplicity, assume first or prompt
    return installations[0]["id"] if installations else None

def get_installation_token(installation_id: int, jwt_token: str) -> str:
    """Exchange for short-lived (1h) Installation Access Token."""
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    resp = requests.post(url, headers=headers)
    resp.raise_for_status()
    return resp.json()["token"]

def push_changes(token: str, refspec: str = None):
    """Perform git push using the token via HTTPS."""
    if not token:
        print("❌ No token provided.")
        return False
    
    # Set up credential helper or use git push with token
    # For safety, use GIT_ASKPASS or extraheader
    env = os.environ.copy()
    env["GIT_ASKPASS"] = "echo"  # Placeholder, better to use credential store in real
    
    # Use token in URL or extra header
    remote_url = f"https://x-access-token:{token}@github.com/{REPO}.git"
    
    cmd = ["git", "push", remote_url]
    if refspec:
        cmd.append(refspec)
    else:
        cmd.extend(["HEAD:refs/heads/" + DEFAULT_BRANCH])
    
    try:
        subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        print("✅ Push successful.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Push failed: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="GitHub App Push Helper")
    parser.add_argument("--push", action="store_true", help="Push current HEAD")
    parser.add_argument("--push-ref", metavar="REFSPEC", help="Push specific refspec e.g. SHA:refs/heads/main")
    parser.add_argument("--renew-token", action="store_true", help="Mint and cache new token (stdout or /tmp)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be pushed without executing")
    parser.add_argument("--print-token", action="store_true", help="Print token (disabled by default for security)")
    
    args = parser.parse_args()
    
    if args.print_token:
        print("❌ --print-token prohibited by TACSOP security rules.")
        sys.exit(1)
    
    jwt_token = generate_jwt()
    installation_id = get_installation_id(jwt_token)
    if not installation_id:
        print("❌ No installation found.")
        sys.exit(1)
    
    token = get_installation_token(installation_id, jwt_token)
    
    if args.renew_token:
        # Cache to /tmp/gh_token_shadowtag.txt for subsequent use
        with open("/tmp/gh_token_shadowtag.txt", "w") as f:
            f.write(token)
        print("✅ Token renewed and cached to /tmp/gh_token_shadowtag.txt")
        return
    
    if args.dry_run:
        print(f"DRY RUN: Would push to {REPO} using fresh token (expires in ~1h)")
        print(f"Token (first 20 chars): {token[:20]}...")
        return
    
    if args.push or args.push_ref:
        refspec = args.push_ref if args.push_ref else None
        success = push_changes(token, refspec)
        if not success:
            sys.exit(1)
    else:
        print("No action specified. Use --push, --push-ref, or --renew-token.")

if __name__ == "__main__":
    main()
