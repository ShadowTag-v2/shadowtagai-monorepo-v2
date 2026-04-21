import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import jwt
import requests

APP_1_ID = "3018080"
APP_1_KEY = "/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem"
SOURCE_LOGIN = "ehanc69"

APP_2_ID = "3018200"
APP_2_KEY = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem"
TARGET_ORG = "ShadowTag-v2"
TARGET_REPO = "Monorepo-Uphillsnowball"

TEMP_DIR = Path("/tmp/ShadowTag-v2_temp")
DST_ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/ShadowTag-v2_stack")
EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".DS_Store",
    ".venv",
    "venv",
    ".env",
    "libs/ruff",
    "third_party",
    ".chroma_db",
    ".beads",
    ".lancedb",
}


def run_cmd(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)  # nosec B602 — intentional shell for git/system ops
    if res.returncode != 0 and "Deleted branch" not in res.stderr and "No such remote" not in res.stderr:
        pass
    return res


def get_installation_token(app_id, pem_path, target_account):
    with open(pem_path) as f:
        private_key = f.read()
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + (10 * 60), "iss": app_id}
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}
    resp = requests.get("https://api.github.com/app/installations", headers=headers, timeout=30)
    resp.raise_for_status()
    installations = resp.json()
    inst_id = next(
        (inst["id"] for inst in installations if inst["account"]["login"].lower() == target_account.lower()),
        None,
    )
    if not inst_id:
        sys.exit(1)
    resp = requests.post(f"https://api.github.com/app/installations/{inst_id}/access_tokens", headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()["token"]


def get_repos(token):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    repos = []
    url = "https://api.github.com/installation/repositories?per_page=100"
    while url:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        repos.extend(data.get("repositories", []))
        if "next" in resp.links:
            url = resp.links["next"]["url"]
        else:
            break
    return repos


def append_to_manifest(repo_name, manifest_path) -> None:
    if not manifest_path.exists():
        return
    with open(manifest_path) as f:
        content = f.read()

    # If it is in the YAML as unresolved, replace it inline:
    if f"  - name: {repo_name}\n" in content:
        content = re.sub(
            rf"  - name: {repo_name}\n    status: unresolved\n    canonical_path: null",
            f"  - name: {repo_name}\n    status: canonical\n    canonical_path: apps/ShadowTag-v2_stack/{repo_name}",
            content,
            flags=re.MULTILINE,
        )
        content = re.sub(
            rf"  - name: {repo_name}\n    status: canonical\n    canonical_path: apps/ShadowTag-v2_stack/{repo_name}(.*?)\n    notes: .*?\n",
            f"  - name: {repo_name}\n    status: canonical\n    canonical_path: apps/ShadowTag-v2_stack/{repo_name}\\1\n    notes: Flat copied via squashed assimilation script and uploaded to ShadowTag-v2.\n",
            content,
            flags=re.MULTILINE | re.DOTALL,
        )
        with open(manifest_path, "w") as f:
            f.write(content)
        return

    append_str = f"""
  - name: {repo_name}
    status: canonical
    canonical_path: apps/ShadowTag-v2_stack/{repo_name}
    archived_paths: []
    notes: Flat copied via squashed assimilation script and uploaded to ShadowTag-v2.
"""
    with open(manifest_path, "a") as f:
        f.write(append_str)


def copy_tree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for current_root, dirs, files in os.walk(src):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        rel_root = Path(current_root).relative_to(src)
        target_root = dst / rel_root
        target_root.mkdir(parents=True, exist_ok=True)

        for name in files:
            if name in EXCLUDE_DIRS:
                continue
            s = Path(current_root) / name
            t = target_root / name
            shutil.copy2(s, t)


def main() -> None:
    source_token = get_installation_token(APP_1_ID, APP_1_KEY, SOURCE_LOGIN)

    target_token = get_installation_token(APP_2_ID, APP_2_KEY, TARGET_ORG)

    repos = get_repos(source_token)

    monorepo_root = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
    run_cmd("git add -A", cwd=monorepo_root)
    run_cmd(
        'git commit -m "chore(assimilation): check point before rigorous flat copy loop" || true',
        cwd=monorepo_root,
    )

    # Configure the push remote explicitly via App 2 token
    target_remote_url = f"https://x-access-token:{target_token}@github.com/{TARGET_ORG}/{TARGET_REPO}.git"
    run_cmd("git remote remove origin || true", cwd=monorepo_root)
    run_cmd(f"git remote add origin {target_remote_url}", cwd=monorepo_root)

    # Ensure local main branch tracks remote main
    run_cmd("git branch -M main", cwd=monorepo_root)
    run_cmd("git pull origin main --no-rebase -s recursive -X ours || true", cwd=monorepo_root)

    initial_push = run_cmd("git push -u origin main", cwd=monorepo_root)
    if initial_push.returncode != 0:
        pass
    else:
        pass

    manifest_path = monorepo_root / "monorepo_manifest.yaml"
    success_count = 0
    fail_count = 0

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    DST_ROOT.mkdir(parents=True, exist_ok=True)

    for _i, repo in enumerate(repos):
        repo_name = repo["name"]
        if repo_name == "TsubameViewer":
            continue

        target_dir = f"apps/ShadowTag-v2_stack/{repo_name}"
        target_path = monorepo_root / target_dir

        if target_path.exists():
            append_to_manifest(repo_name, manifest_path)
            continue

        clone_url = repo["clone_url"].replace("https://", f"https://x-access-token:{source_token}@")
        clone_path = TEMP_DIR / repo_name

        if clone_path.exists():
            shutil.rmtree(clone_path)

        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, str(clone_path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            copy_tree(clone_path, target_path)

            append_to_manifest(repo_name, manifest_path)

            run_cmd("git add -A", cwd=monorepo_root)
            run_cmd(f'git commit -m "chore(assimilation): flat copy {repo_name}"', cwd=monorepo_root)
            push_res = run_cmd("git push origin main", cwd=monorepo_root)

            if push_res.returncode == 0:
                success_count += 1
            else:
                run_cmd("git pull origin main --no-rebase -s recursive -X ours", cwd=monorepo_root)
                push_retry = run_cmd("git push origin main", cwd=monorepo_root)
                if push_retry.returncode == 0:
                    success_count += 1
                else:
                    fail_count += 1
        except subprocess.CalledProcessError:
            fail_count += 1
        finally:
            if clone_path.exists():
                shutil.rmtree(clone_path)


if __name__ == "__main__":
    main()
