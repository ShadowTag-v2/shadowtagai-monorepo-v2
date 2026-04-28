#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import subprocess
import sys
import time

import jwt
import requests

APP_ID = "3018200"
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"
REPO = "ShadowTag-v2/Monorepo-Uphillsnowball"
REMOTE_BRANCH = "main"
BATCH_SIZE = 1


def run_cmd(args):
    res = subprocess.run(args, capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(1)
    return res.stdout.strip().splitlines()


# 1. Auth via App Token
if not os.path.exists(PEM_PATH):
    sys.exit(1)

with open(PEM_PATH) as f:
    private_key = f.read()

payload = {"iat": int(time.time()) - 60, "exp": int(time.time()) + (10 * 60), "iss": APP_ID}
encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}

res = requests.get("https://api.github.com/app/installations", headers=headers, timeout=30)
insts = res.json()
if not insts:
    sys.exit(1)

inst_id = insts[0]["id"]
res = requests.post(f"https://api.github.com/app/installations/{inst_id}/access_tokens", headers=headers, timeout=30)
token = res.json()["token"]
remote_url = f"https://x-access-token:{token}@github.com/{REPO}.git"

subprocess.run(["git", "remote", "remove", "origin"], stderr=subprocess.DEVNULL)
subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)

# 2. Get chronological list of all commits
commits = run_cmd(["git", "rev-list", "--reverse", "HEAD"])

if len(commits) == 0:
    sys.exit(0)

# 3. Push in batches
batches = [commits[i : i + BATCH_SIZE] for i in range(0, len(commits), BATCH_SIZE)]

for idx, batch in enumerate(batches):
    target_commit = batch[-1]

    push_args = ["git", "push", "origin", f"{target_commit}:refs/heads/{REMOTE_BRANCH}"]

    # Force push the first batch because it replaces the remote branch completely
    if idx == 0:
        push_args.insert(2, "-f")

    res = subprocess.run(push_args)
    if res.returncode != 0:
        sys.exit(1)


# Finalize the branch push to ensure HEAD is pinned exactly
subprocess.run(["git", "push", "-u", "origin", "HEAD"])
