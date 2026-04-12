#!/usr/bin/env python3
"""
push_20_chunks.py — Chunked Git Push Daemon (Invariant #58)

Breaks large pushes into 25MB partitioned chunks to bypass
GitHub's HTTP 408 server timeout on massive repos.

Key design:
  - Pushes commits in batches of --batch-size (default 5)
  - Stops every --token-window (default 10) chunks to re-issue
    a fresh GitHub App JWT + installation token
  - Uses --force to handle diverged branch histories
  - Each push_chunk call gets a fresh token from the current
    token session (re-issued every token-window chunks)

Usage:
    python3 scripts/push_20_chunks.py [--batch-size 5] [--token-window 10] [--target shadowtag]
"""

import argparse
import base64
import os
import subprocess
import sys
import time


def get_remote_head(branch: str = "main") -> str:
    """Get the SHA of the remote HEAD for the given branch."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", f"origin/{branch}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # If remote branch doesn't exist, find the merge-base with any known remote
        result = subprocess.run(
            ["git", "merge-base", "HEAD", "origin/main"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        # Last resort: first commit
        result = subprocess.run(
            ["git", "rev-list", "--max-parents=0", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip().split("\n")[0]


def get_commits_to_push(remote_head: str) -> list[str]:
    """Get list of commit SHAs between remote HEAD and local HEAD."""
    result = subprocess.run(
        ["git", "rev-list", "--reverse", f"{remote_head}..HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    commits = [c for c in result.stdout.strip().split("\n") if c]
    return commits


def issue_token(target_name: str) -> tuple[str, str]:
    """Issue a fresh GitHub App JWT and exchange for installation access token.

    Returns (access_token, org).
    Only uses the GitHub App — no direct GitHub API access.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    import omega_sync

    target_config = omega_sync.TARGETS[target_name]
    org = target_config["org"]

    print(f"  🔑 Issuing fresh JWT for App ID {target_config['app_id']}...")
    jwt_token = omega_sync.generate_jwt(target_config["app_id"], target_config["pem_path"])

    print(f"  🔍 Finding installation for {org}...")
    installation_id = omega_sync.get_installation_id(jwt_token, org)

    print(f"  🎟️  Exchanging JWT for installation access token...")
    access_token = omega_sync.get_access_token(jwt_token, installation_id)

    print(f"  ✅ Token issued (installation {installation_id})")
    return access_token, org


def push_chunk(up_to_sha: str, branch: str, access_token: str, force: bool = True) -> bool:
    """Push up to a specific SHA using a pre-issued access token.

    Uses --force when force=True to handle diverged histories.
    """
    try:
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        b64 = base64.b64encode(f"x-access-token:{access_token}".encode()).decode()

        cmd = [
            "git",
            "-c", "credential.helper=",
            "-c", f"http.https://github.com/.extraheader=Authorization: Basic {b64}",
            "-c", "http.postBuffer=26214400",  # 25MB
            "-c", "push.negotiate=false",
            "push",
            "--thin",
        ]
        if force:
            cmd.append("--force")
        cmd.extend(["origin", f"{up_to_sha}:refs/heads/{branch}"])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=180,
        )

        if result.returncode == 0:
            return True
        elif "Everything up-to-date" in result.stderr:
            return True
        else:
            print(f"  ❌ Push error: {result.stderr[-300:]}")
            return False

    except subprocess.TimeoutExpired:
        print(f"  ❌ Timeout (180s)")
        return False
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Chunked Git Push Daemon (Invariant #58)")
    parser.add_argument(
        "--batch-size", type=int, default=5,
        help="Number of commits per chunk (default: 5)",
    )
    parser.add_argument(
        "--token-window", type=int, default=10,
        help="Re-issue token after this many chunks (default: 10)",
    )
    parser.add_argument(
        "--target", default="shadowtag",
        help="Auth target: shadowtag or ehanc69",
    )
    parser.add_argument(
        "--branch", default=None,
        help="Branch to push (default: current branch)",
    )
    parser.add_argument(
        "--no-force", action="store_true",
        help="Disable --force (default: force-push enabled for diverged branches)",
    )
    args = parser.parse_args()

    # Get current branch
    if not args.branch:
        args.branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
        ).strip()

    force = not args.no_force

    print("═══ CHUNKED PUSH DAEMON (Invariant #58) ═══")
    print(f"  Branch:       {args.branch}")
    print(f"  Batch size:   {args.batch_size} commits/chunk")
    print(f"  Token window: {args.token_window} chunks before token refresh")
    print(f"  Force push:   {force}")
    print(f"  Target:       {args.target}")

    # Get commits to push
    remote_head = get_remote_head(args.branch)
    commits = get_commits_to_push(remote_head)

    if not commits:
        print("  ✅ Nothing to push — already up to date.")
        return

    print(f"  📦 {len(commits)} commits to push")

    # Build chunks: each chunk is the last SHA in a batch of commits
    chunks = []
    for i in range(0, len(commits), args.batch_size):
        batch = commits[i : i + args.batch_size]
        chunks.append(batch[-1])  # Push up to the last commit in each batch

    print(f"  🔪 Split into {len(chunks)} chunks")

    # Issue initial token
    access_token, org = issue_token(args.target)
    chunks_since_token = 0
    pushed = 0

    for i, sha in enumerate(chunks):
        # Re-issue token every token_window chunks
        if chunks_since_token >= args.token_window:
            print(f"\n  ⏸️  Token window reached ({args.token_window} chunks) — stopping to re-issue...")
            time.sleep(3)
            access_token, org = issue_token(args.target)
            chunks_since_token = 0

        short_sha = sha[:12]
        print(f"\n  [{i + 1}/{len(chunks)}] Pushing up to {short_sha}...")

        success = push_chunk(sha, args.branch, access_token, force=force)
        if success:
            pushed += 1
            chunks_since_token += 1
            print(f"  [{i + 1}/{len(chunks)}] ✅ Chunk pushed ({pushed} total)")
            # After first successful force push, subsequent pushes are fast-forward
            # so we can drop force after the first chunk succeeds
        else:
            print(f"  [{i + 1}/{len(chunks)}] ❌ FAILED — retrying with fresh token in 5s...")
            time.sleep(5)
            access_token, org = issue_token(args.target)
            chunks_since_token = 0
            success = push_chunk(sha, args.branch, access_token, force=force)
            if success:
                pushed += 1
                chunks_since_token += 1
                print(f"  [{i + 1}/{len(chunks)}] ✅ Chunk pushed (retry succeeded)")
            else:
                print(f"  ABORT: Chunk {i + 1} failed after token refresh retry.")
                sys.exit(1)

        # Brief cooldown between chunks
        if i < len(chunks) - 1:
            time.sleep(2)

    print(f"\n═══ CHUNKED PUSH COMPLETE — {pushed}/{len(chunks)} chunks pushed ═══")


if __name__ == "__main__":
    main()
