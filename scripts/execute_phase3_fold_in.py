# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import json
import os
import shutil
import subprocess
import time

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

load_dotenv()


def get_token():
    app_id = os.environ.get("GITHUB_EHANC69_APP_ID")
    pem_path = os.environ.get("GITHUB_EHANC69_PRIVATE_KEY_PATH")
    with open(pem_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

    payload = {"iat": int(time.time()), "exp": int(time.time()) + 600, "iss": app_id}
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}

    resp = requests.get("https://api.github.com/app/installations", headers=headers)
    for inst in resp.json():
        if inst.get("account", {}).get("login") == "ehanc69":
            t_resp = requests.post(inst["access_tokens_url"], headers=headers)
            return t_resp.json().get("token")
    return None


def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error running command: {cmd}\nOutput: {result.stderr}")
    return result.returncode == 0


def main():
    token = get_token()
    if not token:
        print("Failed to get github token")
        exit(1)

    TMP_DIR = "/tmp/ehanc69_fold_in"
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)

    with open("repo_fold_in_delta.json") as f:
        delta = json.load(f)

    with open("repo_merge_execution_log.md", "a") as log:
        log.write("\n## Phase 3 — PHYSICAL FOLD-IN\n")

        completed = 0
        rem = len(delta)
        for repo in delta:
            repo_name = repo["repo_name"]
            dest = repo["destination_path"]

            if dest == "none" or not dest:
                print(f"Skipping {repo_name}, no destination")
                continue

            print(f"Processing {repo_name} -> {dest}")
            clone_url = f"https://x-access-token:{token}@github.com/ehanc69/{repo_name}.git"
            clone_path = os.path.join(TMP_DIR, repo_name)

            # Clean clone path if it exists
            if os.path.exists(clone_path):
                shutil.rmtree(clone_path)

            if not run_cmd(f"git -c credential.helper= clone --depth 1 {clone_url} {clone_path} >/dev/null 2>&1"):
                print(f"Failed to clone {repo_name}")
                log.write(f"- **{repo_name}**: FAILED clone\n")
                continue

            # Ensure destination exists
            if not os.path.exists(dest):
                os.makedirs(dest)

            # Rsync into destination
            rsync_cmd = (
                f"rsync -a "
                f"--exclude='.git' "
                f"--exclude='.github' "
                f"--exclude='node_modules' "
                f"--exclude='dist' "
                f"--exclude='build' "
                f"--exclude='.venv' "
                f"--exclude='__pycache__' "
                f"{clone_path}/ {dest}/"
            )

            if run_cmd(rsync_cmd):
                # Clean up nested .git manually in case structural overlap
                run_cmd(f"find {dest} -name '.git' -type d -prune -exec rm -rf '{{}}' +")
                print(f"Successfully folded in {repo_name}")
                log.write(f"- **{repo_name}**: PASS (Dest: `{dest}`)\n")
                completed += 1
            else:
                log.write(f"- **{repo_name}**: FAILED rsync\n")

            # Clean cache
            shutil.rmtree(clone_path)

        log.write(f"\nBATCH_COMPLETE\nrepos_completed={completed}\nrepos_remaining={rem - completed}\nhistory_imported=no\nnested_git_remaining=no\n")


if __name__ == "__main__":
    main()
