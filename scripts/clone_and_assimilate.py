# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import json
import os
import shutil
import subprocess
import sys
import time

import jwt
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def get_session():
    session = requests.Session()
    # Aggressive backoff for GitHub API timeouts
    retry = Retry(connect=5, read=5, backoff_factor=1.0, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session


def get_token(client_id, pem_path, owner_name):
    print(f"Attempting to fetch installation token for {owner_name} using Client ID {client_id}...")
    try:
        if not os.path.exists(pem_path):
            print(f"ERROR: PEM file not found at {pem_path}")
            return None

        with open(pem_path, "rb") as f:
            pem_data = f.read()

        # JWT with Client ID as issuer
        iat = int(time.time()) - 60
        exp = iat + (10 * 60)
        payload = {"iat": iat, "exp": exp, "iss": str(client_id)}
        encoded_jwt = jwt.encode(payload, pem_data, algorithm="RS256")

        headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}
        session = get_session()

        resp = session.get("https://api.github.com/app/installations", headers=headers, timeout=30)
        if resp.status_code != 200:
            print(f"Failed to get installations for {owner_name}: {resp.status_code} {resp.text}")
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
            print(f"No installation ID found in API response for {owner_name}")
            return None

        print(f"Found installation ID {target_installation_id} for {owner_name}, requesting access token...")
        resp = session.post(
            f"https://api.github.com/app/installations/{target_installation_id}/access_tokens",
            headers=headers,
            timeout=30,
        )

        if resp.status_code == 201:
            print(f"Token acquired for {owner_name}.")
            return resp.json()["token"]
        else:
            print(f"Failed to create access token for {owner_name}: {resp.status_code} {resp.text}")

    except Exception as e:
        print(f"Exception fetching token for {owner_name}: {e}")
    return None


if __name__ == "__main__":
    print("--- GitHub Multi-Repo Assimilator ---")

    # 1. Fetch Tokens
    token_e = get_token("Iv23liWtuBLy8uYLpzjn", "/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem", "ehanc69")
    token_s = get_token(
        "Iv23ctYqrxPQIt2ir8gY",
        "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem",
        "ShadowTag-v2",
    )

    if not token_e and not token_s:
        print("CRITICAL: Failed to acquire any GitHub App tokens. Check network and PEM files.")
        sys.exit(1)

    # 2. Load manifest repos
    json_path = "fetched_repos_client_id.json"
    if not os.path.exists(json_path):
        json_path = "fetched_repos.json"

    print(f"\nLoading {json_path}...")
    with open(json_path) as f:
        repos = json.load(f)

    if "Monorepo-Uphillsnowball" in repos:
        repos.remove("Monorepo-Uphillsnowball")

    print(f"Targeting {len(repos)} internal repositories to clone into canonical roots...")

    cloned_count = 0
    skipped_count = 0

    for repo in repos:
        dest = f"apps/aiyou_stack/{repo}"

        # Check if dir exists and isn't just our proxy README
        if os.path.exists(dest):
            files = os.listdir(dest)
            if len(files) > 1 or (len(files) == 1 and files[0] != "README.md"):
                print(f"Skipping {repo}: appears already populated.")
                skipped_count += 1
                continue
            else:
                shutil.rmtree(dest)

        success = False

        # Try ehanc69 token first
        if token_e:
            cmd = f"git clone https://x-access-token:{token_e}@github.com/ehanc69/{repo}.git {dest}"
            res = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                success = True

        # Fallback to ShadowTag-v2 token
        if not success and token_s:
            cmd = f"git clone https://x-access-token:{token_s}@github.com/ShadowTag-v2/{repo}.git {dest}"
            res = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                success = True

        if success:
            git_dir = os.path.join(dest, ".git")
            if os.path.exists(git_dir):
                shutil.rmtree(git_dir)  # Vaporize .git to merge cleanly into the monorepo
            print(f" [OK] Cloned internal: {repo}")
            cloned_count += 1
        else:
            print(f" [FAILED] Could not clone {repo} using provided tokens.")

    print(f"\nInternal Clone Phase Complete: {cloned_count} cloned, {skipped_count} skipped.")

    # 3. Process external Prettier repos
    print("\n--- Cloning external remote dependencies ---")
    externals = [
        "https://github.com/prettier/prettier",
        "https://github.com/prettier/prettier-vscode",
        "https://github.com/prettier/eslint-config-prettier",
        "https://github.com/prettier/prettier-eslint",
        "https://github.com/prettier/eslint-plugin-prettier",
        "https://github.com/tailwindlabs/prettier-plugin-tailwindcss",
    ]

    os.makedirs("third_party", exist_ok=True)
    ext_cloned = 0
    for url in externals:
        name = url.split("/")[-1]
        dest = f"third_party/{name}"
        if not os.path.exists(dest):
            print(f"Cloning external: {name}...")
            cmd = f"git clone {url} {dest}"
            res = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                git_dir = os.path.join(dest, ".git")
                if os.path.exists(git_dir):
                    shutil.rmtree(git_dir)  # Flatten inside our monorepo tree
                print(f" [OK] Externally pulled: {name}")
                ext_cloned += 1
            else:
                print(f" [FAILED] External: {name}")
        else:
            print(f" [SKIPPED] External {name}: already exists.")

    print(f"\nTotal Run Finished. Internals: {cloned_count}, Externals: {ext_cloned}")
