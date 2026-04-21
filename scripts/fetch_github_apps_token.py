import sys
import time

import jwt
import requests


def get_installation_token(app_id: int, pem_file_path: str, repo_owner: str, repo_name: str) -> str:
    with open(pem_file_path) as f:
        cert_bytes = f.read()

    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + (10 * 60), "iss": str(app_id)}

    encoded_jwt = jwt.encode(payload, cert_bytes, algorithm="RS256")
    headers = {
        "Authorization": f"Bearer {encoded_jwt}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Getting the installation ID for the repo
    repo_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/installation"
    r = requests.get(repo_url, headers=headers, timeout=30)
    if r.status_code != 200:
        sys.exit(1)

    inst_id = r.json()["id"]

    # Getting the token
    token_url = f"https://api.github.com/app/installations/{inst_id}/access_tokens"
    r2 = requests.post(token_url, headers=headers, timeout=30)
    if r2.status_code != 201:
        sys.exit(1)

    return r2.json()["token"]


if __name__ == "__main__":
    # target 1: ehanc69
    token_src = get_installation_token(
        3018080,
        "/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem",
        "ehanc69",
        "ShadowTag-v2-fastapi-services",
    )

    # target 2: ShadowTag-v2
    token_dest = get_installation_token(
        3018200,
        "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem",
        "ShadowTag-v2",
        "Monorepo-Uphillsnowball",
    )
