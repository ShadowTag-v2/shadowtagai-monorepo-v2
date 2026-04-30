#!/usr/bin/env python3
"""GitHub App JWT-based PR creator. Replaces `gh pr create` for doctrine compliance."""

import json
import os
import sys
import time

try:
    import jwt
    import requests
except ImportError:
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyJWT", "requests", "--quiet"])
    import jwt
    import requests

APP_ID = "3018200"
REPO = "ShadowTag-v2/Monorepo-Uphillsnowball"

# 5-tier PEM fallback chain per GEMINI.md
PEM_CANDIDATES = [
    os.environ.get("SHADOWTAG_PEM", ""),
    os.path.expanduser("~/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"),
    "keys/antigravity-shadowtag-manager.pem",
    os.path.expanduser("~/.ssh/antigravity-shadowtag-manager.pem"),
]


def find_pem():
    for p in PEM_CANDIDATES:
        if p and os.path.isfile(p):
            return p
    return None


def get_installation_token():
    pem_path = find_pem()
    if not pem_path:
        print("[!] No PEM found in 5-tier fallback chain. PRs will be skipped.")
        return None

    with open(pem_path, "rb") as f:
        signing_key = f.read()

    payload = {
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + 600,
        "iss": APP_ID,
    }
    encoded_jwt = jwt.encode(payload, signing_key, algorithm="RS256")
    headers = {
        "Authorization": f"Bearer {encoded_jwt}",
        "Accept": "application/vnd.github.v3+json",
    }

    resp = requests.get(f"https://api.github.com/repos/{REPO}/installation", headers=headers, timeout=15)
    if resp.status_code != 200:
        print(f"[!] Installation lookup failed: {resp.status_code} {resp.text[:200]}")
        return None

    inst_id = resp.json()["id"]
    resp = requests.post(
        f"https://api.github.com/app/installations/{inst_id}/access_tokens",
        headers=headers,
        timeout=15,
    )
    if resp.status_code != 201:
        print(f"[!] Token generation failed: {resp.status_code} {resp.text[:200]}")
        return None

    return resp.json()["token"]


def create_pr(token, branch, title, body, base="main"):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "title": title,
        "head": branch,
        "base": base,
        "body": body,
    }
    resp = requests.post(
        f"https://api.github.com/repos/{REPO}/pulls",
        headers=headers,
        json=data,
        timeout=30,
    )
    if resp.status_code == 201:
        pr_url = resp.json().get("html_url", "unknown")
        print(f"  ✅ PR created: {pr_url}")
        return True
    elif resp.status_code == 422:
        # PR already exists or validation error
        print(f"  ⚠️  PR already exists or validation error: {resp.json().get('message', '')}")
        return False
    else:
        print(f"  ❌ PR creation failed ({resp.status_code}): {resp.text[:200]}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: pr_creator.py <pr_manifest.json>")
        sys.exit(1)

    manifest_path = sys.argv[1]
    with open(manifest_path) as f:
        prs = json.load(f)

    token = get_installation_token()
    if not token:
        print("[!] Could not obtain GitHub App token. Branches are pushed but PRs not created.")
        print("[!] Run manually: open https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball/branches")
        sys.exit(1)

    created = 0
    for pr in prs:
        print(f"→ Creating PR: {pr['title']}")
        if create_pr(token, pr["branch"], pr["title"], pr["body"]):
            created += 1

    print(f"\n✅ {created}/{len(prs)} PRs created successfully.")


if __name__ == "__main__":
    main()
