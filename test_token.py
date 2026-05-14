# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import time

import jwt
import requests

pem_path = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem"
app_id = "3018200"
with open(pem_path, "rb") as f:
    pem_data = f.read()
iat = int(time.time()) - 60
exp = iat + (10 * 60)
payload = {"iat": iat, "exp": exp, "iss": str(app_id)}
encoded_jwt = jwt.encode(payload, pem_data, algorithm="RS256")
headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}
resp = requests.get("https://api.github.com/app/installations", headers=headers)
print(resp.json())
