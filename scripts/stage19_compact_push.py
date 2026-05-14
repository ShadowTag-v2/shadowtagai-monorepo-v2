#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import subprocess
import time

import jwt
import requests

APP_ID = "3018200"
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"
REPO = "ShadowTag-v2/Monorepo-Uphillsnowball"

print("[*] Retrieving GitHub App Token...")
if not os.path.exists(PEM_PATH):
    print(f"[-] Private key not found at {PEM_PATH}")
    exit(1)

with open(PEM_PATH) as f:
    private_key = f.read()

payload = {"iat": int(time.time()) - 60, "exp": int(time.time()) + (10 * 60), "iss": APP_ID}
encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}
res = requests.get("https://api.github.com/app/installations", headers=headers)
insts = res.json()
if not insts:
    print("No installations found.")
    exit(1)

inst_id = insts[0]["id"]
res = requests.post(f"https://api.github.com/app/installations/{inst_id}/access_tokens", headers=headers)
token = res.json()["token"]
remote_url = f"https://x-access-token:{token}@github.com/{REPO}.git"

print("[*] Reconfiguring and Purging...")
subprocess.run("find . -name '.git' -type d -exec rm -rf {} +", shell=True)  # Destroys root git AND all external repo gits
subprocess.run(["git", "init"], check=True)
subprocess.run(["git", "branch", "-m", "main"], check=True)

print("[*] Staging stateless mega-squash...")
subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m", "chore(core): mega-purge and squashed history reset"], check=True)

print("[*] Force pushing stateless ultra-compact repository...")
res = subprocess.run(["git", "push", "--force", remote_url, "HEAD:refs/heads/main"])

if res.returncode == 0:
    print("[+] Ultra-compact repository push SUCCESS. History obliterated.")
else:
    print("[-] Push failed. Is there a single file exceeding 100MB?")

# Configure safe credentials-free remote
subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{REPO}.git"])
