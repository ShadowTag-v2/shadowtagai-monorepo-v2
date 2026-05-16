# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import json
import time

import jwt
import requests

APP_ID = "3018200"
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"

with open(PEM_PATH) as f:
  private_key = f.read()

payload = {"iat": int(time.time()), "exp": int(time.time()) + (10 * 60), "iss": APP_ID}
encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

headers = {
  "Authorization": f"Bearer {encoded_jwt}",
  "Accept": "application/vnd.github.v3+json",
}

res = requests.get("https://api.github.com/app/installations", headers=headers)
installations = res.json()

if installations:
  inst_id = installations[0]["id"]
  target_account = installations[0]["account"]["login"]
  print(f"App installed on: {target_account}")

  res2 = requests.post(
    f"https://api.github.com/app/installations/{inst_id}/access_tokens", headers=headers
  )
  token = res2.json()["token"]

  headers2 = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
  }

  res3 = requests.get(
    "https://api.github.com/installation/repositories?per_page=100", headers=headers2
  )
  repos = res3.json().get("repositories", [])
  repo_names = [r["full_name"] for r in repos]
  print(json.dumps(repo_names, indent=2))
