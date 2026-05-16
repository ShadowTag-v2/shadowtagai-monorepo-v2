#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import subprocess
import time

import jwt
import requests

APP_ID = "3018200"
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"
REPO = "ShadowTag-v2/Monorepo-Uphillsnowball"

print("[*] Retrieving GitHub App Token...")
if not os.path.exists(PEM_PATH):
    print(f"[-] Private key not found at {PEM_PATH}")
    exit(1)

with open(PEM_PATH) as f:
    private_key = f.read()

payload = {"iat": int(time.time()) - 60, "exp": int(time.time()) + (10 * 60), "iss": APP_ID}
encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}
res = requests.get("https://api.github.com/app/installations", headers=headers)
inst_id = res.json()[0]["id"]
res = requests.post(f"https://api.github.com/app/installations/{inst_id}/access_tokens", headers=headers)
token = res.json()["token"]
remote_url = f"https://x-access-token:{token}@github.com/{REPO}.git"

print("[*] Refreshing Git Init to clear the 3GB root commit...")
subprocess.run(["rm", "-rf", ".git"])
subprocess.run(["git", "init"], check=True)
subprocess.run(["git", "branch", "-m", "main"], check=True)

print("[*] Gathering files...")
res = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True)
files = res.stdout.splitlines()

# Build Chunks based on 90MB
print("[*] Calculating Chunks based on 90MB threshold...")
MAX_CHUNK_BYTES = 90 * 1024 * 1024
chunks = []
current_chunk = []
current_size = 0

for f in files:
    try:
        f_size = os.path.getsize(f)
    except FileNotFoundError:
        continue

    if current_size + f_size > MAX_CHUNK_BYTES and current_chunk:
        chunks.append(current_chunk)
        current_chunk = []
        current_size = 0

    current_chunk.append(f)
    current_size += f_size

if current_chunk:
    chunks.append(current_chunk)

print(f"[*] Total Files: {len(files)}.")
print(f"[*] Total 90MB Chunks created: {len(chunks)}.")

for idx, chunk in enumerate(chunks):
    print("\n==============================")
    print(f"🚀 EXECUTING BATCH {idx + 1}/{len(chunks)} ({len(chunk)} files, approx {sum(os.path.getsize(x) for x in chunk) / (1024 * 1024):.1f} MB)")
    print("==============================")

    # Adding files in sub-batches if too long for argv
    step = 500
    for i in range(0, len(chunk), step):
        subprocess.run(["git", "add"] + chunk[i : i + step])

    subprocess.run(["git", "commit", "--no-verify", "-m", f"chore(core): structural ingestion payload {idx + 1}"])

    push_args = ["git", "push", remote_url, "HEAD:refs/heads/main"]
    if idx == 0:
        push_args.insert(2, "--force")  # Force push the very first root commit to wipe GitHub history

    res = subprocess.run(push_args)
    if res.returncode != 0:
        print(f"\n[!] Push failed on batch {idx + 1}. Aborting.")
        exit(1)

print("\n[+] Hybrid Incremental Stateless Repository Push Complete! 🚀")
subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{REPO}.git"])
