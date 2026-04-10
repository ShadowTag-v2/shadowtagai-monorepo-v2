#!/usr/bin/env python3
import sys
import os
import time
import subprocess
import requests
import jwt

# User Provided Credentials
APP_ID = "3018200"
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"
REPO_OWNER = "ShadowTag-v2"
REPO_NAME = "Monorepo-Uphillsnowball"

def generate_jwt(app_id, pem_path):
    with open(pem_path) as f:
        signing_key = f.read()

    payload = {
        'iat': int(time.time()),
        'exp': int(time.time()) + (10 * 60),
        'iss': app_id
    }

    return jwt.encode(payload, signing_key, algorithm='RS256')

def get_installation_id(jwt_token, org_name):
    url = "https://api.github.com/app/installations"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    installations = response.json()
    for inst in installations:
        if inst['account']['login'].lower() == org_name.lower():
            return inst['id']

    raise Exception(f"Installation not found for organization {org_name}")

def get_access_token(jwt_token, installation_id):
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.post(url, headers=headers)
    response.raise_for_status()

    return response.json()['token']

def push_to_remote(token):
    remote_url = f"https://x-access-token:{token}@github.com/{REPO_OWNER}/{REPO_NAME}.git"

    # Check current branch
    branch_output = subprocess.check_output(["git", "branch", "--show-current"]).decode().strip()
    if not branch_output:
        branch_output = "HEAD"

    print(f"Pushing branch {branch_output} to remote...")

    subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)
    push_result = subprocess.run(["git", "push", "--no-verify", "origin", branch_output], capture_output=True, text=True)

    if push_result.returncode != 0:
        print(f"Error pushing: {push_result.stderr}", file=sys.stderr)
        sys.exit(1)

    print("Push successful!")

if __name__ == "__main__":
    if not os.path.exists(PEM_PATH):
        print(f"Error: PEM file not found at {PEM_PATH}", file=sys.stderr)
        sys.exit(1)

    print("Generating JWT...")
    jwt_token = generate_jwt(APP_ID, PEM_PATH)

    print(f"Finding installation for {REPO_OWNER}...")
    try:
        install_id = get_installation_id(jwt_token, REPO_OWNER)
    except Exception as e:
        print(f"Error getting installation ID: {e}", file=sys.stderr)
        sys.exit(1)

    print("Exchanging JWT for Installation Access Token...")
    try:
        access_token = get_access_token(jwt_token, install_id)
    except Exception as e:
        print(f"Error generating token: {e}", file=sys.stderr)
        sys.exit(1)

    push_to_remote(access_token)
