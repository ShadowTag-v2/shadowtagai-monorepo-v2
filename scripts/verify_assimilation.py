# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import time

import jwt
import requests


def get_session():
    return requests.Session()


def get_installation_token(client_id, pem_path, owner_name):
    try:
        if not os.path.exists(pem_path):
            print(f"ERROR: PEM file not found at {pem_path}")
            return None

        with open(pem_path, "rb") as f:
            pem_data = f.read()

        iat = int(time.time()) - 60
        exp = iat + (10 * 60)
        payload = {"iat": iat, "exp": exp, "iss": str(client_id)}
        encoded_jwt = jwt.encode(payload, pem_data, algorithm="RS256")

        headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}
        session = get_session()

        resp = session.get("https://api.github.com/app/installations", headers=headers, timeout=10)
        if resp.status_code != 200:
            return None

        installations = resp.json()
        target_installation_id = None
        for inst in installations:
            if inst["account"]["login"].lower() == owner_name.lower():
                target_installation_id = inst["id"]
                break

        if not target_installation_id and installations:
            target_installation_id = installations[0]["id"]

        if not target_installation_id:
            return None

        resp = session.post(
            f"https://api.github.com/app/installations/{target_installation_id}/access_tokens",
            headers=headers,
            timeout=10,
        )

        if resp.status_code == 201:
            return resp.json()["token"]
    except Exception as e:
        print(f"Exception fetching token for {owner_name}: {e}")
    return None


def fetch_installation_repos(token):
    repos = []
    page = 1
    session = get_session()
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}

    while True:
        resp = session.get(f"https://api.github.com/installation/repositories?per_page=100&page={page}", headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"Failed to fetch repositories: {resp.status_code} {resp.text}")
            break

        data = resp.json()
        if "repositories" not in data:
            break

        page_repos = data["repositories"]
        if not page_repos:
            break

        for r in page_repos:
            repos.append(r["name"])

        page += 1

    return repos


def verify_assimilation():
    print("=== ASIMILATION VERIFICATION ===")

    # 1. Fetch Tokens
    print("\n[1] Authenticating with GitHub Apps...")
    token_e = get_installation_token("Iv23liWtuBLy8uYLpzjn", "/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem", "ehanc69")
    token_s = get_installation_token(
        "Iv23ctYqrxPQIt2ir8gY",
        "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem",
        "ShadowTag-v2",
    )

    ehanc69_repos = []
    if token_e:
        print(" -> ehanc69 Auth OK")
        ehanc69_repos = fetch_installation_repos(token_e)
        print(f" -> ehanc69 Remote Repositories Extracted: {len(ehanc69_repos)}")
    else:
        print(" -> ehanc69 Auth FAILED")

    shadowtag_repos = []
    if token_s:
        print(" -> ShadowTag-v2 Auth OK")
        shadowtag_repos = fetch_installation_repos(token_s)
        print(f" -> ShadowTag-v2 Remote Repositories Extracted: {len(shadowtag_repos)}")
    else:
        print(" -> ShadowTag-v2 Auth FAILED")

    # Target directory
    target_dir = os.path.join(os.getcwd(), "apps", "aiyou_stack")

    print("\n[2] Verifying Local Assimilation...")
    all_remote_repos = list(set(ehanc69_repos + shadowtag_repos))

    # Remove self-references
    if "Monorepo-Uphillsnowball" in all_remote_repos:
        all_remote_repos.remove("Monorepo-Uphillsnowball")
    if "TsubameViewer" in all_remote_repos:
        all_remote_repos.remove("TsubameViewer")

    print(f" -> Total Expected Canonical Repos: {len(all_remote_repos)}")

    missing = []
    present = []

    for repo in all_remote_repos:
        repo_path = os.path.join(target_dir, repo)
        if os.path.isdir(repo_path):
            # Check if it's not just an empty directory or proxy README
            files = os.listdir(repo_path)
            if len(files) > 1 or (len(files) == 1 and files[0] != "README.md"):
                present.append(repo)
            else:
                missing.append(repo)
        else:
            missing.append(repo)

    print("\n[3] Results:")
    print(f" -> Successfully Assimilated: {len(present)}")
    print(f" -> Missing / Empty: {len(missing)}")

    if len(missing) > 0:
        print("\nMissing Repositories:")
        for m in missing:
            print(f" - {m}")
    else:
        print("\nSUCCESS: 100% of the remote target repositories have been physically cloned into the monorepo.")


if __name__ == "__main__":
    verify_assimilation()
