import json
import subprocess
import time
from pathlib import Path

import jwt
import requests

# The 4 that are already present as canonical roots
existing = {"ShadowTag-v2-fastapi-services", "cosmic-crab-payload", "Pipeline", "nascent-apollo"}


def get_installations(client_id, pem_path):
    with open(pem_path, "rb") as f:
        pem_data = f.read()

    # Generate JWT using Client ID
    iat = int(time.time()) - 60
    exp = iat + (10 * 60)
    payload = {"iat": iat, "exp": exp, "iss": str(client_id)}
    encoded_jwt = jwt.encode(payload, pem_data, algorithm="RS256")

    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}

    resp = requests.get("https://api.github.com/app/installations", headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f"Failed to get installations for {client_id}: {resp.status_code} {resp.text}")
        return None, None

    return resp.json(), headers


def get_access_token(installation_id, headers):
    resp = requests.post(f"https://api.github.com/app/installations/{installation_id}/access_tokens", headers=headers, timeout=30)
    if resp.status_code != 201:
        print(f"Failed to get access token: {resp.status_code} {resp.text}")
        return None
    return resp.json()["token"]


def clone_repo(repo_name, owner, token, target_dir):
    repo_path = target_dir / repo_name
    if repo_path.exists():
        print(f"[{repo_name}] Already exists, skipping clone.")
        return True

    clone_url = f"https://x-access-token:{token}@github.com/{owner}/{repo_name}.git"

    print(f"[{repo_name}] Cloning...")
    # Hide output unless it fails to avoid spam, but hide the token!
    result = subprocess.run(["git", "clone", clone_url, str(repo_path)], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[{repo_name}] ❌ Clone failed.")
        # Don't print the raw stderr because it might contain the token
        return False

    print(f"[{repo_name}] ✅ Cloned successfully.")

    # Remove the .git folder so it becomes part of the monorepo instead of a submodule
    # if it's not one of the existing 4
    if repo_name not in existing:
        subprocess.run(["rm", "-rf", str(repo_path / ".git")])
        print(f"[{repo_name}] 🧹 Stripped .git directory for monorepo ingestion.")

    return True


def process_identity(client_id, pem_path, owner_name, repos_to_clone, target_dir):
    installations, headers = get_installations(client_id, pem_path)
    if not installations:
        return

    target_installation_id = None
    for inst in installations:
        if inst["account"]["login"].lower() == owner_name.lower():
            target_installation_id = inst["id"]
            break

    if not target_installation_id:
        if installations:
            target_installation_id = installations[0]["id"]
        else:
            return

    token = get_access_token(target_installation_id, headers)
    if not token:
        return

    for repo_name in repos_to_clone:
        # We need to test if the repo belongs to this owner
        # If the clone fails, it might belong to the other owner
        clone_repo(repo_name, owner_name, token, target_dir)


if __name__ == "__main__":
    target_dir = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/ShadowTag-v2_stack")
    target_dir.mkdir(parents=True, exist_ok=True)

    with open("fetched_repos_client_id.json") as f:
        all_repos = json.load(f)

    # Filter out the monorepo itself
    all_repos = [r for r in all_repos if r != "Monorepo-Uphillsnowball"]

    # Do we need to clone the 4 existing ones? The prompt says they are already in the manifest but
    # taking a look they might actually be tracked already. We'll skip stripping their .git.

    print(f"Total repos to process: {len(all_repos)}")

    ehanc69_client_id = "Iv23liWtuBLy8uYLpzjn"
    ehanc69_pem = "/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem"

    shadowtag_client_id = "Iv23ctYqrxPQIt2ir8gY"
    shadowtag_pem = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem"

    # Note: Since we don't know which repo belongs to which owner easily from the list,
    # we can try both or use the GitHub API to check.
    # For simplicity, we can fetch the list for each again and map them.

    # ... but actually we can just re-use the logic from fetch_github_repos_client_id.py
    # to know which is which. Let's do that quickly.

    def get_repo_list(client_id, pem_path, owner_name):
        installations, headers = get_installations(client_id, pem_path)
        if not installations:
            return []

        target_installation_id = None
        for inst in installations:
            if inst["account"]["login"].lower() == owner_name.lower():
                target_installation_id = inst["id"]
                break
        if not target_installation_id and installations:
            target_installation_id = installations[0]["id"]

        token = get_access_token(target_installation_id, headers)
        if not token:
            return []

        auth_headers = {
            "Authorization": f"Token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        repos = []
        page = 1
        while True:
            resp = requests.get(f"https://api.github.com/installation/repositories?per_page=100&page={page}", headers=auth_headers, timeout=30)
            if resp.status_code != 200:
                break
            data = resp.json()
            repos.extend(data["repositories"])
            if len(data["repositories"]) < 100:
                break
            page += 1

        return [r["name"] for r in repos], token

    ehanc69_repos, ehanc69_token = get_repo_list(ehanc69_client_id, ehanc69_pem, "ehanc69")
    shadowtag_repos, shadowtag_token = get_repo_list(shadowtag_client_id, shadowtag_pem, "ShadowTag-v2")

    for repo in all_repos:
        if repo in ehanc69_repos:
            clone_repo(repo, "ehanc69", ehanc69_token, target_dir)
        elif repo in shadowtag_repos:
            clone_repo(repo, "ShadowTag-v2", shadowtag_token, target_dir)
        else:
            print(f"[{repo}] ⚠️ Could not determine owner.")

    print("✅ All repositories physically cloned into the monorepo.")
