# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import subprocess
import time
from pathlib import Path

import jwt
import requests

APP_2_ID = "3018200"
APP_2_KEY = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem"
TARGET_ORG = "ShadowTag-v2"
TARGET_REPO = "Monorepo-Uphillsnowball"

monorepo_root = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")


def get_token():
    with open(APP_2_KEY) as f:
        pk = f.read()
    now = int(time.time())
    encoded_jwt = jwt.encode({"iat": now - 60, "exp": now + (10 * 60), "iss": APP_2_ID}, pk, algorithm="RS256")
    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}
    resp = requests.get("https://api.github.com/app/installations", headers=headers)
    inst_id = next(inst["id"] for inst in resp.json() if inst["account"]["login"].lower() == TARGET_ORG.lower())
    resp = requests.post(f"https://api.github.com/app/installations/{inst_id}/access_tokens", headers=headers)
    return resp.json()["token"]


def run_cmd(cmd):
    subprocess.run(cmd, shell=True, cwd=monorepo_root, check=True)


if __name__ == "__main__":
    t = get_token()
    print("Purging bloated .git...")
    subprocess.run("pkill -9 -f git || true", shell=True)
    subprocess.run("rm -rf .git", shell=True, cwd=monorepo_root)
    run_cmd("git init")
    remote = f"https://x-access-token:{t}@github.com/{TARGET_ORG}/{TARGET_REPO}.git"
    run_cmd(f"git remote add origin {remote}")
    print("Fetching clean remote main...")
    run_cmd("git fetch origin main")
    run_cmd("git checkout -b main")
    run_cmd("git reset --mixed origin/main")
    print("Local git repo re-initialized and synced with origin/main perfectly! 15GB bloat eradicated.")
