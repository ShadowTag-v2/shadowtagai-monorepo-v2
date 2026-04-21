import time

import jwt
import requests

APP_ID = "3018200"
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem"
REPO_OWNER = "ShadowTag-v2"
REPO_NAME = "Monorepo-Uphillsnowball"


def generate_jwt(app_id, pem_path):
    from cryptography.hazmat.primitives import serialization

    with open(pem_path, "rb") as pem_file:
        signing_key = serialization.load_pem_private_key(pem_file.read(), password=None)
    payload = {"iat": int(time.time()) - 60, "exp": int(time.time()) + (10 * 60), "iss": app_id}
    return jwt.encode(payload, signing_key, algorithm="RS256")


def get_installation_id(encoded_jwt, owner):
    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}
    url = f"https://api.github.com/orgs/{owner}/installation"
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()["id"]


def get_installation_token(encoded_jwt, installation_id):
    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    response = requests.post(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()["token"]


def set_branch_protection(token, owner, repo, branch) -> None:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}/protection"
    payload = {
        "required_status_checks": {"strict": True, "contexts": ["bazel-build-test"]},
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "required_approving_review_count": 1,
            "require_code_owner_reviews": True,
        },
        "restrictions": None,
    }
    response = requests.put(url, headers=headers, json=payload, timeout=30)
    if response.status_code == 200:
        pass
    else:
        pass


if __name__ == "__main__":
    jwt_token = generate_jwt(APP_ID, PEM_PATH)
    inst_id = get_installation_id(jwt_token, REPO_OWNER)
    token = get_installation_token(jwt_token, inst_id)
    set_branch_protection(token, REPO_OWNER, REPO_NAME, "main")
