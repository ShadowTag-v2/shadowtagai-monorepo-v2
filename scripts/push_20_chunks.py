#!/usr/bin/env python3
"""
push_20_chunks.py — Chunked Git Push Daemon (Invariant #58)

Breaks large pushes into 25MB partitioned chunks to bypass
GitHub's HTTP 408 server timeout on massive repos.

Flow:
1. Get all commits between remote HEAD and local HEAD
2. Push them in batches of N commits at a time
3. Use omega_sync.py for JWT auth on each batch

Usage:
    python3 scripts/push_20_chunks.py [--batch-size 5] [--target shadowtag]
"""
import argparse
import os
import subprocess
import sys
import time


def get_remote_head(branch: str = "main") -> str:
    """Get the SHA of the remote HEAD for the given branch."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", f"origin/{branch}"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # If remote branch doesn't exist, find the merge-base with any known remote
        result = subprocess.run(
            ["git", "merge-base", "HEAD", "origin/main"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        # Last resort: first commit
        result = subprocess.run(
            ["git", "rev-list", "--max-parents=0", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip().split("\n")[0]


def get_commits_to_push(remote_head: str) -> list[str]:
    """Get list of commit SHAs between remote HEAD and local HEAD."""
    result = subprocess.run(
        ["git", "rev-list", "--reverse", f"{remote_head}..HEAD"],
        capture_output=True, text=True, check=True,
    )
    commits = [c for c in result.stdout.strip().split("\n") if c]
    return commits


def get_pack_size(from_sha: str, to_sha: str) -> int:
    """Estimate the pack size for a range of commits in bytes."""
    result = subprocess.run(
        ["git", "rev-list", "--objects", f"{from_sha}..{to_sha}"],
        capture_output=True, text=True,
    )
    # Rough estimate: count objects * avg object size
    objects = len(result.stdout.strip().split("\n"))
    return objects * 2048  # ~2KB avg per object


def push_chunk(up_to_sha: str, branch: str, target: str = "shadowtag") -> bool:
    """Push up to a specific SHA using omega_sync auth."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    omega_sync = os.path.join(script_dir, "omega_sync.py")

    # First, get the auth token via omega_sync internals
    # We'll import it directly
    sys.path.insert(0, script_dir)
    try:
        import base64

        import omega_sync

        target_config = omega_sync.TARGETS[target]
        jwt_token = omega_sync.generate_jwt(
            target_config["app_id"], target_config["pem_path"]
        )
        installation_id = omega_sync.get_installation_id(
            jwt_token, target_config["org"]
        )
        access_token = omega_sync.get_access_token(jwt_token, installation_id)

        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        b64 = base64.b64encode(
            f"x-access-token:{access_token}".encode()
        ).decode()

        result = subprocess.run(
            [
                "git", "-c", "credential.helper=",
                "-c", f"http.https://github.com/.extraheader=Authorization: Basic {b64}",
                "push", "--thin", "origin",
                f"{up_to_sha}:refs/heads/{branch}",
            ],
            capture_output=True, text=True, env=env, timeout=180,
        )

        if result.returncode == 0:
            return True
        elif "Everything up-to-date" in result.stderr:
            return True
        else:
            print(f"  ❌ Push error: {result.stderr[-200:]}")
            return False

    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Chunked Git Push Daemon")
    parser.add_argument("--batch-size", type=int, default=3,
                        help="Number of commits per chunk (default: 3)")
    parser.add_argument("--target", default="shadowtag",
                        help="Auth target: shadowtag or ehanc69")
    parser.add_argument("--branch", default=None,
                        help="Branch to push (default: current branch)")
    args = parser.parse_args()

    # Get current branch
    if not args.branch:
        args.branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
        ).strip()

    print("═══ CHUNKED PUSH DAEMON ═══")
    print(f"  Branch: {args.branch}")
    print(f"  Batch size: {args.batch_size} commits")
    print(f"  Target: {args.target}")

    # Get commits to push
    remote_head = get_remote_head(args.branch)
    commits = get_commits_to_push(remote_head)

    if not commits:
        print("  ✅ Nothing to push — already up to date.")
        return

    print(f"  📦 {len(commits)} commits to push")

    # Chunk them
    chunks = []
    for i in range(0, len(commits), args.batch_size):
        batch = commits[i:i + args.batch_size]
        chunks.append(batch[-1])  # Push up to the last commit in each batch

    print(f"  🔪 Split into {len(chunks)} chunks")

    # Push each chunk
    for i, sha in enumerate(chunks):
        short_sha = sha[:12]
        print(f"\n  [{i+1}/{len(chunks)}] Pushing up to {short_sha}...")

        success = push_chunk(sha, args.branch, args.target)
        if success:
            print(f"  [{i+1}/{len(chunks)}] ✅ Chunk pushed")
        else:
            print(f"  [{i+1}/{len(chunks)}] ❌ FAILED — retrying in 5s...")
            time.sleep(5)
            success = push_chunk(sha, args.branch, args.target)
            if not success:
                print(f"  ABORT: Chunk {i+1} failed after retry.")
                sys.exit(1)

        # Brief cooldown between chunks
        if i < len(chunks) - 1:
            time.sleep(2)

    print(f"\n═══ CHUNKED PUSH COMPLETE — {len(chunks)} chunks pushed ═══")


if __name__ == "__main__":
    main()
