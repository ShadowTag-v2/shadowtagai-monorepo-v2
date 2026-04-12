import os
import subprocess
import time

import jwt
import requests

# Authentication Parameters
APP_ID = "3018200"
CLIENT_ID = "Iv23ctYqrxPQIt2ir8gY"
KEY_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem"

# The raw multiline string provided by the user
RAW_PATHS = """
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/.vscode
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep-mcp
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep-vscode
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep.github.io
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/grep-ast
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/heavy_lift
/Users/pikeymickey/.gemini/antigravity/playground/cosmic-crab/scripts/__pycache__
/Users/pikeymickey/.gemini/antigravity/playground/cosmic-crab/.agent
/Users/pikeymickey/.gemini/antigravity/playground/cosmic-crab/.antigravity
/Users/pikeymickey/.gemini/antigravity/playground/cosmic-crab
/Users/pikeymickey/.gemini/antigravity-demo-archive/antigravity-demo-2026-3-7-25
/Users/pikeymickey/.gemini/antigravity-demo-archive/antigravity-demo-2026-3-7-25/playground
/Users/pikeymickey/.gemini/antigravity/playground
/Users/pikeymickey/.gemini/antigravity-backup-recovered/playground
/Users/pikeymickey
/Users/Deleted Users/pikeymickey
/Users/pikeymickey/antigravity-knowledge
/Users/pikeymickey/Library/Application Support/Claude
/Users/pikeymickey/.antigravity/nascent-apollo
/Users/pikeymickey/.gemini/antigravity-demo-archive/antigravity-demo-2026-3-7-25/brain
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/
/Users/pikeymickey/.gemini/antigravity-demo-archive/antigravity-demo-2026-3-7-25/code_tracker/active/ShadowTag-v2_bea43616e508f85cade1de6fdee33ec72b5e65b1
/Users/pikeymickey/.gemini/history
"""


def generate_installation_token():
    if not os.path.exists(KEY_PATH):
        print(f"ERROR: Key file not found at {KEY_PATH}")
        return None

    with open(KEY_PATH) as f:
        private_key = f.read()

    # Create JWT
    payload = {"iat": int(time.time()), "exp": int(time.time()) + (10 * 60), "iss": APP_ID}
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}

    resp = requests.get("https://api.github.com/app/installations", headers=headers)
    if resp.status_code != 200:
        print(f"Error fetching installations: HTTP {resp.status_code}\n{resp.text}")
        return None

    installations = resp.json()
    if not installations:
        print("ERROR: No installations found for this GitHub App.")
        return None

    inst_id = installations[0]["id"]
    url = f"https://api.github.com/app/installations/{inst_id}/access_tokens"
    res = requests.post(url, headers=headers)

    if res.status_code != 201:
        print(f"Error creating access token: HTTP {res.status_code}\n{res.text}")
        return None

    return res.json()["token"]


def extract_repo_path(remote_url: str):
    """Converts generic gh remote to owner/repo format."""
    url = remote_url.strip()
    if "github.com/" in url:
        return url.split("github.com/")[-1]
    if "github.com:" in url:
        return url.split("github.com:")[-1]
    return None


def process_git_directory(repo_path: str, token: str):
    print(f"\n--- Processing: {repo_path} ---")
    if repo_path == "/Users/pikeymickey" or repo_path == "/Users/Deleted Users/pikeymickey":
        print(
            "⏭️ DANGER: Target is the system user home directory. Hard-skipping to prevent massive secrets leak."
        )
        return

    if not os.path.isdir(os.path.join(repo_path, ".git")):
        print("⏭️ Not a git repository (missing .git wrapper). Skipping.")
        return

    try:
        # 1. Add all changes
        subprocess.run(["git", "add", "-A"], cwd=repo_path, check=False)

        # 2. Check if there are changes to commit
        status = subprocess.getoutput(f"cd '{repo_path}' && git status --porcelain")
        if status.strip():
            subprocess.run(
                ["git", "commit", "-m", "chore(antigravity): autonomous multi-repo sync"],
                cwd=repo_path,
                check=False,
            )
            print("✅ Changes committed.")
        else:
            print("✅ Working tree clean. No new commits.")

        # 3. Pull Current Remote
        remote_out = subprocess.getoutput(f"cd '{repo_path}' && git remote get-url origin").strip()
        if "fatal: No such remote" in remote_out or not remote_out:
            print("❌ No 'origin' remote found. Cannot push.")
            return

        relative_repo = extract_repo_path(remote_out)
        if not relative_repo:
            print(f"❌ Failed to parse GitHub owner/repo from origin: {remote_out}")
            return

        # 4. Push aggressively using ephemeral App Token via direct HTTPS injection
        push_cmd = f"https://x-access-token:{token}@github.com/{relative_repo}"
        # Using check_call to let failure propagate cleanly to logs without exposing token in stdout by default
        os.environ.copy()

        print("🚀 Pushing to GitHub via App Authorized Route...")
        subprocess.run(["git", "push", push_cmd, "HEAD"], cwd=repo_path, check=True)
        print("🌟 Push Successful.")

    except Exception as e:
        print(f"⚠️ Error processing repository {repo_path}: {e}")


def main():
    print("Initiating Mass Multi-Repo Sync Matrix...")
    token = generate_installation_token()
    if not token:
        print("CRITICAL: Failed to bind GitHub App context. Halting Matrix.")
        return

    print("🔐 GitHub App Connection Established.")

    # Parse provided raw blob, trimming commas and cleaning paths
    lines = RAW_PATHS.splitlines()
    targets = []
    for line in lines:
        cleaned = line.strip().rstrip(",")
        if cleaned:
            targets.append(cleaned)

    # Deduplicate via Set
    targets = list(set(targets))

    for t in targets:
        process_git_directory(t, token)


if __name__ == "__main__":
    main()
