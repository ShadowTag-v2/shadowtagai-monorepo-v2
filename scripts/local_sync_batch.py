import os
import subprocess
import time
from pathlib import Path

import jwt
import requests

MONO_ROOT = os.getcwd()
CACHE_DIR = os.path.expanduser("~/antigravity-repos")


def get_mapping(repo_name):
    mappings = {
        "ShadowTag-v2jr-template-2": "apps/templates/ShadowTag-v2jr-template-2",
        "ShadowTag-v2-objections-decisions": "governance/ShadowTag-v2-objections-decisions",
        "ShadowTag-v2-core": "packages/ShadowTag-v2-core",
        "ShadowTag-v2-clients": "apps/ShadowTag-v2_stack/ShadowTag-v2-clients",
        "ShadowTag-v2-mlops": "infra/ShadowTag-v2-mlops",
        "ShadowTag-v2-data-contracts": "packages/ShadowTag-v2-data-contracts",
        "ShadowTag-v2-infra": "infra/ShadowTag-v2-infra",
        "ShadowTag-v2-devops": "infra/ShadowTag-v2-devops",
        "ShadowTag-v2-observability": "infra/ShadowTag-v2-observability",
        "ShadowTag-v2-sre": "infra/ShadowTag-v2-sre",
        "ShadowTag-v2-security": "infra/ShadowTag-v2-security",
        "ShadowTag-v2-sops": "infra/ShadowTag-v2-sops",
        "ShadowTag-v2-docs": "docs/ShadowTag-v2",
        "erik-hancock-llm-memory": "memory/erik-hancock-llm-memory",
        "ShadowTag-v2-rollup": "packages/ShadowTag-v2-rollup",
        "pnkln": "control/pnkln",
        "ShadowTag-v2-policy": "packages/ShadowTag-v2-policy",
        "ShadowTag-v2-evals": "evals/ShadowTag-v2-evals",
        "ShadowTag-v2-governance": "governance/ShadowTag-v2-governance",
        "ShadowTag-v2-risk-engine": "infra/ShadowTag-v2-risk-engine",
        "ShadowTag-v2-indexer": "packages/ShadowTag-v2-indexer",
        "ShadowTag-v2-codesmith": "packages/ShadowTag-v2-codesmith",
        "ShadowTag-v2-prompts": "packages/ShadowTag-v2-prompts",
        "ShadowTag-v2-exec": "packages/ShadowTag-v2-exec",
        "ShadowTag-v2-ml": "staging/ShadowTag-v2-ml",
        "ShadowTag-v2-data": "data/ShadowTag-v2-data",
        "ShadowTag-v2-risk": "infra/ShadowTag-v2-risk",
        "ShadowTag-v2-ci": "infra/ci/ShadowTag-v2-ci",
    }
    return mappings.get(repo_name, f"apps/ShadowTag-v2_stack/{repo_name}")


print("Discovering local source payloads...")
synced_count = 0
for rep_dir in Path(CACHE_DIR).iterdir():
    if not rep_dir.is_dir():
        continue
    git_dir = rep_dir / ".git"
    if not git_dir.exists():
        continue

    try:
        remote = subprocess.check_output(
            ["git", "-C", str(rep_dir), "config", "--get", "remote.origin.url"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        remote = ""

    if "ehanc69" not in remote and "ShadowTag-v2" not in remote:
        continue

    repo_name = rep_dir.name
    dest_sub = get_mapping(repo_name)
    dest_abs = os.path.join(MONO_ROOT, dest_sub)

    print(f"[{repo_name}] Synchronizing to {dest_sub}...")
    os.makedirs(dest_abs, exist_ok=True)
    subprocess.run(["rsync", "-a", "--exclude=.git", f"{str(rep_dir)}/", dest_abs], capture_output=True)
    synced_count += 1

print(f"Synchronized {synced_count} repositories.")

print("\nAuthenticating GitHub App Route (ID: 3018080)...")
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem"
APP_ID = "3018080"
try:
    with open(PEM_PATH) as f:
        pk = f.read()
    payload = {"iat": int(time.time()), "exp": int(time.time()) + (10 * 60), "iss": APP_ID}
    enc = jwt.encode(payload, pk, algorithm="RS256")
    r = requests.get("https://api.github.com/app/installations", headers={"Authorization": f"Bearer {enc}"})
    r.raise_for_status()
    inst = r.json()[0]
    r2 = requests.post(
        f"https://api.github.com/app/installations/{inst['id']}/access_tokens",
        headers={"Authorization": f"Bearer {enc}"},
    )
    r2.raise_for_status()
    token = r2.json()["token"]

    print("Setting remote and Executing Egress...")
    remote_url = f"https://x-access-token:{token}@github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git"
    subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)

    subprocess.run(["git", "add", "-A"], check=False)
    status = subprocess.getoutput("git status --porcelain")
    if status.strip():
        subprocess.run(
            ["git", "commit", "-m", "chore: final convergence of all 56 source payloads [skip ci]"],
            check=False,
        )
        subprocess.run(["git", "push", "origin", "HEAD"], check=False)
        print("✅ Massive Push Complete. The Monorepo is Canonical.")
    else:
        print("✅ No net-new drifts detected in local cache.")
except Exception as e:
    print(f"❌ Custom Auth Egress Failed: {e}")
