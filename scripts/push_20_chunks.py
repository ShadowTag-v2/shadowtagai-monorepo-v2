#!/usr/bin/env python3
"""
push_20_chunks.py — Chunked Git Push Daemon (Invariant #58)

Breaks large pushes into partitioned chunks to bypass
GitHub's HTTP 408 server timeout on massive repos.

Key design:
  - Pushes commits in batches of --batch-size (default 5)
  - When a batch times out, splits it into single-commit pushes
  - Stops every --token-window (default 10) chunks to re-issue
    a fresh GitHub App JWT + installation token
  - Uses --force to handle diverged branch histories

Usage:
    python3 scripts/push_20_chunks.py [--batch-size 5] [--token-window 10] [--resume-from 13]
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

    print("  🎟️  Exchanging JWT for installation access token...")
    access_token = omega_sync.get_access_token(jwt_token, installation_id)

    print(f"  ✅ Token issued (installation {installation_id})")
    return access_token, org


def push_chunk(
    up_to_sha: str,
    branch: str,
    access_token: str,
    force: bool = True,
    timeout: int = 300,
    post_buffer: int = 26214400,
) -> bool:
    """Push up to a specific SHA using a pre-issued access token.

    Uses --force when force=True to handle diverged histories.
    """
    try:
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        b64 = base64.b64encode(f"x-access-token:{access_token}".encode()).decode()

        cmd = [
            "git",
            "-c",
            "credential.helper=",
            "-c",
            f"http.https://github.com/.extraheader=Authorization: Basic {b64}",
            "-c",
            f"http.postBuffer={post_buffer}",
            "-c",
            "push.negotiate=false",
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
            timeout=timeout,
        )

        if result.returncode == 0:
            return True
        elif "Everything up-to-date" in result.stderr:
            return True
        else:
            print(f"  ❌ Push error: {result.stderr[-300:]}")
            return False

    except subprocess.TimeoutExpired:
        print(f"  ❌ Timeout ({timeout}s)")
        return False
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False


def push_commits_individually(
    commits: list[str],
    branch: str,
    access_token: str,
    force: bool,
    token_issuer,
    target: str,
) -> tuple[bool, str, int]:
    """Push a list of commits one at a time (escalation mode).

    Returns (success, current_token, total_pushed).
    """
    pushed = 0
    current_token = access_token

    for j, sha in enumerate(commits):
        short = sha[:12]
        print(f"    ↳ Sub-commit [{j + 1}/{len(commits)}] {short}...")

        # Try with 300s timeout and 50MB buffer for single commits
        ok = push_chunk(sha, branch, current_token, force=force, timeout=300, post_buffer=52428800)
        if ok:
            pushed += 1
            print(f"    ↳ [{j + 1}/{len(commits)}] ✅ individual commit pushed")
        else:
            # Last resort: fresh token + 600s timeout
            print(f"    ↳ [{j + 1}/{len(commits)}] ⚠️ failed — escalating (fresh token + 600s)...")
            time.sleep(5)
            current_token, _ = token_issuer(target)
            ok = push_chunk(sha, branch, current_token, force=force, timeout=600, post_buffer=52428800)
            if ok:
                pushed += 1
                print(f"    ↳ [{j + 1}/{len(commits)}] ✅ pushed (escalation succeeded)")
            else:
                print(f"    ↳ [{j + 1}/{len(commits)}] ❌ FATAL: commit {short} cannot be pushed.")
                return False, current_token, pushed

        time.sleep(1)  # Brief cooldown

    return True, current_token, pushed


def main():
    parser = argparse.ArgumentParser(description="Chunked Git Push Daemon (Invariant #58)")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Number of commits per chunk (default: 5)",
    )
    parser.add_argument(
        "--token-window",
        type=int,
        default=10,
        help="Re-issue token after this many chunks (default: 10)",
    )
    parser.add_argument(
        "--target",
        default="shadowtag",
        help="Auth target: shadowtag or ehanc69",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Branch to push (default: current branch)",
    )
    parser.add_argument(
        "--no-force",
        action="store_true",
        help="Disable --force (default: force-push enabled for diverged branches)",
    )
    parser.add_argument(
        "--resume-from",
        type=int,
        default=1,
        help="Resume from chunk N (1-indexed, default: 1)",
    )
    args = parser.parse_args()

    # Get current branch
    if not args.branch:
        args.branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
        ).strip()

    force = not args.no_force

    print("═══ CHUNKED PUSH DAEMON v2 (Invariant #58) ═══")
    print(f"  Branch:       {args.branch}")
    print(f"  Batch size:   {args.batch_size} commits/chunk")
    print(f"  Token window: {args.token_window} chunks before token refresh")
    print(f"  Force push:   {force}")
    print(f"  Resume from:  chunk {args.resume_from}")
    print(f"  Target:       {args.target}")

    # Get commits to push
    remote_head = get_remote_head(args.branch)
    commits = get_commits_to_push(remote_head)

    if not commits:
        print("  ✅ Nothing to push — already up to date.")
        return

    print(f"  📦 {len(commits)} commits to push")

    # Build chunks: each chunk is a list of commit SHAs
    chunk_groups = []
    for i in range(0, len(commits), args.batch_size):
        batch = commits[i : i + args.batch_size]
        chunk_groups.append(batch)

    total_chunks = len(chunk_groups)
    print(f"  🔪 Split into {total_chunks} chunks")

    # Issue initial token
    access_token, org = issue_token(args.target)
    chunks_since_token = 0
    pushed = 0
    skipped = 0

    for i, chunk_commits in enumerate(chunk_groups):
        chunk_num = i + 1  # 1-indexed for display

        # Skip already-pushed chunks
        if chunk_num < args.resume_from:
            skipped += 1
            print(f"\n  [{chunk_num}/{total_chunks}] ⏭️  Skipped (resume-from={args.resume_from})")
            continue

        # Re-issue token every token_window chunks
        if chunks_since_token >= args.token_window:
            print(f"\n  ⏸️  Token window reached ({args.token_window} chunks) — re-issuing...")
            time.sleep(3)
            access_token, org = issue_token(args.target)
            chunks_since_token = 0

        target_sha = chunk_commits[-1]
        short_sha = target_sha[:12]
        print(f"\n  [{chunk_num}/{total_chunks}] Pushing {len(chunk_commits)} commits up to {short_sha}...")

        # Try the batch push
        success = push_chunk(target_sha, args.branch, access_token, force=force, timeout=300)
        if success:
            pushed += 1
            chunks_since_token += 1
            print(f"  [{chunk_num}/{total_chunks}] ✅ Batch pushed ({pushed} chunks done)")
        else:
            # === ADAPTIVE SPLIT: push commits individually ===
            print(f"  [{chunk_num}/{total_chunks}] ⚠️ Batch failed — splitting into {len(chunk_commits)} individual commits...")
            time.sleep(3)
            access_token, org = issue_token(args.target)
            chunks_since_token = 0

            ok, access_token, sub_pushed = push_commits_individually(
                chunk_commits,
                args.branch,
                access_token,
                force,
                issue_token,
                args.target,
            )
            if ok:
                pushed += 1
                chunks_since_token += 1
                print(f"  [{chunk_num}/{total_chunks}] ✅ All {sub_pushed} sub-commits pushed (adaptive split)")
            else:
                print(f"  ABORT: Chunk {chunk_num} failed even with individual commits.")
                print(f"  💡 Hint: resume later with --resume-from {chunk_num}")
                sys.exit(1)

        # Brief cooldown between chunks
        if i < len(chunk_groups) - 1:
            time.sleep(2)

    print("\n═══ CHUNKED PUSH COMPLETE ═══")
    print(f"  Chunks: {pushed} pushed, {skipped} skipped / {total_chunks} total")
    print(f"  Branch: {args.branch}")


if __name__ == "__main__":
    main()
