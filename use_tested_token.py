# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import subprocess
import time

import jwt
import requests

pem_path = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"
app_id = "3018200"
with open(pem_path, "rb") as f:
  pem_data = f.read()
payload = {"iat": int(time.time()) - 60, "exp": int(time.time()) + 600, "iss": app_id}
encoded_jwt = jwt.encode(payload, pem_data, algorithm="RS256")
headers = {
  "Authorization": f"Bearer {encoded_jwt}",
  "Accept": "application/vnd.github.v3+json",
}
installations = requests.get(
  "https://api.github.com/app/installations", headers=headers
).json()
target_id = installations[0]["id"]
token = requests.post(
  f"https://api.github.com/app/installations/{target_id}/access_tokens", headers=headers
).json()["token"]
subprocess.run(
  f"git remote set-url origin https://x-access-token:{token}@github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git",
  shell=True,
)
