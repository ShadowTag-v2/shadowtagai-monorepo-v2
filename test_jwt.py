# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import time

import jwt
import requests

pem_path = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem"
with open(pem_path) as f:
  private_key = f.read()

for iss_val in ["3018200", "Iv23ctYqrxPQIt2ir8gY"]:
  payload = {
    "iat": int(time.time()) - 60,
    "exp": int(time.time()) + 600,
    "iss": iss_val,
  }
  encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
  if isinstance(encoded_jwt, bytes):
    encoded_jwt = encoded_jwt.decode("utf-8")
  headers = {
    "Authorization": f"Bearer {encoded_jwt}",
    "Accept": "application/vnd.github+json",
  }
  resp = requests.get("https://api.github.com/app/installations", headers=headers)
  print(f"ISS: {iss_val} -> {resp.status_code} {resp.text[:100]}")
