import sys
import time

import jwt
import requests

APP_ID = "3018200"
CLIENT_ID = "Iv23ctYqrxPQIt2ir8gY"
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"
REPO_OWNER = "ShadowTag-v2"
REPO_NAME = "Monorepo-Uphillsnowball"


def generate_jwt():
    with open(PEM_PATH, "rb") as f:
        private_key = f.read()
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + (10 * 60), "iss": APP_ID}
    return jwt.encode(payload, private_key, algorithm="RS256")


def get_installation_token() -> None:
    token = generate_jwt()
    headers = {"Accept": "application/vnd.github.v3+json", "Authorization": f"Bearer {token}"}

    # 1. Get Installation ID for the repo
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/installation"
    resp = requests.get(url, headers=headers, timeout=30)

    if resp.status_code != 200:
        sys.exit(1)

    inst_id = resp.json()["id"]

    # 2. Get Access Token
    token_url = f"https://api.github.com/app/installations/{inst_id}/access_tokens"
    resp = requests.post(token_url, headers=headers, timeout=30)

    if resp.status_code != 201:
        sys.exit(1)

    resp.json()["token"]


if __name__ == "__main__":
    get_installation_token()
