import json
import os
import shutil
import subprocess
import sys
import time

import jwt
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def get_session():
  session = requests.Session()
  # Aggressive backoff for GitHub API timeouts
  retry = Retry(
    connect=5, read=5, backoff_factor=1.0, status_forcelist=[500, 502, 503, 504]
  )
  adapter = HTTPAdapter(max_retries=retry)
  session.mount("https://", adapter)
  return session


def get_token(client_id, pem_path, owner_name):
  try:
    if not os.path.exists(pem_path):
      return None

    with open(pem_path, "rb") as f:
      pem_data = f.read()

    # JWT with Client ID as issuer
    iat = int(time.time()) - 60
    exp = iat + (10 * 60)
    payload = {"iat": iat, "exp": exp, "iss": str(client_id)}
    encoded_jwt = jwt.encode(payload, pem_data, algorithm="RS256")

    headers = {
      "Authorization": f"Bearer {encoded_jwt}",
      "Accept": "application/vnd.github.v3+json",
    }
    session = get_session()

    resp = session.get(
      "https://api.github.com/app/installations", headers=headers, timeout=30
    )
    if resp.status_code != 200:
      return None

    installations = resp.json()
    target_installation_id = None
    for inst in installations:
      if inst["account"]["login"].lower() == owner_name.lower():
        target_installation_id = inst["id"]
        break

    if not target_installation_id and installations:
      target_installation_id = installations[0]["id"]

    if not target_installation_id:
      return None

    resp = session.post(
      f"https://api.github.com/app/installations/{target_installation_id}/access_tokens",
      headers=headers,
      timeout=30,
    )

    if resp.status_code == 201:
      return resp.json()["token"]

  except Exception:
    pass
  return None


if __name__ == "__main__":
  # 1. Fetch Tokens
  token_e = get_token(
    "Iv23liWtuBLy8uYLpzjn",
    "/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem",
    "ehanc69",
  )
  token_s = get_token(
    "Iv23ctYqrxPQIt2ir8gY",
    "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem",
    "ShadowTag-v2",
  )

  if not token_e and not token_s:
    sys.exit(1)

  # 2. Load manifest repos
  json_path = "fetched_repos_client_id.json"
  if not os.path.exists(json_path):
    json_path = "fetched_repos.json"

  with open(json_path) as f:
    repos = json.load(f)

  if "Monorepo-Uphillsnowball" in repos:
    repos.remove("Monorepo-Uphillsnowball")

  cloned_count = 0
  skipped_count = 0

  for repo in repos:
    dest = f"apps/ShadowTag-v2_stack/{repo}"

    # Check if dir exists and isn't just our proxy README
    if os.path.exists(dest):
      files = os.listdir(dest)
      if len(files) > 1 or (len(files) == 1 and files[0] != "README.md"):
        skipped_count += 1
        continue
      else:
        shutil.rmtree(dest)

    success = False

    # Try ehanc69 token first
    if token_e:
      cmd = f"git clone https://x-access-token:{token_e}@github.com/ehanc69/{repo}.git {dest}"
      res = subprocess.run(
        cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
      )  # nosec B602 — intentional shell for git/system ops
      if res.returncode == 0:
        success = True

    # Fallback to ShadowTag-v2 token
    if not success and token_s:
      cmd = f"git clone https://x-access-token:{token_s}@github.com/ShadowTag-v2/{repo}.git {dest}"
      res = subprocess.run(
        cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
      )  # nosec B602 — intentional shell for git/system ops
      if res.returncode == 0:
        success = True

    if success:
      git_dir = os.path.join(dest, ".git")
      if os.path.exists(git_dir):
        shutil.rmtree(git_dir)  # Vaporize .git to merge cleanly into the monorepo
      cloned_count += 1
    else:
      pass

  # 3. Process external Prettier repos
  externals = [
    "https://github.com/prettier/prettier",
    "https://github.com/prettier/prettier-vscode",
    "https://github.com/prettier/eslint-config-prettier",
    "https://github.com/prettier/prettier-eslint",
    "https://github.com/prettier/eslint-plugin-prettier",
    "https://github.com/tailwindlabs/prettier-plugin-tailwindcss",
  ]

  os.makedirs("third_party", exist_ok=True)
  ext_cloned = 0
  for url in externals:
    name = url.split("/")[-1]
    dest = f"third_party/{name}"
    if not os.path.exists(dest):
      cmd = f"git clone {url} {dest}"
      res = subprocess.run(
        cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
      )  # nosec B602 — intentional shell for git/system ops
      if res.returncode == 0:
        git_dir = os.path.join(dest, ".git")
        if os.path.exists(git_dir):
          shutil.rmtree(git_dir)  # Flatten inside our monorepo tree
        ext_cloned += 1
      else:
        pass
    else:
      pass
