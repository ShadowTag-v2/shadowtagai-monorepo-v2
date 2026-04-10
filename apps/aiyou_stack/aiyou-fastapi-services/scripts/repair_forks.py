import os
import subprocess
from pathlib import Path

TARGET_DIR = Path(os.path.expanduser("~/antigravity-flattened"))

# Repos that failed to clone or went missing
MISSING_REPOS = [
    "https://github.com/google/generative-ai-python",
    "https://github.com/model-context-protocol/python-sdk",
]


def clone_missing():
    if not TARGET_DIR.exists():
        TARGET_DIR.mkdir(parents=True)

    for url in MISSING_REPOS:
        repo_name = url.split("/")[-1].replace(".git", "")
        # Handle the rename for python-sdk if needed to avoid conflicts?
        # Actually 'python-sdk' is generic, let's rename it to 'mcp-python-sdk' locally?
        # The main script forks it as 'python-sdk'. We should stick to that or be smarter.

        # But wait, looking at the previous output:
        # "ls: .../python-sdk: No such file or directory"

        print(f"Repairing {repo_name}...")
        try:
            subprocess.run(
                ["gh", "repo", "fork", url, "--clone", "--remote"], cwd=TARGET_DIR, check=True
            )
        except subprocess.CalledProcessError:
            print(f"gh fork failed for {repo_name}, trying git clone...")
            subprocess.run(["git", "clone", url], cwd=TARGET_DIR, check=True)


if __name__ == "__main__":
    clone_missing()
