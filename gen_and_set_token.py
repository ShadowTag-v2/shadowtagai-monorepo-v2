# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import subprocess
import time

import jwt
import requests

pem_path = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem"
app_id = "3018200"
owner_name = "ShadowTag-v2"

try:
  with open(pem_path, "rb") as f:
    pem_data = f.read()
  iat = int(time.time()) - 60
  exp = iat + (10 * 60)
  payload = {"iat": iat, "exp": exp, "iss": str(app_id)}
  encoded_jwt = jwt.encode(payload, pem_data, algorithm="RS256")
  headers = {
    "Authorization": f"Bearer {encoded_jwt}",
    "Accept": "application/vnd.github.v3+json",
  }
  resp = requests.get("https://api.github.com/app/installations", headers=headers)
  installations = resp.json()
  target_id = None
  for i in installations:
    if i["account"]["login"].lower() == owner_name.lower():
      target_id = i["id"]
      break
  if not target_id:
    target_id = installations[0]["id"]
  resp = requests.post(
    f"https://api.github.com/app/installations/{target_id}/access_tokens",
    headers=headers,
  )
  token = resp.json()["token"]
  subprocess.run(
    f"git remote set-url origin https://x-access-token:{token}@github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git",
    shell=True,
  )
  print("Remote origin strictly bound to new 2026-03-13 PEM key.")
except Exception as e:
  print(f"Failed to set remote token: {e}")
