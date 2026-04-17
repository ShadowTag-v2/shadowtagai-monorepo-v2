import subprocess
import sys

try:
    import jwt
    import requests
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "PyJWT", "cryptography", "requests"], check=True)
    import jwt
    import requests

import time

pem_path = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem"
app_id = "Iv23ctYqrxPQIt2ir8gY"

with open(pem_path) as f:
    private_key = f.read()

payload = {"iat": int(time.time()) - 60, "exp": int(time.time()) + (10 * 60), "iss": app_id}
encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
if isinstance(encoded_jwt, bytes):
    encoded_jwt = encoded_jwt.decode("utf-8")

headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github+json"}

print("Fetching installation ID...")
resp = requests.get("https://api.github.com/app/installations", headers=headers)
resp.raise_for_status()
data = resp.json()
if not data:
    print("No installations found for this App!")
    sys.exit(1)

install_id = data[0]["id"]
print(f"Installation ID: {install_id}")

print("Fetching access token...")
resp = requests.post(f"https://api.github.com/app/installations/{install_id}/access_tokens", headers=headers)
resp.raise_for_status()
token = resp.json()["token"]

print("Configuring git remote with token...")
cmd = f"git remote set-url origin https://x-access-token:{token}@github.com/ehanc69/Monorepo-Uphillsnowball.git"
subprocess.run(cmd, shell=True, check=True)

print("Calling egress scripts...")
subprocess.run("python3 scripts/finish_changes.py", shell=True)

try:
    subprocess.run("python3 scripts/omega-loopin.py", shell=True, check=True)
except Exception:
    pass

print("GitHub App Sync complete.")
