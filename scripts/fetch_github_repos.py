# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import json
import time

import jwt
import requests


def get_repos(app_id, pem_path, owner_type, owner_name):
    with open(pem_path, "rb") as f:
        pem_data = f.read()

    # Generate JWT
    iat = int(time.time())
    exp = iat + (10 * 60)
    payload = {"iat": iat, "exp": exp, "iss": str(app_id)}
    encoded_jwt = jwt.encode(payload, pem_data, algorithm="RS256")

    # Authenticate as App to get installations
    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}

    resp = requests.get("https://api.github.com/app/installations", headers=headers)
    resp.raise_for_status()
    installations = resp.json()

    target_installation_id = None
    for inst in installations:
        if inst["account"]["login"].lower() == owner_name.lower():
            target_installation_id = inst["id"]
            break

    if not target_installation_id:
        print(f"Could not find installation for {owner_name}")
        return []

    # Get installation access token
    resp = requests.post(f"https://api.github.com/app/installations/{target_installation_id}/access_tokens", headers=headers)
    resp.raise_for_status()
    token_data = resp.json()
    access_token = token_data["token"]

    # Get repositories
    auth_headers = {"Authorization": f"Token {access_token}", "Accept": "application/vnd.github.v3+json"}

    repos = []
    page = 1
    while True:
        resp = requests.get(f"https://api.github.com/installation/repositories?per_page=100&page={page}", headers=auth_headers)
        resp.raise_for_status()
        data = resp.json()
        repos.extend(data["repositories"])
        if len(data["repositories"]) < 100:
            break
        page += 1

    return [r["name"] for r in repos]


if __name__ == "__main__":
    # Try the user ones first
    repos_ehanc69 = []
    try:
        repos_ehanc69 = get_repos(
            app_id="3018080",
            pem_path="/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem",
            owner_type="User",
            owner_name="ehanc69",
        )
    except Exception as e:
        print(f"Failed for ehanc69: {e}")

    repos_shadowtag = []
    try:
        repos_shadowtag = get_repos(
            app_id="3018200",
            pem_path="/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem",
            owner_type="Organization",
            owner_name="ShadowTag-v2",
        )
    except Exception as e:
        print(f"Failed for ShadowTag-v2: {e}")

    all_repos = sorted(list(set(repos_ehanc69 + repos_shadowtag)))
    with open("fetched_repos.json", "w") as f:
        json.dump(all_repos, f, indent=2)

    print(f"Total fetched repos: {len(all_repos)}")
