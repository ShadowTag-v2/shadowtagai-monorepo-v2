# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import subprocess
import sys
import time

import requests

TARGET_DIR = "third_party/ehanc69_repos"
GITHUB_USER = "ehanc69"

os.makedirs(TARGET_DIR, exist_ok=True)

print(f"Fetching repositories for user: {GITHUB_USER}")
repos = []
page = 1
while True:
    print(f"Fetching page {page}...")
    try:
        response = requests.get(f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100&page={page}")
        response.raise_for_status()
        page_repos = response.json()
        if not page_repos:
            break
        repos.extend(page_repos)
        page += 1
    except Exception as e:
        print(f"Error fetching repos: {e}")
        sys.exit(1)

print(f"Found {len(repos)} repositories to ingest into {TARGET_DIR}")

for repo in repos:
    repo_name = repo["name"]
    clone_url = repo["clone_url"]
    repo_path = os.path.join(TARGET_DIR, repo_name)

    if os.path.exists(repo_path):
        print(f"Repo {repo_name} already exists. Pulling latest...")
        subprocess.run(
            ["git", "-C", repo_path, "pull", "origin", repo["default_branch"]],
            check=False,
        )
    else:
        print(f"Cloning {repo_name}...")
        subprocess.run(["git", "clone", clone_url, repo_path], check=False)

    # Optional: sleep slightly to prevent hammering GitHub if rate limits are a concern
    time.sleep(0.5)

print("\nIngestion complete.")
print("NOTE: We expect these directories to be explicitly ignored by the root git configuration so they don't break our git logs.")
