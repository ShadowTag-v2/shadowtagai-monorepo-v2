# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import subprocess
import sys
import time
from pathlib import Path

import jwt
import requests

APP_ID = "3018080"
KEY_PATH = "/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem"
TARGET_LOGIN = "ehanc69"
TARGET_REPO_TO_DELETE = "ehanc69/TsubameViewer"


def run_cmd(cmd, cwd=None):
  print(f"Running: {cmd}")
  res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
  if res.returncode != 0:
    print(f"Error ({res.returncode}): {res.stderr}")
  return res


def get_installation_token():
  with open(KEY_PATH) as f:
    private_key = f.read()

  now = int(time.time())
  payload = {"iat": now - 60, "exp": now + (10 * 60), "iss": APP_ID}
  encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

  headers = {
    "Authorization": f"Bearer {encoded_jwt}",
    "Accept": "application/vnd.github.v3+json",
  }

  # 1. Find the installation ID for ehanc69
  resp = requests.get("https://api.github.com/app/installations", headers=headers)
  resp.raise_for_status()
  installations = resp.json()

  inst_id = None
  for inst in installations:
    if inst["account"]["login"] == TARGET_LOGIN:
      inst_id = inst["id"]
      break

  if not inst_id:
    print(f"Could not find installation for {TARGET_LOGIN}")
    sys.exit(1)

  # 2. Get access token
  resp = requests.post(
    f"https://api.github.com/app/installations/{inst_id}/access_tokens", headers=headers
  )
  resp.raise_for_status()
  return resp.json()["token"]


def delete_repo(token, full_name):
  print(f"\nAttempting to delete {full_name}...")
  headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28",
  }
  url = f"https://api.github.com/repos/{full_name}"
  resp = requests.delete(url, headers=headers)
  if resp.status_code == 204:
    print(f"Successfully deleted {full_name}")
  elif resp.status_code == 404:
    print(f"{full_name} not found. May already be deleted.")
  else:
    print(f"Failed to delete {full_name}: {resp.status_code} {resp.text}")


def get_repos(token):
  headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
  }
  repos = []
  url = f"https://api.github.com/users/{TARGET_LOGIN}/repos?per_page=100"
  while url:
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    repos.extend(resp.json())
    url = resp.links.get("next", {}).get("url")
  return repos


def main():
  token = get_installation_token()
  print("Successfully authenticated and acquired Installation Access Token.")

  # First, delete TsubameViewer
  delete_repo(token, TARGET_REPO_TO_DELETE)

  # Fetch remaining repos
  repos = get_repos(token)
  print(f"\nFound {len(repos)} repositories under {TARGET_LOGIN}.")

  monorepo_root = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
  target_base = monorepo_root / "apps" / "aiyou_stack"
  target_base.mkdir(parents=True, exist_ok=True)

  manifest_path = monorepo_root / "docs" / "ASSIMILATION_MANIFEST.md"

  # Initialize manifest if it doesn't exist
  if not manifest_path.exists():
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w") as f:
      f.write(
        "# Assimilation Manifest\n\n| Source Repo | Canonical Path | Method | Status |\n|---|---|---|---|\n"
      )

  success_count = 0
  fail_count = 0

  for i, repo in enumerate(repos):
    repo_name = repo["name"]
    print(f"\n[{i + 1}/{len(repos)}] Processing {repo_name}...")

    target_dir = f"apps/aiyou_stack/{repo_name}"
    target_path = monorepo_root / target_dir

    # Skip if directory already exists
    if target_path.exists():
      print(f"Directory {target_dir} already exists. Skipping subtree merge.")
      continue

    default_branch = repo.get("default_branch", "main")
    clone_url = repo["clone_url"]
    auth_url = clone_url.replace("https://", f"https://x-access-token:{token}@")

    # 1. Add remote
    run_cmd(f"git remote add {repo_name} {auth_url}", cwd=monorepo_root)

    try:
      # 2. Fetch remote
      res = run_cmd(f"git fetch {repo_name}", cwd=monorepo_root)
      if res.returncode != 0:
        print(f"Failed to fetch {repo_name}. Skipping subtree add.")
        fail_count += 1
        with open(manifest_path, "a") as f:
          f.write(f"| {clone_url} | {target_dir} | git fetch failed | ERROR |\n")
        continue

      # 3. Subtree add
      res = run_cmd(
        f"git subtree add --prefix={target_dir} {repo_name} {default_branch}",
        cwd=monorepo_root,
      )
      if res.returncode == 0:
        print(f"Successfully subtree merged {repo_name} into {target_dir}")
        success_count += 1
        with open(manifest_path, "a") as f:
          f.write(f"| {clone_url} | {target_dir} | git subtree add | SUCCESS |\n")
      else:
        print(f"Failed to subtree merge {repo_name}. Trying master if main failed.")
        # fall back to master if we assumed main but it was actually master
        if default_branch == "main":
          res = run_cmd(
            f"git subtree add --prefix={target_dir} {repo_name} master",
            cwd=monorepo_root,
          )
          if res.returncode == 0:
            success_count += 1
            with open(manifest_path, "a") as f:
              f.write(
                f"| {clone_url} | {target_dir} | git subtree add (master) | SUCCESS |\n"
              )
          else:
            fail_count += 1
            with open(manifest_path, "a") as f:
              f.write(
                f"| {clone_url} | {target_dir} | git subtree add failed | ERROR |\n"
              )
        else:
          fail_count += 1
          with open(manifest_path, "a") as f:
            f.write(
              f"| {clone_url} | {target_dir} | git subtree add failed | ERROR |\n"
            )
    finally:
      # 4. Remove temporary remote
      run_cmd(f"git remote remove {repo_name}", cwd=monorepo_root)

  print(f"\nAssimilation complete! {success_count} successful, {fail_count} failed.")


if __name__ == "__main__":
  main()
