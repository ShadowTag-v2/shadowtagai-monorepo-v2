import os
import subprocess
import sys
import time

import jwt
import requests

APP_ID = "3018200"
PRIVATE_KEY_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"
REPO_OWNER = "ShadowTag-v2"
REPO_NAME = "Monorepo-Uphillsnowball"


def get_installation_access_token():
    if not os.path.exists(PRIVATE_KEY_PATH):
        sys.exit(1)

    with open(PRIVATE_KEY_PATH) as f:
        private_key = f.read()

    payload = {"iat": int(time.time()) - 60, "exp": int(time.time()) + (10 * 60), "iss": APP_ID}

    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/installation"
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code != 200:
        sys.exit(1)

    installation_id = response.json()["id"]

    token_url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    response = requests.post(token_url, headers=headers, timeout=30)
    if response.status_code != 201:
        sys.exit(1)

    return response.json()["token"]


def main() -> None:
    token = get_installation_access_token()

    remote_url = f"https://x-access-token:{token}@github.com/{REPO_OWNER}/{REPO_NAME}.git"

    # Push commits sequentially
    subprocess.run(["git", "fetch", remote_url, "main"], check=True)

    res = subprocess.run(
        ["git", "log", "FETCH_HEAD..HEAD", "--oneline", "--reverse"],
        capture_output=True,
        text=True,
        check=True,
    )

    output = res.stdout.strip()
    if not output:
        sys.exit(0)

    commits = [line.split()[0] for line in output.split("\n")]

    for _i, commit in enumerate(commits, 1):
        res = subprocess.run(["git", "push", remote_url, f"{commit}:refs/heads/main"])
        if res.returncode != 0:
            sys.exit(1)

    # Finally switch remote origin url to git@ to preserve local setup
    # we won't change origin to avoid messing up other things if not needed


if __name__ == "__main__":
    main()
