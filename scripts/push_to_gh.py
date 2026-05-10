import subprocess
import sys
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

res = requests.get(
  "https://api.github.com/app/installations", headers=headers, timeout=30
)
res.raise_for_status()
installations = res.json()

target_inst = next(
  (i for i in installations if i["account"]["login"] == "ShadowTag-v2"), None
)
if not target_inst:
  sys.exit(1)

inst_id = target_inst["id"]
res2 = requests.post(
  f"https://api.github.com/app/installations/{inst_id}/access_tokens",
  headers=headers,
  timeout=30,
)
res2.raise_for_status()
token = res2.json()["token"]

repo_url = (
  f"https://x-access-token:{token}@github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git"
)
subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=True)

subprocess.run(["git", "push", "origin", "main"], check=True)
