# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import subprocess
import time

import requests

try:
    import jwt
except ImportError:
    pass

APP_ID = "3018200"
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"

try:
    with open(PEM_PATH) as f:
        private_key = f.read()
    payload = {"iat": int(time.time()), "exp": int(time.time()) + (10 * 60), "iss": APP_ID}
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get("https://api.github.com/app/installations", headers=headers)
    res.raise_for_status()
    installations = res.json()
    inst_id = installations[0]["id"]
    res2 = requests.post(f"https://api.github.com/app/installations/{inst_id}/access_tokens", headers=headers)
    res2.raise_for_status()
    token = res2.json()["token"]
    remote_url = f"https://x-access-token:{token}@github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git"
    subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)
    print("✅ Authenticated GitHub App Native Route Established.")
except Exception as e:
    print(f"❌ Custom Auth Egress Failed: {e}")
