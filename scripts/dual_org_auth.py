import os
import time

import jwt
import requests

# ehanc69 Credentials
EHANC69_APP_ID = "3018080"
EHANC69_CLIENT_ID = "Iv23liWtuBLy8uYLpzjn"
EHANC69_KEY_PATH = "/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem"

# ShadowTag-v2 Credentials
SHADOWTAG_APP_ID = "3018200"
SHADOWTAG_CLIENT_ID = "Iv23ctYqrxPQIt2ir8gY"
SHADOWTAG_KEY_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem"


def get_installation_token(app_id, key_path):
    if not os.path.exists(key_path):
        print(f"ERROR: Private key not found at {key_path}")
        return None

    with open(key_path) as f:
        private_key = f.read()

    # Create JWT
    payload = {"iat": int(time.time()), "exp": int(time.time()) + (10 * 60), "iss": app_id}

    try:
        encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    except Exception as e:
        print(f"Error encoding JWT for {app_id}: {e}")
        return None

    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}

    resp = requests.get("https://api.github.com/app/installations", headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f"Error fetching installations for {app_id}: HTTP {resp.status_code}")
        return None

    installations = resp.json()
    if not installations:
        print(f"ERROR: No installations found for App {app_id}.")
        return None

    inst_id = installations[0]["id"]
    url = f"https://api.github.com/app/installations/{inst_id}/access_tokens"
    res = requests.post(url, headers=headers, timeout=30)
    if res.status_code != 201:
        print(f"Error creating access token for {app_id}: HTTP {res.status_code}")
        return None

    return res.json()["token"]


def generate_tokens():
    print("Generating dual-org GitHub App installation tokens...")
    ehanc69_token = get_installation_token(EHANC69_APP_ID, EHANC69_KEY_PATH)
    if ehanc69_token:
        print(f"[✅] Successfully generated ehanc69 short-lived token: {ehanc69_token[:8]}...")

    shadowtag_token = get_installation_token(SHADOWTAG_APP_ID, SHADOWTAG_KEY_PATH)
    if shadowtag_token:
        print(f"[✅] Successfully generated ShadowTag-v2 short-lived token: {shadowtag_token[:8]}...")

    return ehanc69_token, shadowtag_token


if __name__ == "__main__":
    t1, t2 = generate_tokens()
    with open(".github_tokens.json", "w") as f:
        import json

        json.dump({"ehanc69": t1, "ShadowTag-v2": t2}, f)
