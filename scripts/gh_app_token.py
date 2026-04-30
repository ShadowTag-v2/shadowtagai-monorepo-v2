import os
import sys
import time
from pathlib import Path

import jwt
import requests

pem_path = os.environ.get("GITHUB_APP_PEM")
app_id = os.environ.get("GITHUB_APP_ID")

if not pem_path or not app_id:
    sys.exit(1)

pem = Path(pem_path).read_bytes()
now = int(time.time())
payload = {"iat": now, "exp": now + (10 * 60), "iss": app_id}

jwt_token = jwt.encode(payload, pem, algorithm="RS256")

# Get installation ID for the repo
headers = {"Authorization": f"Bearer {jwt_token}", "Accept": "application/vnd.github.v3+json"}

resp = requests.get("https://api.github.com/repos/ShadowTag-v2/Monorepo-Uphillsnowball/installation", headers=headers, timeout=30)
if resp.status_code != 200:
    sys.exit(1)

install_id = resp.json()["id"]

# Get access token
resp = requests.post(f"https://api.github.com/app/installations/{install_id}/access_tokens", headers=headers, timeout=30)
if resp.status_code != 201:
    sys.exit(1)
