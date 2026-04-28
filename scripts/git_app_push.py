# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import subprocess
import sys
import time

import jwt
import requests


def get_app_token(app_id, pem_path):
    try:
        with open(pem_path) as f:
            private_key = f.read()
    except FileNotFoundError:
        sys.exit(1)

    payload = {"iat": int(time.time()) - 60, "exp": int(time.time()) + (10 * 60), "iss": app_id}

    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}

    resp = requests.get("https://api.github.com/app/installations", headers=headers, timeout=30)
    installations = resp.json()

    if not installations or "message" in installations:
        sys.exit(1)

    installation_id = installations[0]["id"]

    token_url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    resp2 = requests.post(token_url, headers=headers, timeout=30)
    token_data = resp2.json()

    if "token" not in token_data:
        sys.exit(1)

    return token_data["token"]


def push_repo() -> None:
    # ShadowTag-v2 App Configuration
    APP_ID = "3018200"
    PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"
    # Fallback to ehanc69 App if needed:
    # EHANC69_APP_ID = '3018080'
    # EHANC69_PEM_PATH = '/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem'

    token = get_app_token(APP_ID, PEM_PATH)
    repo_url = f"https://x-access-token:{token}@github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git"

    subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=True)

    try:
        push_proc = subprocess.run(["git", "push", "origin", "HEAD:main"], capture_output=True, text=True)

        if push_proc.returncode == 0:
            if push_proc.stderr:
                pass
        else:
            pass
    finally:
        clean_url = "https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git"
        subprocess.run(["git", "remote", "set-url", "origin", clean_url], check=True)


if __name__ == "__main__":
    push_repo()
