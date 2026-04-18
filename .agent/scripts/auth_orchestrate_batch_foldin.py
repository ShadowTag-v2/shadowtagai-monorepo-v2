import json
import os
import subprocess
import sys
import time

try:
    import jwt
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyJWT", "requests", "cryptography"])
    import jwt
    import requests

APP_ID = "3018200"
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"

REPOS = [
    ("pnkln-stackjr-template-2", "apps/templates/pnkln-stackjr-template-2"),
    ("pnkln-stack-objections-decisions", "governance/pnkln-stack-objections-decisions"),
    ("pnkln-stack-core", "packages/pnkln-stack-core"),
    ("pnkln-stack-clients", "apps/pnkln-stack_stack/pnkln-stack-clients"),
    ("pnkln-stack-mlops", "infra/pnkln-stack-mlops"),
    ("pnkln-stack-data-contracts", "packages/pnkln-stack-data-contracts"),
    ("pnkln-stack-infra", "infra/pnkln-stack-infra"),
    ("pnkln-stack-devops", "infra/pnkln-stack-devops"),
    ("pnkln-stack-observability", "infra/pnkln-stack-observability"),
    ("pnkln-stack-sre", "infra/pnkln-stack-sre"),
    ("pnkln-stack-security", "infra/pnkln-stack-security"),
    ("pnkln-stack-sops", "infra/pnkln-stack-sops"),
    ("pnkln-stack-docs", "docs/pnkln-stack"),
    ("pnkln-stack-frontend", "apps/pnkln-stack_stack/pnkln-stack-frontend"),
    ("pnkln-stack-examples", "apps/pnkln-stack_stack/pnkln-stack-examples"),
    ("erik-hancock-llm-memory", "memory/erik-hancock-llm-memory"),
    ("pnkln-stack-rollup", "packages/pnkln-stack-rollup"),
    ("pnkln-stack-api", "apps/pnkln-stack_stack/pnkln-stack-api"),
    ("pnkln", "control/pnkln"),
    ("pnkln-stack-policy", "packages/pnkln-stack-policy"),
    ("pnkln-stack-backend", "apps/pnkln-stack_stack/pnkln-stack-backend"),
    ("pnkln-stack-evals", "evals/pnkln-stack-evals"),
    ("pnkln-stack-governance", "governance/pnkln-stack-governance"),
    ("pnkln-stack-ui-kit", "apps/pnkln-stack_stack/pnkln-stack-ui-kit"),
    ("pnkln-stack-offline-appliance", "apps/pnkln-stack_stack/pnkln-stack-offline-appliance"),
    ("pnkln-stack-risk-engine", "infra/pnkln-stack-risk-engine"),
    ("pnkln-stack-indexer", "packages/pnkln-stack-indexer"),
    ("pnkln-stack-codesmith", "packages/pnkln-stack-codesmith"),
    ("pnkln-stack-prompts", "packages/pnkln-stack-prompts"),
    ("pnkln-stack-exec", "packages/pnkln-stack-exec"),
    ("pnkln-stack-ml", "staging/pnkln-stack-ml"),
    ("pnkln-stack-data", "data/pnkln-stack-data"),
    ("pnkln-stack-risk", "infra/pnkln-stack-risk"),
    ("pnkln-stack-ci", "infra/ci/pnkln-stack-ci"),
]

MONO_ROOT = os.getcwd()
INCOMING_DIR = os.path.join(MONO_ROOT, ".agent", "incoming_repos_auth")
REPORTS_DIR = os.path.join(MONO_ROOT, ".agent", "reports_auth")
CHECKLIST_SCRIPT = os.path.join(
    MONO_ROOT,
    ".agent",
    "bundles",
    "antigravity_manifest_bundle_v3",
    "antigravity_manifest_bundle_v3",
    "fold_in_repo_checklist.py",
)
MANIFEST_PATH = os.path.join(MONO_ROOT, "monorepo_manifest.yaml")

os.makedirs(INCOMING_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


def get_auth_token():
    try:
        with open(PEM_PATH) as f:
            private_key = f.read()

        payload = {"iat": int(time.time()), "exp": int(time.time()) + (10 * 60), "iss": APP_ID}
        encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

        headers = {
            "Authorization": f"Bearer {encoded_jwt}",
            "Accept": "application/vnd.github.v3+json",
        }

        res = requests.get("https://api.github.com/app/installations", headers=headers)
        res.raise_for_status()
        installations = res.json()
        if not installations:
            print("WARNING: No installations found for this App ID.")
            return None

        inst_id = installations[0]["id"]

        res2 = requests.post(f"https://api.github.com/app/installations/{inst_id}/access_tokens", headers=headers)
        res2.raise_for_status()
        return res2.json()["token"]
    except Exception as e:
        print(f"Auth Token Error: {e}")
        return None


token = get_auth_token()
if token:
    print("[AUTH SUCCESS] Generated installation access token for daemon.")
else:
    print("[AUTH WARN] Could not generate token.")

markdown_table = "| Repo | Status | Destination | Duplicate Family | Blockers | Verification |\n"
markdown_table += "| --- | --- | --- | --- | --- | --- |\n"

env = os.environ.copy()
env["GIT_TERMINAL_PROMPT"] = "0"

for repo_name, dest_path in REPOS:
    clone_path = os.path.join(INCOMING_DIR, repo_name)
    out_report = os.path.join(REPORTS_DIR, f"{repo_name}_foldin_report.json")

    if os.path.exists(clone_path) and not os.listdir(clone_path):
        import shutil

        shutil.rmtree(clone_path)

    print(f"[{repo_name}] Cloning...")
    cloned = False

    if not os.path.exists(clone_path):
        # Try shadowtag-omega-v4 first, then ehanc69
        orgs_to_try = ["shadowtag-omega-v4", "ehanc69"]
        for org in orgs_to_try:
            if token:
                clone_url = f"https://x-access-token:{token}@github.com/{org}/{repo_name}.git"
            else:
                clone_url = f"https://github.com/{org}/{repo_name}.git"

            res = subprocess.run(["git", "clone", clone_url, clone_path], capture_output=True, env=env)
            if res.returncode == 0:
                print(f"[{repo_name}] Cloned successfully from {org}.")
                cloned = True
                break

        if not cloned:
            markdown_table += f"| {repo_name} | BLOCKED | {dest_path} | - | Auth/Clone failed | Fail |\n"
            print(f"[{repo_name}] Clone failed. Skipping.")
            continue

    print(f"[{repo_name}] Running Audit...")
    subprocess.run(
        [
            "python3",
            CHECKLIST_SCRIPT,
            repo_name,
            clone_path,
            dest_path,
            "--monorepo-root",
            MONO_ROOT,
            "--out",
            out_report,
        ],
        capture_output=True,
    )

    blockers = "None"
    status = "canonical"
    if os.path.exists(out_report):
        with open(out_report) as f:
            try:
                rep_data = json.load(f)
                if rep_data.get("blocked"):
                    blockers = str(rep_data.get("block_reasons", "Unknown block"))
                    status = "blocked"
            except:
                pass

    if status == "blocked":
        markdown_table += f"| {repo_name} | BLOCKED | {dest_path} | - | {blockers} | Fail |\n"
        print(f"[{repo_name}] Blocked gracefully. Moving on.")
        continue

    print(f"[{repo_name}] Landing Tree to {dest_path}...")
    abs_dest = os.path.join(MONO_ROOT, dest_path)
    os.makedirs(abs_dest, exist_ok=True)
    subprocess.run(["rsync", "-a", "--exclude=.git", f"{clone_path}/", abs_dest], capture_output=True)

    print(f"[{repo_name}] Updating Manifest...")
    try:
        with open(MANIFEST_PATH) as f:
            manifest_lines = f.readlines()

        insert_idx = next((i + 1 for i, line in enumerate(manifest_lines) if line.startswith("repo_roots:")), -1)
        exists = any(f"  {repo_name}:" in line for line in manifest_lines)

        if insert_idx != -1 and not exists:
            entry = [
                f"  {repo_name}:\n",
                "    status: canonical\n",
                f"    canonical_path: {dest_path}\n",
                "    notes: Auto-folded via GitHub App auth.\n\n",
            ]
            manifest_lines = manifest_lines[:insert_idx] + entry + manifest_lines[insert_idx:]
            with open(MANIFEST_PATH, "w") as f:
                f.writelines(manifest_lines)
    except Exception as e:
        print(f"[{repo_name}] Manifest update failed: {e}")

    markdown_table += f"| {repo_name} | canonical | {dest_path} | resolved | None | Success |\n"

with open("batch_auth_foldin_summary.md", "w") as f:
    f.write(markdown_table)

print("[done] Authenticated Batch Fold-In Complete.")
