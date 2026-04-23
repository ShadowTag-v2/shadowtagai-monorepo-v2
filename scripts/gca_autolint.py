#!/usr/bin/env python3
"""GCA Omni-Autolint — One-Shot CLI for Gemini Code Assist Extension.

This is NOT a daemon. It is a single-invocation CLI that the GCA extension
can bind to a task or keybinding. It:
  1. Authenticates via the GitHub App PEM (reuses auth_github_app.py)
  2. Runs the Omni-Linter triad: ruff check + ruff format + biome
  3. Traps fatal errors (exit code > 1) and aborts gracefully
  4. Shows `git diff` for human-in-the-loop review
  5. Pushes AST fixes via short-lived HTTPS token

Rich Hickey Doctrine: This replaces the rejected gca_autolint_daemon.py.
The CI workflow (.github/workflows/omni-autolint.yml) is the automated backstop.
This script is the operator-controlled LOCAL execution path.

Usage:
  python scripts/gca_autolint.py              # interactive mode (default)
  python scripts/gca_autolint.py --auto       # skip interactive prompt (CI-like)
  python scripts/gca_autolint.py --dry-run    # lint only, no commit/push
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Import auth from canonical module — single source of truth
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

REPO_OWNER = "ShadowTag-v2"
REPO_NAME = "Monorepo-Uphillsnowball"

# Linter commands with their descriptions
LINTERS = [
    {
        "name": "ruff check --fix",
        "cmd": [str(REPO_ROOT / ".venv/bin/ruff"), "check", "--fix", "--exit-zero", "."],
        "fatal_threshold": 2,  # exit > 1 = severe syntax crash
    },
    {
        "name": "ruff format",
        "cmd": [str(REPO_ROOT / ".venv/bin/ruff"), "format", "."],
        "fatal_threshold": 2,
    },
    {
        "name": "biome check --write",
        "cmd": [
            "bash",
            "-c",
            "export PATH=/opt/homebrew/bin:$PATH && "
            "node_modules/.bin/biome check --write --unsafe "
            "--files-ignore-unknown=true --no-errors-on-unmatched .",
        ],
        "fatal_threshold": 2,
    },
]


def _run(cmd: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
    """Execute a command, capturing output."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd or str(REPO_ROOT),
    )


def run_linters() -> bool:
    """Run the Omni-Linter triad. Returns True if all passed without fatal errors."""
    print("🧹 Running Omni-Linter Suite...")
    for linter in LINTERS:
        print(f"  ➤ {linter['name']}...")
        result = _run(linter["cmd"])

        # Judgment Check 1: Fatal Errors
        if result.returncode >= linter["fatal_threshold"]:
            print(f"\n  ❌ SEVERE ERROR in {linter['name']} (exit code {result.returncode})")
            if result.stderr:
                # Truncate to avoid flooding terminal
                stderr_lines = result.stderr.strip().split("\n")
                for line in stderr_lines[:20]:
                    print(f"     {line}")
                if len(stderr_lines) > 20:
                    print(f"     ... ({len(stderr_lines) - 20} more lines)")
            print("\n  🛑 Aborting to prevent repository corruption.")
            return False

        if result.returncode == 0:
            print("     ✅ Clean")
        else:
            print(f"     ⚠️ Warnings (exit {result.returncode}), fixes applied")

    print("  ✅ Linting pass complete.\n")
    return True


def check_changes() -> bool:
    """Returns True if git detects uncommitted modifications."""
    result = _run(["git", "status", "--porcelain"])
    return bool(result.stdout.strip())


def show_diff() -> str:
    """Print and return the git diff."""
    result = _run(["git", "diff"])
    return result.stdout


def commit_and_push(auto: bool = False) -> bool:
    """Stage, commit, and push AST fixes using the GitHub App token."""
    diff = show_diff()
    if not diff.strip():
        # Check staged changes too (biome may have added files)
        staged = _run(["git", "diff", "--staged"])
        if not staged.stdout.strip():
            print("✨ No AST changes detected. Repository is clean.")
            return True

    print("\n⚠️  AST changes detected. Diff preview:\n")
    # Truncate long diffs
    lines = diff.split("\n")
    for line in lines[:100]:
        print(f"  {line}")
    if len(lines) > 100:
        print(f"  ... ({len(lines) - 100} more lines)")

    # Judgment Check 2: Human-in-the-Loop
    if not auto:
        choice = input("\n🔍 AST changes detected. Review diff above.\n   Proceed with commit and push? (y/n): ")
        if choice.strip().lower() != "y":
            print("🛑 Aborting commit and push as requested.")
            return False

    # Import auth and get token
    try:
        from auth_github_app import get_token

        token = get_token()
    except Exception as e:
        print(f"❌ Auth failed: {e}")
        print("   Falling back to existing remote URL...")
        token = None

    # Set push URL with token
    if token:
        push_url = f"https://x-access-token:{token}@github.com/{REPO_OWNER}/{REPO_NAME}.git"
        _run(["git", "remote", "set-url", "--push", "origin", push_url])

    # Stage + Commit
    _run(["git", "add", "-A"])
    commit_result = _run(
        [
            "git",
            "commit",
            "-m",
            "chore(ast): autonomous AST optimization via GCA [skip ci]",
        ]
    )
    if commit_result.returncode != 0:
        print(f"❌ Commit failed: {commit_result.stderr}")
        return False

    # Push
    print("\n🚀 Pushing AST fixes...")
    push_result = _run(["git", "push", "origin", "main"])
    if push_result.returncode == 0:
        print("✅ Successfully pushed AST optimizations.")
    else:
        print(f"❌ Push failed: {push_result.stderr}")
        return False

    # Restore SSH push URL
    ssh_url = f"git@github.com:{REPO_OWNER}/{REPO_NAME}.git"
    _run(["git", "remote", "set-url", "--push", "origin", ssh_url])

    return True


def main():
    parser = argparse.ArgumentParser(
        description="GCA Omni-Autolint — One-Shot Continuous Self-Healing",
    )
    parser.add_argument("--auto", action="store_true", help="Skip interactive prompt")
    parser.add_argument("--dry-run", action="store_true", help="Lint only, no commit/push")
    args = parser.parse_args()

    print("=" * 60)
    print("  GCA Omni-Autolint v1.0 — Continuous Self-Healing")
    print("  Rich Hickey Doctrine: Simple Made Easy")
    print("=" * 60)
    print()

    # Pull latest
    print("📥 Pulling latest origin/main...")
    pull = _run(["git", "pull", "--rebase", "origin", "main"])
    if pull.returncode != 0:
        print(f"⚠️  Pull warning: {pull.stderr.strip()}")
    print()

    # Run linters
    if not run_linters():
        sys.exit(1)

    # Check for changes
    if not check_changes():
        print("✨ No AST changes detected. Repository is clean.")
        sys.exit(0)

    if args.dry_run:
        print("🔍 Dry run: showing diff only")
        diff = show_diff()
        print(diff)
        sys.exit(0)

    # Commit and push
    success = commit_and_push(auto=args.auto)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
