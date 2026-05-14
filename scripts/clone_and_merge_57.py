# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import jwt
import requests

APP_ID = "3018080"
KEY_PATH = "/Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem"
TARGET_LOGIN = "ehanc69"
TEMP_DIR = Path("/tmp/aiyou_temp")
DST_ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack")
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", ".DS_Store"}


def get_installation_token():
    with open(KEY_PATH) as f:
        private_key = f.read()

    payload = {"iat": int(time.time()), "exp": int(time.time()) + (10 * 60), "iss": APP_ID}
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}

    resp = requests.get("https://api.github.com/app/installations", headers=headers)
    if resp.status_code != 200:
        print(f"Error fetching installations: {resp.text}")
        return None

    installations = resp.json()
    inst_id = next((inst["id"] for inst in installations if inst["account"]["login"].lower() == TARGET_LOGIN.lower()), None)

    if not inst_id:
        print("Installation not found.")
        return None

    url = f"https://api.github.com/app/installations/{inst_id}/access_tokens"
    res = requests.post(url, headers=headers)
    if res.status_code != 201:
        print(f"Error token: {res.text}")
        return None

    return res.json()["token"]


def copy_tree(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for current_root, dirs, files in os.walk(src):
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


def main():
    token = get_installation_token()
    if not token:
        print("Failed to authenticate.")
        sys.exit(1)

    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get("https://api.github.com/installation/repositories?per_page=100", headers=headers)
    repos = res.json().get("repositories", [])

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    DST_ROOT.mkdir(parents=True, exist_ok=True)

    success = 0
    for repo in repos:
        name = repo["name"]
        clone_url = repo["clone_url"].replace("https://", f"https://x-access-token:{token}@")
        clone_path = TEMP_DIR / name

        print(f"Cloning {name}...")
        if clone_path.exists():
            shutil.rmtree(clone_path)

        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, str(clone_path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            dst_path = DST_ROOT / name
            copy_tree(clone_path, dst_path)
            success += 1
            print(f"Merged {name} into {dst_path}")
        except subprocess.CalledProcessError:
            print(f"Failed to clone {name}")
        finally:
            if clone_path.exists():
                shutil.rmtree(clone_path)

    print(f"\nSuccessfully cloned and merged {success} out of {len(repos)} repositories.")


if __name__ == "__main__":
    main()
