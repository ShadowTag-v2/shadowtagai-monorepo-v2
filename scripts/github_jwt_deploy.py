#!/usr/bin/env python3
import os
import subprocess
import sys
import time

import jwt
import requests

# User Provided Credentials
APP_ID = "3018200"
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"
REPO_OWNER = "ShadowTag-v2"
REPO_NAME = "Monorepo-Uphillsnowball"


def generate_jwt(app_id, pem_path):
  with open(pem_path) as f:
    signing_key = f.read()

  payload = {
    "iat": int(time.time()),
    "exp": int(time.time()) + (10 * 60),
    "iss": app_id,
  }

  return jwt.encode(payload, signing_key, algorithm="RS256")


def get_installation_id(jwt_token, org_name):
  url = "https://api.github.com/app/installations"
  headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Accept": "application/vnd.github.v3+json",
  }

  response = requests.get(url, headers=headers, timeout=30)
  response.raise_for_status()

  installations = response.json()
  for inst in installations:
    if inst["account"]["login"].lower() == org_name.lower():
      return inst["id"]

  msg = f"Installation not found for organization {org_name}"
  raise Exception(msg)


def get_access_token(jwt_token, installation_id):
  url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
  headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Accept": "application/vnd.github.v3+json",
  }

  response = requests.post(url, headers=headers, timeout=30)
  response.raise_for_status()

  return response.json()["token"]


def push_to_remote(token) -> None:
  remote_url = f"https://x-access-token:{token}@github.com/{REPO_OWNER}/{REPO_NAME}.git"

  # Check current branch
  branch_output = (
    subprocess.check_output(["git", "branch", "--show-current"]).decode().strip()
  )
  if not branch_output:
    branch_output = "HEAD"

  subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)
  push_result = subprocess.run(
    ["git", "push", "--no-verify", "origin", branch_output],
    capture_output=True,
    text=True,
  )

  if push_result.returncode != 0:
    sys.exit(1)


if __name__ == "__main__":
  if not os.path.exists(PEM_PATH):
    sys.exit(1)

  jwt_token = generate_jwt(APP_ID, PEM_PATH)

  try:
    install_id = get_installation_id(jwt_token, REPO_OWNER)
  except Exception:
    sys.exit(1)

  try:
    access_token = get_access_token(jwt_token, install_id)
  except Exception:
    sys.exit(1)

  push_to_remote(access_token)
