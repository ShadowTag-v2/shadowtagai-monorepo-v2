#!/usr/bin/env python3
import json
import time
from pathlib import Path

import jwt
import requests

# Config
APP_ID = "3018080"
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem"
INSTALLATION_USER = "ehanc69"
MONOREPO_ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
INVENTORY_PATH = MONOREPO_ROOT / "docs" / "assimilation_inventory.json"


def get_installation_token():
  with open(PEM_PATH) as f:
    private_key = f.read()

  payload = {"iat": int(time.time()), "exp": int(time.time()) + 600, "iss": APP_ID}
  encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

  headers = {
    "Authorization": f"Bearer {encoded_jwt}",
    "Accept": "application/vnd.github.v3+json",
  }

  resp = requests.get(
    "https://api.github.com/app/installations", headers=headers, timeout=30
  )
  if resp.status_code != 200:
    msg = f"Failed to fetch installations: {resp.text}"
    raise Exception(msg)

  installations = resp.json()
  inst_id = next(
    (
      inst["id"]
      for inst in installations
      if inst["account"]["login"].lower() == INSTALLATION_USER.lower()
    ),
    None,
  )

  if not inst_id:
    msg = f"Installation for {INSTALLATION_USER} not found."
    raise Exception(msg)

  token_resp = requests.post(
    f"https://api.github.com/app/installations/{inst_id}/access_tokens",
    headers=headers,
    timeout=30,
  )
  if token_resp.status_code != 201:
    msg = f"Failed to generate token: {token_resp.text}"
    raise Exception(msg)

  return token_resp.json()["token"]


def generate_inventory(token):
  headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
  }
  res = requests.get(
    "https://api.github.com/installation/repositories?per_page=100",
    headers=headers,
    timeout=30,
  )
  if res.status_code != 200:
    msg = f"Failed to fetch repositories: {res.text}"
    raise Exception(msg)

  repos = res.json().get("repositories", [])

  inventory = []
  for repo in repos:
    name = repo["name"]

    # Verify if it currently exists as a flat copy in apps/ShadowTag-v2_stack
    canonical_path = f"apps/ShadowTag-v2_stack/{name}"
    abs_canonical = MONOREPO_ROOT / canonical_path

    # Determine status
    if abs_canonical.exists() and (abs_canonical / ".git").exists():
      status = "duplicate_live_repo"
    elif abs_canonical.exists():
      status = "flat_copied"
    else:
      status = "absent"

    inventory.append(
      {
        "repo_name": name,
        "source_url": repo["clone_url"],
        "canonical_path": canonical_path,
        "status": status,
        "build_wired": False,
        "ci_wired": False,
      },
    )

  INVENTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
  with open(INVENTORY_PATH, "w") as f:
    json.dump({"repos": inventory}, f, indent=2)

  return inventory


if __name__ == "__main__":
  try:
    tkn = get_installation_token()
    inv = generate_inventory(tkn)
  except Exception:
    pass
