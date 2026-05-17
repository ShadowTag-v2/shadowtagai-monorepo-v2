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

# GitHub App Authentication
print("[*] Retrieving GitHub App Token...")
if not os.path.exists(PEM_PATH):
  print(f"[-] Private key not found at {PEM_PATH}")
  exit(1)

with open(PEM_PATH) as f:
  private_key = f.read()

payload = {
  "iat": int(time.time()) - 60,
  "exp": int(time.time()) + (10 * 60),
  "iss": APP_ID,
}
encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
headers = {
  "Authorization": f"Bearer {encoded_jwt}",
  "Accept": "application/vnd.github.v3+json",
}

res = requests.get("https://api.github.com/app/installations", headers=headers)
insts = res.json()
if not insts:
  print("No installations found.")
  exit(1)

inst_id = insts[0]["id"]
res = requests.post(
  f"https://api.github.com/app/installations/{inst_id}/access_tokens", headers=headers
)
token = res.json()["token"]
remote_url = f"https://x-access-token:{token}@github.com/{REPO}.git"

print("[*] Configuring Git Remote...")
subprocess.run(["git", "remote", "remove", "origin"], stderr=subprocess.DEVNULL)
subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)

print("[*] Gathering untracked/modified files...")
res = subprocess.run(
  ["git", "ls-files", "--others", "--exclude-standard", "--cached"],
  capture_output=True,
  text=True,
)
files = res.stdout.splitlines()

# deduplicate while preserving order across cached and untracked combinations
seen = set()
unique_files = []
for f in files:
  if f not in seen and os.path.isfile(f):
    unique_files.append(f)
    seen.add(f)

if not unique_files:
  print("[-] No files to push.")
  exit(0)

# Build Chunks based on 90MB
print("[*] Calculating Chunks based on 90MB threshold...")
MAX_CHUNK_BYTES = 90 * 1024 * 1024
chunks = []
current_chunk = []
current_size = 0

for f in unique_files:
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

print(f"[*] Total Files: {len(unique_files)}.")
print(f"[*] Total 90MB Chunks created: {len(chunks)}.")

BATCH_LIMIT = 1
batches = [chunks[i : i + BATCH_LIMIT] for i in range(0, len(chunks), BATCH_LIMIT)]
print(f"[*] Total Push Batches ({BATCH_LIMIT} chunks per push): {len(batches)}")

chunk_index = 0
for batch_idx, batch in enumerate(batches):
  print("\n==============================")
  print(
    f"🚀 EXECUTING BATCH {batch_idx + 1}/{len(batches)} (Pushing {len(batch)} chunks)"
  )
  print("==============================")

  # Create the local commits
  for inner_chunk in batch:
    chunk_index += 1
    print(
      f" ---> Creating Commit for Chunk {chunk_index}/{len(chunks)} ({len(inner_chunk)} files, approx {sum(os.path.getsize(x) for x in inner_chunk) / (1024 * 1024):.1f} MB)"
    )

    # Adding files in sub-batches if too long for argv
    step = 500
    for i in range(0, len(inner_chunk), step):
      subprocess.run(["git", "add"] + inner_chunk[i : i + step])

    subprocess.run(
      [
        "git",
        "commit",
        "--no-verify",
        "-m",
        f"chore(core): incremental 90MB chunk {chunk_index}",
      ]
    )

  # Push the commits
  print(f"\n [⬆] PUSHING BATCH {batch_idx + 1} TO GITHUB...")
  push_args = ["git", "push", "-u", "origin", "main"]
  if batch_idx == 0:
    push_args.insert(2, "-f")

  res = subprocess.run(push_args)
  if res.returncode != 0:
    print(
      f"\n[!] Push failed on batch {batch_idx + 1}. Aborting so as not to compound local unpushed commits."
    )
    exit(1)

print("\n[+] Incremental 90MB Batch Push Complete! 🚀")
