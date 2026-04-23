import subprocess
import time
import sys
import os

try:
    import jwt
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyJWT", "requests", "--quiet"])
    import jwt
    import requests

# ==============================================================================
# SOVEREIGN EGRESS: PUSH SKILL TO MONOREPO
# ==============================================================================
APP_ID = "3018200"
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"
REPO = "ShadowTag-v2/Monorepo-Uphillsnowball"
BRANCH = "main"


def get_installation_token():
    print("\n[*] Generating fresh GitHub App JWT for Skill Egress...")
    if not os.path.exists(PEM_PATH):
        print(f"[!] CRITICAL: PEM key missing at {PEM_PATH}")
        sys.exit(1)

    with open(PEM_PATH, "rb") as pem_file:
        signing_key = pem_file.read()

    payload = {"iat": int(time.time()) - 60, "exp": int(time.time()) + (10 * 60), "iss": APP_ID}
    encoded_jwt = jwt.encode(payload, signing_key, algorithm="RS256")
    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}

    # Fetch Installation ID
    resp = requests.get(f"https://api.github.com/repos/{REPO}/installation", headers=headers)
    if resp.status_code != 200:
        print(f"[!] Error fetching installation: {resp.text}")
        sys.exit(1)
    inst_id = resp.json()["id"]

    # Fetch Access Token
    resp = requests.post(f"https://api.github.com/app/installations/{inst_id}/access_tokens", headers=headers)
    if resp.status_code != 201:
        print(f"[!] Error fetching token: {resp.text}")
        sys.exit(1)

    return resp.json()["token"]


def main():
    print("[*] Staging .agents/skills/db-architect-guard/SKILL.md...")
    subprocess.run("git add .agents/skills/db-architect-guard/SKILL.md", shell=True)

    status = subprocess.run("git diff --staged --quiet", shell=True)
    if status.returncode == 0:
        print("[*] No new changes to commit. Skill is already synchronized.")
        sys.exit(0)

    subprocess.run(["git", "commit", "-m", "feat(architecture): Enforce Firestore vs Supabase doctrine via Antigravity Skill"])

    token = get_installation_token()
    safe_url = f"https://x-access-token:{token}@github.com/{REPO}.git"

    print("[*] Executing payload push to master remote...")
    push_result = subprocess.run(["git", "push", safe_url, f"HEAD:refs/heads/{BRANCH}"])

    if push_result.returncode == 0:
        print("\n[SUCCESS] The DB Architect Guard has been fused into the Monorepo.")
    else:
        print("\n[!] Push failed.")


if __name__ == "__main__":
    main()
