import subprocess
import time

import jwt
import requests

APP_ID = "3018200"
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"

with open(PEM_PATH) as f:
    private_key = f.read()

payload = {"iat": int(time.time()), "exp": int(time.time()) + (10 * 60), "iss": APP_ID}
encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}

res = requests.get("https://api.github.com/app/installations", headers=headers, timeout=30)
res.raise_for_status()
installations = res.json()

inst_id = installations[0]["id"]
res2 = requests.post(f"https://api.github.com/app/installations/{inst_id}/access_tokens", headers=headers, timeout=30)
token = res2.json()["token"]

remote_url = f"https://x-access-token:{token}@github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git"
subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)

subprocess.run(["python3", "scripts/finish_changes.py"])
