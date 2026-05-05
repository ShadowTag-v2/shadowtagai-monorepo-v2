#!/usr/bin/env python3
"""Omni-Autolint Daemon — Secure lint + push via GitHub App short-lived tokens.

Astral Ruff Integration:
    - Core: https://github.com/astral-sh/ruff
    - Pre-commit: https://github.com/astral-sh/ruff-pre-commit
    - VSCode: https://github.com/astral-sh/ruff-vscode (charliermarsh.ruff)

Usage:
    python3 scripts/gca_autolint_daemon.py              # Interactive mode
    python3 scripts/gca_autolint_daemon.py --yes         # Headless auto-approve
    python3 scripts/gca_autolint_daemon.py --json        # Write results to .lint-results/
    python3 scripts/gca_autolint_daemon.py --dry-run     # Run linters, skip push
    python3 scripts/gca_autolint_daemon.py --timeout 300 # Custom lint timeout (seconds)
    python3 scripts/gca_autolint_daemon.py --exclude 'libs/,docs/' # Skip paths
    python3 scripts/gca_autolint_daemon.py --notify      # Send GWS notification on completion
    python3 scripts/gca_autolint_daemon.py --aggressive  # Enable unsafe ruff fixes
    CI=true python3 scripts/gca_autolint_daemon.py       # Headless via env var
"""

import argparse
import contextlib
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, UTC
from pathlib import Path

# Augment PATH for non-interactive shells (Python 3.14 subprocess may not
# inherit zsh PATH that includes homebrew, cargo, etc.)
_EXTRA_PATHS = [
    "/opt/homebrew/bin",
    str(Path.home() / ".local" / "bin"),
    str(Path.home() / ".cargo" / "bin"),
    "/usr/local/bin",
]
_current_path = os.environ.get("PATH", "")
_missing = [p for p in _EXTRA_PATHS if p not in _current_path]
if _missing:
    os.environ["PATH"] = ":".join(_missing) + ":" + _current_path

import jwt
import requests

# --- Constants ---
APP_ID = "3018200"
REPO_OWNER = "ShadowTag-v2"
REPO_NAME = "Monorepo-Uphillsnowball"
GITHUB_APP_NOREPLY = "3018200+shadowtag-bot[bot]@users.noreply.github.com"
RESULTS_DIR = Path(".lint-results")
RESULTS_FILE = RESULTS_DIR / "latest.json"
BEADS_DIR = Path(".beads")
BEADS_ISSUES = BEADS_DIR / "issues.jsonl"
BEADS_HEARTBEAT = BEADS_DIR / "heartbeat.json"
DEFAULT_TIMEOUT = 600  # 10 minutes per linter

# 5-tier PEM fallback chain (github_doctrine)
PEM_CANDIDATES = [
    # Tier 1: GCP Secret Manager — handled separately via gcloud CLI
    # Tier 2: keys/ directory
    Path("keys/antigravity-shadowtag-manager.pem"),
    # Tier 3: ~/Downloads (canonical local)
    Path.home() / "Downloads" / "antigravity-shadowtag-manager.2026-03-17.private-key.pem",
    # Tier 4: ~/.ssh/
    Path.home() / ".ssh" / "antigravity-shadowtag-manager.pem",
]


def resolve_pem_path() -> Path:
    """Resolve PEM path using the 5-tier fallback chain."""
    # Tier 5: $SHADOWTAG_PEM env var (checked first for override)
    import os

    env_pem = os.environ.get("SHADOWTAG_PEM")
    if env_pem:
        p = Path(env_pem)
        if p.exists():
            return p

    for candidate in PEM_CANDIDATES:
        if candidate.exists():
            return candidate

    # Tier 1 fallback: Try GCP Secret Manager
    try:
        result = subprocess.run(
            [
                "gcloud",
                "secrets",
                "versions",
                "access",
                "latest",
                "--secret=github-app-shadowtag-v2-pem",
                "--project=shadowtag-omega-v4",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            tmp = Path(tempfile.mktemp(suffix=".pem"))
            tmp.write_text(result.stdout)
            return tmp
    except FileNotFoundError, subprocess.TimeoutExpired:
        pass

    print("[!] FATAL: No PEM file found in any of the 5 fallback tiers.")
    print("    Checked: $SHADOWTAG_PEM, keys/, ~/Downloads/, ~/.ssh/, GCP Secret Manager")
    sys.exit(1)


def generate_jwt(app_id: str, pem_path: Path) -> str:
    """Generate RS256 JWT for GitHub App Authentication."""
    private_key = pem_path.read_bytes()
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + (10 * 60), "iss": app_id}
    return jwt.encode(payload, private_key, algorithm="RS256")


def get_installation_id(jwt_token: str) -> int:
    """Fetch the installation ID for the specific repository."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/installation"
    headers = {"Authorization": f"Bearer {jwt_token}", "Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()["id"]


def get_access_token(jwt_token: str, installation_id: int) -> str:
    """Exchange JWT and Installation ID for a short-lived access token."""
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {"Authorization": f"Bearer {jwt_token}", "Accept": "application/vnd.github.v3+json"}
    response = requests.post(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()["token"]


def run_command(
    command: list[str],
    check_fatal: bool = False,
    env_override: dict | None = None,
) -> subprocess.CompletedProcess:
    """Run a shell command, optionally checking for fatal errors (exit code > 1)."""
    print(f"[*] Running: {' '.join(command)}")

    import os

    kwargs: dict = {"capture_output": True, "text": True}
    if env_override:
        env = dict(os.environ)
        env.update(env_override)
        kwargs["env"] = env

    result = subprocess.run(command, **kwargs)

    if check_fatal and result.returncode > 1:
        print(f"\n[!] FATAL ERROR: {' '.join(command)} exited with code {result.returncode}")
        print("STDOUT:\n", result.stdout[-2000:] if result.stdout else "(empty)")
        print("STDERR:\n", result.stderr[-2000:] if result.stderr else "(empty)")
        print("Aborting to prevent pushing a broken tree.")
        sys.exit(1)

    return result


def create_git_askpass_helper(token: str) -> str:
    """Create a temporary GIT_ASKPASS helper script that injects the token securely.

    This prevents the token from appearing in process arguments, shell history,
    or git remote -v output.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as helper:
        helper.write(f"#!/bin/sh\necho {token}\n")
    Path(helper.name).chmod(0o700)
    return helper.name


def secure_push(access_token: str, branch_name: str) -> subprocess.CompletedProcess:
    """Push via HTTPS with token injected through GIT_ASKPASS (never in URL)."""
    import os

    askpass_helper = create_git_askpass_helper(access_token)
    remote_url = f"https://x-access-token@github.com/{REPO_OWNER}/{REPO_NAME}.git"

    try:
        result = run_command(
            ["git", "push", remote_url, f"HEAD:refs/heads/{branch_name}"],
            env_override={
                "GIT_ASKPASS": askpass_helper,
                "GIT_TERMINAL_PROMPT": "0",
            },
        )
    finally:
        # Clean up helper script immediately
        with contextlib.suppress(OSError):
            os.unlink(askpass_helper)

    return result


def get_ruff_version() -> str:
    """Capture current ruff version for reproducibility (item 5)."""
    try:
        r = subprocess.run(
            ["ruff", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except FileNotFoundError, subprocess.TimeoutExpired:
        return "unknown"


def run_linters(
    timeout: int = DEFAULT_TIMEOUT,
    exclude: str = "",
    aggressive: bool = False,
    dry_run: bool = False,
) -> dict:
    """Execute the full Omni-Linter suite and return structured results.

    Ruff integration:
        - Core: https://github.com/astral-sh/ruff
        - Pre-commit: https://github.com/astral-sh/ruff-pre-commit
        - VSCode: https://github.com/astral-sh/ruff-vscode
    """
    results = {}
    base_exclude = "external_repos,node_modules,.venv"
    if exclude:
        base_exclude = f"{base_exclude},{exclude}"

    # Item 5: Capture ruff version for beads reproducibility
    results["ruff_version"] = {"exit_code": 0, "stdout": get_ruff_version(), "stderr": ""}

    # 1. Ruff check + fix (item 7: JSON output, item 9: --unsafe-fixes)
    ruff_check_cmd = ["ruff", "check", "--fix", "--output-format=json", "."]
    if aggressive:
        ruff_check_cmd.insert(3, "--unsafe-fixes")
    r = run_command(ruff_check_cmd, check_fatal=True)
    results["ruff_check"] = {"exit_code": r.returncode, "stdout": r.stdout, "stderr": r.stderr}

    # Item 8: Ruff statistics summary
    r_stats = run_command(["ruff", "check", "--statistics", "."])
    results["ruff_statistics"] = {"exit_code": r_stats.returncode, "stdout": r_stats.stdout, "stderr": r_stats.stderr}

    # 2. Ruff format (item 11: diff mode for dry-run)
    if dry_run:
        r = run_command(["ruff", "format", "--diff", "."])
    else:
        r = run_command(["ruff", "format", "."], check_fatal=True)
    results["ruff_format"] = {"exit_code": r.returncode, "stdout": r.stdout, "stderr": r.stderr}

    # 3. Ruff dead-code focused pass (V22 Pruned Singularity — replaces vulture)
    r = run_command(
        ["ruff", "check", "--select", "F401,F841", "--statistics", "."],
        check_fatal=False,
    )
    results["ruff_dead_code"] = {"exit_code": r.returncode, "stdout": r.stdout, "stderr": r.stderr}

    # 4. Biome check + fix
    r = run_command(["npx", "@biomejs/biome", "check", "--write", "."], check_fatal=True)
    results["biome"] = {"exit_code": r.returncode, "stdout": r.stdout, "stderr": r.stderr}

    return results


def write_beads_entry(lint_results: dict) -> None:
    """Append a structured entry to .beads/issues.jsonl for audit trail (item 9)."""
    BEADS_DIR.mkdir(parents=True, exist_ok=True)
    # Exclude meta-entries (ruff_version, ruff_statistics) from severity calc
    tool_results = {k: v for k, v in lint_results.items() if k not in ("ruff_version", "ruff_statistics")}
    total_warnings = sum(1 for d in tool_results.values() if d["exit_code"] == 1)
    total_fatals = sum(1 for d in tool_results.values() if d["exit_code"] > 1)
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "source": "omni-autolint-daemon",
        "type": "lint_sweep",
        "severity": "FATAL" if total_fatals else ("WARNING" if total_warnings else "CLEAN"),
        "summary": f"{total_fatals} fatal, {total_warnings} warnings across {len(tool_results)} tools",
        "tools": {k: {"exit_code": v["exit_code"]} for k, v in tool_results.items()},
        "ruff_version": lint_results.get("ruff_version", {}).get("stdout", "unknown"),
    }
    with BEADS_ISSUES.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[*] Beads audit entry written to {BEADS_ISSUES}")


def write_heartbeat(phase: str, status: str) -> None:
    """Write daemon health check to .beads/heartbeat.json (item 16)."""
    BEADS_DIR.mkdir(parents=True, exist_ok=True)
    heartbeat = {
        "daemon": "omni-autolint",
        "timestamp": datetime.now(UTC).isoformat(),
        "pid": os.getpid(),
        "phase": phase,
        "status": status,
    }
    BEADS_HEARTBEAT.write_text(json.dumps(heartbeat, indent=2))


def send_gws_notification(summary: str, branch: str = "") -> None:
    """Send Google Workspace notification on completion (items 11, 12).

    Uses gws CLI if available, otherwise logs and skips.
    """
    import shutil

    gws = shutil.which("gws")
    if not gws:
        print("[*] GWS CLI not found — notification skipped (install googleworkspace/cli)")
        return
    msg = f"🤖 Omni-Autolint: {summary}"
    if branch:
        msg += f" → branch: {branch}"
    try:
        subprocess.run(
            [gws, "chat", "spaces", "messages", "create", "--space=spaces/autolint-alerts", f"--text={msg}"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        print(f"[*] GWS notification sent: {msg[:80]}")
    except FileNotFoundError, subprocess.TimeoutExpired:
        print("[*] GWS notification failed — continuing")


def write_results_json(lint_results: dict, diff_stats: str) -> None:
    """Write structured results to .lint-results/latest.json for cross-agent consumption."""
    RESULTS_DIR.mkdir(exist_ok=True)

    output = {
        "timestamp": datetime.now(UTC).isoformat(),
        "findings": {},
        "git_diff_stats": diff_stats,
    }

    for tool_name, data in lint_results.items():
        exit_code = data["exit_code"]
        if exit_code > 1:
            severity = "FATAL"
        elif exit_code == 1:
            severity = "WARNING"
        else:
            severity = "CLEAN"

        output["findings"][tool_name] = {
            "severity": severity,
            "exit_code": exit_code,
            "output_lines": len(data["stdout"].splitlines()) if data["stdout"] else 0,
        }

    RESULTS_FILE.write_text(json.dumps(output, indent=2))
    print(f"[*] Results written to {RESULTS_FILE}")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Omni-Autolint Daemon — Secure lint + push")
    parser.add_argument("--yes", "-y", action="store_true", help="Auto-approve changes (headless mode)")
    parser.add_argument("--json", action="store_true", help="Write structured results to .lint-results/")
    parser.add_argument("--dry-run", action="store_true", help="Run linters but skip commit/push")
    parser.add_argument("--branch", type=str, default=None, help="Custom branch name (default: chore/autolint-{timestamp})")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"Timeout per linter in seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--exclude", type=str, default="", help="Comma-separated paths to exclude (e.g., 'libs/,docs/')")
    parser.add_argument("--notify", action="store_true", help="Send GWS notification on completion")
    parser.add_argument("--aggressive", action="store_true", help="Enable ruff --unsafe-fixes (item 9)")
    return parser.parse_args()


def main() -> None:
    """Main daemon entry point."""
    import os

    args = parse_args()
    headless = args.yes or os.environ.get("CI", "").lower() == "true"

    print("=== Omni-Autolint Daemon ===")

    # --- Phase 1: Authenticate ---
    print("[1] Authenticating with GitHub App...")
    try:
        pem_path = resolve_pem_path()
        print(f"[*] PEM resolved: {pem_path}")
        jwt_token = generate_jwt(APP_ID, pem_path)
        installation_id = get_installation_id(jwt_token)
        access_token = get_access_token(jwt_token, installation_id)
        print(f"[*] Short-lived token acquired (Installation ID: {installation_id}).")
    except Exception as e:
        print(f"[!] Authentication failed: {e}")
        sys.exit(1)

    # --- Phase 2: Sync ---
    print("\n[2] Synchronizing with origin/main...")
    run_command(["git", "pull", "origin", "main"])

    # --- Phase 3: Lint ---
    print("\n[3] Running Omni-Linter Suite (ruff + biome)...")
    print("    Ruff: https://github.com/astral-sh/ruff")
    write_heartbeat("lint", "running")
    lint_results = run_linters(
        timeout=args.timeout,
        exclude=args.exclude,
        aggressive=args.aggressive,
        dry_run=args.dry_run,
    )
    write_heartbeat("lint", "complete")

    # Write beads audit trail (item 9)
    write_beads_entry(lint_results)

    # --- Phase 3.5: Repo Doctor Health Check (Risk #85 remediation) ---
    print("\n[3.5] Running Repo Doctor health check...")
    repo_doctor_script = Path("scripts/repo_doctor.py")
    if repo_doctor_script.exists():
        import sys as _sys

        rd = subprocess.run(
            [_sys.executable, str(repo_doctor_script)],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if rd.returncode != 0:
            print(f"[!] Repo Doctor warnings:\n{rd.stdout[-1000:]}")
        else:
            print("[*] Repo Doctor: healthy")
        lint_results["repo_doctor"] = {"exit_code": rd.returncode, "stdout": rd.stdout, "stderr": rd.stderr}
    else:
        print("[*] Repo Doctor script not found — skipping")

    # --- Phase 4: Evaluate ---
    print("\n[4] Evaluating modifications...")
    status_result = run_command(["git", "status", "--porcelain"])
    diff_stat_result = run_command(["git", "diff", "--stat"])

    # Write JSON results if requested
    if args.json:
        write_results_json(lint_results, diff_stat_result.stdout)

    if not status_result.stdout.strip():
        print("[*] No AST changes detected. Working tree is clean.")
        return

    # --- Phase 5: Review + Push ---
    print("\n[*] AST modifications detected:")
    print(diff_stat_result.stdout)

    if args.dry_run:
        print("[DRY-RUN] Skipping commit/push as requested.")
        return

    # Human-in-the-loop or headless auto-approve
    if headless:
        print("[HEADLESS] Auto-approving changes (--yes or CI=true).")
        approved = True
    else:
        diff_result = run_command(["git", "diff"])
        print("\n--- DIFF START ---")
        print(diff_result.stdout[:10000])
        if len(diff_result.stdout) > 10000:
            print(f"... ({len(diff_result.stdout) - 10000} more characters truncated)")
        print("--- DIFF END ---\n")
        choice = input("Proceed with commit and push? (y/n): ")
        approved = choice.strip().lower() == "y"

    if not approved:
        print("[*] Commit aborted by user.")
        return

    # Create branch (never push directly to main)
    branch_name = args.branch or f"chore/autolint-{int(time.time())}"
    run_command(["git", "checkout", "-b", branch_name])

    # Configure git user
    run_command(["git", "config", "user.name", "Omni-Autolint Bot[bot]"])
    run_command(["git", "config", "user.email", GITHUB_APP_NOREPLY])

    # Configure commit signing with the Agent's DID SSH key
    did_key_path = Path("keys/agent_did_ed25519")
    commit_cmd = ["git", "commit", "-m", "chore(ast): autonomous AST optimization via GCA"]

    if did_key_path.exists():
        did_key_path.chmod(0o600)
        run_command(["git", "config", "commit.gpgsign", "true"])
        run_command(["git", "config", "gpg.format", "ssh"])
        run_command(["git", "config", "user.signingkey", str(did_key_path.absolute())])
        commit_cmd.insert(2, "-S")
    else:
        print("[!] DID SSH key not found. Commits will not be signed.")
        run_command(["git", "config", "commit.gpgsign", "false"])

    # Stage and commit
    run_command(["git", "add", "."])
    run_command(commit_cmd)

    # Secure push via GIT_ASKPASS (token never in URL args)
    print("[*] Pushing securely via GIT_ASKPASS...")
    push_result = secure_push(access_token, branch_name)

    if push_result.returncode != 0:
        print(f"[!] Push failed:\n{push_result.stderr}")
        sys.exit(1)

    print(f"[*] Push successful to branch: {branch_name}")
    write_heartbeat("push", "complete")

    # Notify via GWS if requested (items 11, 12)
    if args.notify:
        send_gws_notification("Push complete", branch_name)

    # Return to main
    run_command(["git", "checkout", "main"])
    print(f"[*] Done. Create a PR from '{branch_name}' → main.")


if __name__ == "__main__":
    main()
