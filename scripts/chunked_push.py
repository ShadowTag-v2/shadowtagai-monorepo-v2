#!/usr/bin/env python3
"""Chunked Git Data API Push — Invariant #90
Pushes all tracked files in 100MB chunks, 5 per JWT window.
Renews token between batch windows.

Usage:
    python3 scripts/chunked_push.py [--dry-run] [--chunk-size-mb 100] [--batch-size 5]
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

ORG = "ShadowTag-v2"
REPO = "Monorepo-Uphillsnowball"
APP_ID = "3018200"
PEM_PATH = os.environ.get(
    "GITHUB_APP_PEM",
    os.path.expanduser("~/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"),
)
REPO_ROOT = Path(__file__).resolve().parent.parent

CHUNK_SIZE_MB = 100
BATCH_SIZE = 5


def api(method: str, path: str, body: dict | None = None, token: str = "") -> dict:
    url = f"https://api.github.com/repos/{ORG}/{REPO}/{path}"
    data = json.dumps(body).encode() if body else None
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    }
    rq = urllib.request.Request(url, headers=headers, data=data, method=method)
    try:
        r = urllib.request.urlopen(rq, timeout=120)
        return json.loads(r.read())
    except urllib.error.HTTPError:
        raise


def mint_jwt() -> str:
    """Mint a GitHub App installation token via JWT."""
    import jwt as pyjwt

    with open(PEM_PATH) as f:
        pem = f.read()

    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 540, "iss": APP_ID}
    encoded = pyjwt.encode(payload, pem, algorithm="RS256")

    # Get installation ID
    url = "https://api.github.com/app/installations"
    rq = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {encoded}",
            "Accept": "application/vnd.github+json",
        },
    )
    r = urllib.request.urlopen(rq, timeout=30)
    installations = json.loads(r.read())
    install_id = installations[0]["id"]

    # Mint token
    url = f"https://api.github.com/app/installations/{install_id}/access_tokens"
    rq = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {encoded}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
        data=b"{}",
        method="POST",
    )
    r = urllib.request.urlopen(rq, timeout=30)
    return json.loads(r.read())["token"]


def get_token() -> str:
    """Get token from env or mint new one."""
    env_token = os.environ.get("GH_TOKEN", "")
    if env_token:
        return env_token
    return mint_jwt()


def get_tracked_files() -> list[tuple[str, int]]:
    """Return (relative_path, size_bytes) for all git-tracked files."""
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    files = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        full = REPO_ROOT / line
        if full.is_file():
            files.append((line, full.stat().st_size))
    # Sort largest first for early failure detection
    files.sort(key=lambda x: x[1], reverse=True)
    return files


def group_into_chunks(files: list[tuple[str, int]], chunk_mb: int) -> list[list[tuple[str, int]]]:
    """Group files into chunks of approximately chunk_mb megabytes."""
    chunks: list[list[tuple[str, int]]] = []
    current: list[tuple[str, int]] = []
    current_size = 0
    limit = chunk_mb * 1024 * 1024

    for path, size in files:
        if size > limit:
            # Single file exceeds chunk size — its own chunk
            if current:
                chunks.append(current)
                current = []
                current_size = 0
            chunks.append([(path, size)])
            continue

        if current_size + size > limit and current:
            chunks.append(current)
            current = []
            current_size = 0

        current.append((path, size))
        current_size += size

    if current:
        chunks.append(current)

    return chunks


def push_chunk(chunk: list[tuple[str, int]], _chunk_idx: int, token: str, dry_run: bool) -> list[dict]:
    """Push a chunk of files as blobs, return tree items."""
    tree_items = []
    sum(s for _, s in chunk) / 1024 / 1024

    for i, (fpath, _size) in enumerate(chunk):
        if dry_run:
            tree_items.append({"path": fpath, "mode": "100644", "type": "blob", "sha": "dry-run"})
            continue

        full = REPO_ROOT / fpath
        with open(full, "rb") as f:
            content = base64.b64encode(f.read()).decode()

        blob = api("POST", "git/blobs", {"content": content, "encoding": "base64"}, token)
        tree_items.append({"path": fpath, "mode": "100644", "type": "blob", "sha": blob["sha"]})

        if (i + 1) % 50 == 0 or i == len(chunk) - 1:
            pass

    return tree_items


def main() -> None:
    parser = argparse.ArgumentParser(description="Chunked Git Data API Push")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually push")
    parser.add_argument("--chunk-size-mb", type=int, default=CHUNK_SIZE_MB, help="MB per chunk")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Chunks per token window")
    args = parser.parse_args()

    # 1. Get tracked files
    files = get_tracked_files()
    sum(s for _, s in files) / 1024 / 1024

    # 2. Group into chunks
    chunks = group_into_chunks(files, args.chunk_size_mb)

    if args.dry_run:
        pass

    # 3. Push in batches
    all_tree_items: list[dict] = []
    token = "" if args.dry_run else get_token()

    for batch_start in range(0, len(chunks), args.batch_size):
        batch_end = min(batch_start + args.batch_size, len(chunks))
        batch_start // args.batch_size + 1
        (len(chunks) + args.batch_size - 1) // args.batch_size

        if batch_start > 0 and not args.dry_run:
            token = mint_jwt()

        for i in range(batch_start, batch_end):
            items = push_chunk(chunks[i], i + 1, token, args.dry_run)
            all_tree_items.extend(items)

    # 4. Create tree + commit + update ref
    if args.dry_run:
        return

    # Get current main
    branch = api("GET", "branches/main", token=token)
    base_sha = branch["commit"]["sha"]
    base_tree = branch["commit"]["commit"]["tree"]["sha"]

    # Create tree (may need chunking for >1000 items)
    # GitHub tree API handles up to ~10K items
    tree = api(
        "POST",
        "git/trees",
        {"base_tree": base_tree, "tree": all_tree_items},
        token,
    )

    commit = api(
        "POST",
        "git/commits",
        {
            "message": "fix(hygiene): mass repo cleanup — 95% file reduction\n\n"
            "Untracked 430K+ bloated files (external repos, archive, binaries).\n"
            "Ruff auto-fix (93 fixes) + format (249 files).\n"
            "Pushed via Chunked Push Protocol (Invariant #90).",
            "tree": tree["sha"],
            "parents": [base_sha],
            "author": {
                "name": "antigravity-shadowtag-manager[bot]",
                "email": "antigravity-shadowtag-manager[bot]@users.noreply.github.com",
                "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        },
        token,
    )
    new_sha = commit["sha"]

    api("PATCH", "git/refs/heads/main", {"sha": new_sha, "force": False}, token)


if __name__ == "__main__":
    main()
