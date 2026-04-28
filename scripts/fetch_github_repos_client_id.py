# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import contextlib
import json
import time

import jwt
import requests


def get_repos_with_client_id(client_id, pem_path, owner_name):
    with open(pem_path, "rb") as f:
        pem_data = f.read()

    # Generate JWT using Client ID
    iat = int(time.time()) - 60
    exp = iat + (10 * 60)
    payload = {"iat": iat, "exp": exp, "iss": str(client_id)}
    encoded_jwt = jwt.encode(payload, pem_data, algorithm="RS256")

    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}

    # Get installations
    resp = requests.get("https://api.github.com/app/installations", headers=headers, timeout=30)

    if resp.status_code != 200:
        return []

    installations = resp.json()

    target_installation_id = None
    for inst in installations:
        if inst["account"]["login"].lower() == owner_name.lower():
            target_installation_id = inst["id"]
            break

    if not target_installation_id:
        if installations:
            target_installation_id = installations[0]["id"]
        else:
            return []

    # Get installation access token
    resp = requests.post(f"https://api.github.com/app/installations/{target_installation_id}/access_tokens", headers=headers, timeout=30)
    if resp.status_code != 201:
        return []

    token_data = resp.json()
    access_token = token_data["token"]

    # Get repositories
    auth_headers = {
        "Authorization": f"Token {access_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    repos = []
    page = 1
    while True:
        resp = requests.get(f"https://api.github.com/installation/repositories?per_page=100&page={page}", headers=auth_headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        repos.extend(data["repositories"])
        if len(data["repositories"]) < 100:
            break
        page += 1

    return [r["name"] for r in repos]


if __name__ == "__main__":
    repos_ehanc69 = []
    with contextlib.suppress(Exception):
        repos_ehanc69 = get_repos_with_client_id(
            client_id="Iv23liWtuBLy8uYLpzjn",
            pem_path="/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem",
            owner_name="ehanc69",
        )

    repos_shadowtag = []
    with contextlib.suppress(Exception):
        repos_shadowtag = get_repos_with_client_id(
            client_id="Iv23ctYqrxPQIt2ir8gY",
            pem_path="/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem",
            owner_name="ShadowTag-v2",
        )

    all_repos = sorted(set(repos_ehanc69 + repos_shadowtag))
    with open("fetched_repos_client_id.json", "w") as f:
        json.dump(all_repos, f, indent=2)
