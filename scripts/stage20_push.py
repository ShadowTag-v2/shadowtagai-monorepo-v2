#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import subprocess
import time

import jwt
import requests

APP_ID = "3018200"
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"
REPO = "ShadowTag-v2/Monorepo-Uphillsnowball"

with open(PEM_PATH) as f:
    private_key = f.read()

payload = {"iat": int(time.time()) - 60, "exp": int(time.time()) + (10 * 60), "iss": APP_ID}
encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}
res = requests.get("https://api.github.com/app/installations", headers=headers)
inst_id = res.json()[0]["id"]
res = requests.post(f"https://api.github.com/app/installations/{inst_id}/access_tokens", headers=headers)
token = res.json()["token"]
remote_url = f"https://x-access-token:{token}@github.com/{REPO}.git"

print("[*] Staging and committing the final untracked residual files...")
subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m", "chore(core): structural ingestion residual synchronization"], check=False)

print("[*] Pushing to remote...")
res = subprocess.run(["git", "push", remote_url, "HEAD:refs/heads/main"])
if res.returncode == 0:
    print("[+] Residual Push Success!")
else:
    print("[-] Push Failure!")
