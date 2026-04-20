#!/usr/bin/env python3

import os
import subprocess
import sys
import time

import jwt
import requests

MAX_MB = 90
MAX_BYTES = MAX_MB * 1024 * 1024


def get_github_token():
    APP_ID = "3018200"
    PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"
    with open(PEM_PATH) as f:
        private_key = f.read()
    payload = {"iat": int(time.time()), "exp": int(time.time()) + (10 * 60), "iss": APP_ID}
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get("https://api.github.com/app/installations", headers=headers, timeout=30)
    res.raise_for_status()
    target_inst = next((i for i in res.json() if i["account"]["login"] == "ShadowTag-v2"), None)
    res2 = requests.post(f"https://api.github.com/app/installations/{target_inst['id']}/access_tokens", headers=headers, timeout=30)
    res2.raise_for_status()
    return res2.json()["token"]


def sync_remote_state(token):
    repo_url = f"https://x-access-token:{token}@github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git"
    try:
        subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)


def get_push_candidate_set():
    # Construct union of tracked modified, staged, and untracked (non-ignored)
    out_staged = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    out_modified = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
    out_untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True)

    files = set()
    for block in [out_staged, out_modified, out_untracked]:
        for f in block.stdout.splitlines():
            if f.strip():
                files.add(f.strip())
    return sorted(list(files))


def chunk_commit_push():
    BATCH = 20
    current_size = 0
    current_files = []

    print("Enumerating intelligent candidate payload...")
    all_files = get_push_candidate_set()
    print(f"Discovered {len(all_files)} trackable files remaining.")

    total_files = len(all_files)
    idx = 0
    for f in all_files:
        idx += 1
        if not os.path.exists(f):
            continue
        size = 0 if os.path.islink(f) else os.path.getsize(f)

        if size > 95 * 1024 * 1024:
            print(f"WARNING: Skipping {f} because it is >95MB and will break pushing.")
            continue

        current_files.append(f)
        current_size += size

        if current_size > MAX_BYTES or idx == total_files:
            if not current_files:
                continue

            print(f"Batch {BATCH}: Adding {len(current_files)} remaining files ({current_size / 1024 / 1024:.2f} MB)...")
            for i in range(0, len(current_files), 1000):
                subprocess.run(["git", "add"] + current_files[i : i + 1000], check=True)

            subprocess.run(
                ["git", "commit", "--no-verify", "-m", f"chore: stateful sync chunk {BATCH}"],
                check=False,
            )

            success = False
            for attempt in range(3):
                ret = subprocess.run(["git", "push", "origin", "main", "--no-verify"])
                if ret.returncode == 0:
                    success = True
                    break
                time.sleep(5)

            if not success:
                sys.exit(1)

            current_files = []
            current_size = 0
            BATCH += 1


if __name__ == "__main__":
    tok = get_github_token()
    sync_remote_state(tok)
    chunk_commit_push()
