import json
import os
import subprocess

# Configuration – read from environment variables
REPO_NAME = os.getenv("GITHUB_REPO")  # e.g. "owner/repo"
APPROVAL_MESSAGE = "Auto‑approved by admin script."

if not REPO_NAME:
    # Try to infer from current directory if not set, or just warn
    print(
        "Warning: GITHUB_REPO not set. Assuming current directory is the repo or 'gh' context is set."
    )


def main():
    # Check if gh is authenticated
    try:
        subprocess.run(["gh", "auth", "status"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Error: 'gh' CLI is not authenticated. Please run 'gh auth login' first.")
        return

    # List open PRs
    cmd = ["gh", "pr", "list", "--state", "open", "--json", "number,title"]
    if REPO_NAME:
        cmd.extend(["--repo", REPO_NAME])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        prs = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error listing PRs: {e.stderr}")
        return

    approved = 0
    for pr in prs:
        number = pr["number"]
        title = pr["title"]
        print(f"Approving PR #{number}: {title}...")
        try:
            approve_cmd = [
                "gh",
                "pr",
                "review",
                str(number),
                "--approve",
                "--body",
                APPROVAL_MESSAGE,
            ]
            if REPO_NAME:
                approve_cmd.extend(["--repo", REPO_NAME])
            subprocess.run(approve_cmd, check=True, capture_output=True)
            print(" -> Success.")
            approved += 1
        except subprocess.CalledProcessError:
            print(
                f" -> Failed to approve PR #{number}. It might be already approved or you can't approve your own PR."
            )
            # print(e.stderr)

    print(f"Done. Approved {approved} pull request(s).")


if __name__ == "__main__":
    main()
