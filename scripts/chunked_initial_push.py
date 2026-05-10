#!/usr/bin/env python3

import os
import subprocess
import sys
import time

import jwt
import requests

# Maximum batch size: 90 MB
MAX_MB = 90
MAX_BYTES = MAX_MB * 1024 * 1024


def clear_heavy_folders() -> None:
  paths_to_clear = {
    "node_modules",
    ".venv",
    "venv",
    ".next",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    "coverage",
    "target",
    ".pnpm",
  }
  for root, dirs, _ in os.walk(".", topdown=False):
    for name in dirs:
      if name in paths_to_clear:
        dpath = os.path.join(root, name)
        subprocess.run(["rm", "-rf", dpath], check=False)


def get_github_token():
  APP_ID = "3018200"
  PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"
  with open(PEM_PATH) as f:
    private_key = f.read()
  payload = {
    "iat": int(time.time()),
    "exp": int(time.time()) + (10 * 60),
    "iss": APP_ID,
  }
  encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
  headers = {
    "Authorization": f"Bearer {encoded_jwt}",
    "Accept": "application/vnd.github.v3+json",
  }
  res = requests.get(
    "https://api.github.com/app/installations", headers=headers, timeout=30
  )
  res.raise_for_status()
  target_inst = next(
    (i for i in res.json() if i["account"]["login"] == "ShadowTag-v2"), None
  )
  if not target_inst:
    sys.exit(1)
  res2 = requests.post(
    f"https://api.github.com/app/installations/{target_inst['id']}/access_tokens",
    headers=headers,
    timeout=30,
  )
  res2.raise_for_status()
  return res2.json()["token"]


def chunk_commit_push(token) -> None:
  subprocess.run(["rm", "-rf", ".git"], check=False)
  subprocess.run(["git", "init"], check=True)
  subprocess.run(["git", "checkout", "-b", "main"], check=True)

  repo_url = f"https://x-access-token:{token}@github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git"
  subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)

  # Initial skeleton to tie history
  with open(".gitignore", "a") as f:
    f.write(
      "\nnode_modules/\n.venv/\nvenv/\n.next/\ndist/\nbuild/\n__pycache__/\ntarget/\n.pnpm/\n*.jar\n*.node\n*.dylib\n*.so\n*.h5\n*.bin\n"
    )

  subprocess.run(["git", "add", ".gitignore"], check=False)
  if os.path.exists("README.md"):
    subprocess.run(["git", "add", "README.md"], check=False)

  subprocess.run(
    ["git", "commit", "-m", "chore: canonical origin initialization"], check=False
  )
  subprocess.run(
    ["git", "push", "origin", "main", "--force", "--no-verify"], check=False
  )

  BATCH = 1
  current_size = 0
  current_files = []

  # get all untracked standard files
  result = subprocess.run(
    ["git", "ls-files", "--others", "--exclude-standard"],
    capture_output=True,
    text=True,
  )
  all_files = [f for f in result.stdout.split("\n") if f]

  total_files = len(all_files)
  idx = 0
  for f in all_files:
    idx += 1
    if not os.path.exists(f):
      continue
    if os.path.islink(f):
      # Treat symlinks as 0 size safely
      size = 0
    else:
      size = os.path.getsize(f)

    # Git LFS / 100MB limit guard:
    if size > 95 * 1024 * 1024:
      continue

    current_files.append(f)
    current_size += size

    if current_size > MAX_BYTES or idx == total_files:
      if not current_files:
        continue

      for i in range(0, len(current_files), 1000):
        cmd = ["git", "add", *current_files[i : i + 1000]]
        subprocess.run(cmd, check=True)

      subprocess.run(
        ["git", "commit", "-m", f"chore: canonical monorepo payload chunk {BATCH}"],
        check=False,
      )

      success = False
      for _attempt in range(3):
        ret = subprocess.run(["git", "push", "origin", "main", "--no-verify"])
        if ret.returncode == 0:
          success = True
          break
        time.sleep(5)

      if not success:
        sys.exit(1)

      current_files = []
      current_size = 0
      BATCH += 1


if __name__ == "__main__":
  clear_heavy_folders()
  tok = get_github_token()
  chunk_commit_push(tok)
