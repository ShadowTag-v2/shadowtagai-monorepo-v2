import sys
import time

import jwt
import requests


def get_token(client_id, pem_path, owner_name):
    with open(pem_path, "rb") as f:
        pem_data = f.read()

    iat = int(time.time()) - 60
    exp = iat + (10 * 60)
    payload = {"iat": iat, "exp": exp, "iss": str(client_id)}
    encoded_jwt = jwt.encode(payload, pem_data, algorithm="RS256")

    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}
    resp = requests.get("https://api.github.com/app/installations", headers=headers)

    installations = resp.json()
    target_installation_id = None
    for inst in installations:
        if inst["account"]["login"].lower() == owner_name.lower():
            target_installation_id = inst["id"]
            break

    if not target_installation_id:
        return None

    resp = requests.post(f"https://api.github.com/app/installations/{target_installation_id}/access_tokens", headers=headers)
    if resp.status_code == 201:
        return resp.json()["token"]
    return None


if __name__ == "__main__":
    token = get_token("Iv23liWtuBLy8uYLpzjn", "/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem", "ehanc69")
    if not token:
        print("Failed to get token for ehanc69")
        sys.exit(1)

    headers = {
        "Authorization": f"Token {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    url = "https://api.github.com/repos/ehanc69/TsubameViewer"
    print(f"Deleting repository: {url}")

    # Needs delete_repo scope, which the GitHub App must have
    resp = requests.delete(url, headers=headers)

    if resp.status_code == 204:
        print("Successfully deleted ehanc69/TsubameViewer")
    elif resp.status_code == 404:
        print("Repository not found or already deleted.")
    else:
        print(f"Failed to delete repository: {resp.status_code}")
        print(resp.json())
