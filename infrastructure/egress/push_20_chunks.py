"""SSH egress push script — splits large pushes into 20-ref chunks."""
import subprocess
import sys


def get_local_branches():
    """Get all local branches."""
    result = subprocess.run(
        ["git", "branch", "--format=%(refname:short)"],
        capture_output=True, text=True, check=True,
    )
    return [b.strip() for b in result.stdout.strip().split("\n") if b.strip()]


def push_in_chunks(branches, chunk_size=20):
    """Push branches in chunks to avoid SSH connection limits."""
    for i in range(0, len(branches), chunk_size):
        chunk = branches[i:i + chunk_size]
        refs = [f"{b}:{b}" for b in chunk]
        cmd = ["git", "push", "origin"] + refs
        print(f"Pushing chunk {i // chunk_size + 1}: {len(chunk)} refs")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}", file=sys.stderr)
            return False
    return True


if __name__ == "__main__":
    branches = get_local_branches()
    print(f"Found {len(branches)} branches")
    success = push_in_chunks(branches)
    sys.exit(0 if success else 1)
