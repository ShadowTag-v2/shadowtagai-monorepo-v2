# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import json
import os
import subprocess
import time


def fetch_repos_with_token(org, token):
  """Fetches repos for an organization using the installation access token"""
  print(f"Fetching repos for {org}...")
  headers = [
    "-H",
    "Accept: application/vnd.github.v3+json",
    "-H",
    f"Authorization: token {token}",
  ]
  url = (
    f"https://api.github.com/users/{org}/repos?per_page=100"
    if org == "ehanc69"
    else f"https://api.github.com/orgs/{org}/repos?per_page=100"
  )

  cmd = ["curl", "-s"] + headers + [url]
  res = subprocess.run(cmd, capture_output=True, text=True)

  if res.returncode != 0:
    print(f"Error fetching repos for {org}")
    return []

  try:
    data = json.loads(res.stdout)
    if isinstance(data, dict) and "message" in data:
      print(f"API Error for {org}: {data['message']}")
      return []
    return [repo["name"] for repo in data]
  except Exception as e:
    print(f"Failed to parse JSON for {org}: {e}")
    return []


def subtree_merge_all():
  if not os.path.exists(".github_tokens.json"):
    print("Missing .github_tokens.json. Run dual_org_auth.py first.")
    return

  with open(".github_tokens.json") as f:
    tokens = json.load(f)

  for org, token in tokens.items():
    if not token:
      print(f"Skipping {org} - no valid token.")
      continue

    repos = fetch_repos_with_token(org, token)
    print(f"Found {len(repos)} repositories in {org}.")

    for repo in repos:
      prefix = f"apps/{org.lower()}/{repo}"
      remote_url = f"https://x-access-token:{token}@github.com/{org}/{repo}.git"

      if os.path.exists(prefix):
        print(f"⏭ Skip: {prefix} already exists in working tree.")
        continue

      print(f"🚀 Adding subtree for {org}/{repo} into {prefix}...")
      # We assume main branch, fallback to master if main fails
      cmd_main = ["git", "subtree", "add", f"--prefix={prefix}", remote_url, "main"]
      res = subprocess.run(cmd_main, capture_output=True, text=True)

      if res.returncode != 0:
        print("    ⚠️ 'main' branch failed, trying 'master'...")
        cmd_master = [
          "git",
          "subtree",
          "add",
          f"--prefix={prefix}",
          remote_url,
          "master",
        ]
        res2 = subprocess.run(cmd_master, capture_output=True, text=True)
        if res2.returncode != 0:
          print(
            f"    ❌ Failed to add subtree {repo}: {res2.stderr.strip().splitlines()[-1] if res2.stderr else 'Unknown error'}"
          )
        else:
          print("    ✅ Success (master branch)")
      else:
        print("    ✅ Success (main branch)")

      time.sleep(0.5)  # small pause to prevent git locking issues


if __name__ == "__main__":
  subtree_merge_all()
