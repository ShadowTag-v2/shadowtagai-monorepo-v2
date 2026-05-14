#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import logging
import os
import subprocess
import sys
from pathlib import Path

import requests
from github import Auth, GithubIntegration

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

APP_ID = "3018080"
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-manager.2026-03-08.private-key.pem"
TARGET_ORG = "ehanc69"
TARGET_DIR = Path("apps/aiyou_stack")


def main():
    if not os.path.exists(PEM_PATH):
        logging.error(f"Cannot find PEM key at {PEM_PATH}")
        sys.exit(1)

    with open(PEM_PATH) as f:
        private_key = f.read()

    # 1. Authenticate as the GitHub App
    logging.info(f"Authenticating App ID {APP_ID} using downloaded PEM key...")
    try:
        app_auth = Auth.AppAuth(app_id=APP_ID, private_key=private_key)
        integration = GithubIntegration(auth=app_auth)
    except Exception as e:
        logging.error(f"Failed to generate GitHub App JWT: {e}")
        sys.exit(1)

    # 2. Find the Installation ID
    inst_id = None
    try:
        installations = integration.get_installations()
        for inst in installations:
            if inst.account.login == TARGET_ORG:
                inst_id = inst.id
                break
    except Exception as e:
        logging.error(f"Failed to fetch installations via API: {e}")
        sys.exit(1)

    if not inst_id:
        logging.error(f"Could not find matching installation ID on account {TARGET_ORG}.")
        sys.exit(1)

    logging.info(f"Found Installation ID: {inst_id} for {TARGET_ORG}")

    # 3. Generate the Installation Token
    try:
        token = integration.get_access_token(
            inst_id,
        ).token
    except Exception as e:
        logging.error(f"Failed to generate Installation Access Token: {e}")
        sys.exit(1)

    # 4. Fetch all repositories matching the installation natively via REST
    logging.info("Scanning for private repositories via raw REST API...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    all_repos = []
    page = 1
    while True:
        resp = requests.get(
            f"https://api.github.com/installation/repositories?per_page=100&page={page}",
            headers=headers,
        )
        if resp.status_code != 200:
            logging.error(f"GitHub API Error: {resp.text}")
            sys.exit(1)

        data = resp.json()
        repos = data.get("repositories", [])
        if not repos:
            break

        all_repos.extend(repos)
        page += 1

    # Filter strictly for private repos
    private_repos = [r for r in all_repos if r.get("private") is True]

    logging.info(f"Discovered {len(private_repos)} Private Repositories linked to the Installation.")

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    successful_clones = 0
    for repo in private_repos:
        repo_name = repo["name"]

        # Inject the GitHub App Token correctly
        clone_url = repo["clone_url"].replace("https://", f"https://x-access-token:{token}@")
        dest_path = TARGET_DIR / repo_name

        if dest_path.exists():
            logging.info(f"Skipping {repo_name} - Directory already exists.")
            continue

        logging.info(f"Cloning {repo_name} (Private HTTPS)...")
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, str(dest_path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            successful_clones += 1

            git_folder = dest_path / ".git"
            if git_folder.exists():
                subprocess.run(["rm", "-rf", str(git_folder)])

        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to clone {repo_name}: {e.stderr.decode('utf-8')}")

    logging.info(f"INGESTION COMPLETE. Successfully pulled {successful_clones} private repositories into {TARGET_DIR}")


if __name__ == "__main__":
    main()
