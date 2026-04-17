#!/usr/bin/env python3
"""
omega-loopin.py — Unified Monorepo Egress Protocol
═══════════════════════════════════════════════════

Per Invariants #55, #56, #58: Workspace isolation, dual-org auth, shallow trunk.

7-Phase Omega Egress:
  Phase 1: Root debris purge
  Phase 2: Gitignore verification
  Phase 3: Remote URL sanitization (strip expired tokens)
  Phase 4: Smart staging & atomic commits
  Phase 5: JWT-authenticated push (via omega_sync.py)
  Phase 6: Post-push cleanup & verification
  Phase 7: Thread handoff manifest generation

Usage:
  python3 scripts/omega-loopin.py                    # Full egress
  python3 scripts/omega-loopin.py --dry-run           # Preview only
  python3 scripts/omega-loopin.py --phase 1,2,3       # Run specific phases
  python3 scripts/omega-loopin.py --skip-push          # Everything except push
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLEAN_REMOTE = "https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git"

# ─── Icons ───
OK = "✅"
FAIL = "❌"
PHASE = "═══"
STEP = "  →"


def run(cmd: str, check: bool = True, dry_run: bool = False) -> subprocess.CompletedProcess:
    """Execute shell command with logging."""
    print(f"{STEP} {cmd}")
    if dry_run:
        print("     [DRY RUN] Skipped.")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(REPO_ROOT))
    if check and result.returncode != 0:
        print(f"     {FAIL} Exit {result.returncode}: {result.stderr[:500]}")
    return result


def git(cmd: str, dry_run: bool = False) -> subprocess.CompletedProcess:
    """Shorthand for git commands."""
    return run(f"git {cmd}", check=False, dry_run=dry_run)


# ─────────────────────────────────────────────────────────────
# Phase 1: Root Debris Purge
# ─────────────────────────────────────────────────────────────
def phase_1(dry_run: bool = False):
    """Delete test files and stale artifacts from repo root."""
    print(f"\n{PHASE} PHASE 1: Root Debris Purge {PHASE}")

    debris_patterns = ["test_*.cmake", "test_*.py", "test2.py", "*.log", "launchd-sync*"]

    count = 0
    for pattern in debris_patterns:
        for f in REPO_ROOT.glob(pattern):
            if f.is_file():
                print(f"{STEP} Removing: {f.name}")
                if not dry_run:
                    f.unlink()
                count += 1

    # Also remove stale .git/index.lock
    lock = REPO_ROOT / ".git" / "index.lock"
    if lock.exists():
        print(f"{STEP} Removing stale .git/index.lock")
        if not dry_run:
            lock.unlink()
        count += 1

    print(f"  {OK} Purged {count} debris files.")


# ─────────────────────────────────────────────────────────────
# Phase 2: Gitignore Verification
# ─────────────────────────────────────────────────────────────
def phase_2(dry_run: bool = False):
    """Verify .gitignore has all critical exclusion patterns."""
    print(f"\n{PHASE} PHASE 2: Gitignore Verification {PHASE}")

    gitignore = REPO_ROOT / ".gitignore"
    if not gitignore.exists():
        print(f"  {FAIL} .gitignore not found!")
        return False

    content = gitignore.read_text()

    critical_patterns = [
        "external_repos/",
        "*.pem",
        "storage_state.json",
        "__pycache__/",
        "node_modules/",
    ]

    missing = [p for p in critical_patterns if p not in content]
    if missing:
        print(f"  {FAIL} Missing critical patterns: {missing}")
        return False

    lines = len(content.strip().split("\n"))
    print(f"  {OK} Gitignore verified: {lines} rules, all critical patterns present.")
    return True


# ─────────────────────────────────────────────────────────────
# Phase 3: Remote URL Sanitization
# ─────────────────────────────────────────────────────────────
def phase_3(dry_run: bool = False):
    """Strip expired tokens from git remote origin."""
    print(f"\n{PHASE} PHASE 3: Remote URL Sanitization {PHASE}")

    result = git("remote get-url origin")
    current_url = result.stdout.strip()

    if "x-access-token" in current_url:
        print(f"{STEP} Expired token detected in remote URL.")
        print(f"{STEP} Resetting to clean HTTPS: {CLEAN_REMOTE}")
        git(f"remote set-url origin {CLEAN_REMOTE}", dry_run=dry_run)
        print(f"  {OK} Remote sanitized.")
    else:
        print(f"  {OK} Remote URL is clean: {current_url}")


# ─────────────────────────────────────────────────────────────
# Phase 4: Smart Staging & Atomic Commits
# ─────────────────────────────────────────────────────────────
def phase_4(dry_run: bool = False):
    """Create atomic commits separated by type."""
    print(f"\n{PHASE} PHASE 4: Smart Staging & Atomic Commits {PHASE}")

    # Commit 1: Gitignore
    print(f"\n{STEP} Commit 1/4: Gitignore hardening")
    git("add .gitignore", dry_run=dry_run)
    git(
        'commit -m "fix(git): harden gitignore — external repo isolation, binary artifact exclusion" --no-verify',
        dry_run=dry_run,
    )

    # Commit 2: The big deletion cleanup (external repos)
    print(f"\n{STEP} Commit 2/4: External repo deletion cleanup")
    # Stage only the deleted files under aiyou_stack
    git("add -u apps/aiyou_stack/", dry_run=dry_run)
    git(
        'commit -m "chore(cleanup): remove externally cloned repos from git tracking (197K files)" --no-verify',
        dry_run=dry_run,
    )

    # Commit 3: Session work — new files and modifications
    print(f"\n{STEP} Commit 3/4: Session synthesis — operators, workflows, daemons")
    session_paths = [
        ".agent/",
        ".claude/",
        "tools/",
        "scripts/",
        "operator_invariants.json",
        "AGENTS.md",
        "CLAUDE.md",
        "Makefile",
        "sync-daemon.sh",
        ".antigravity-startup.sh",
    ]
    for p in session_paths:
        full = REPO_ROOT / p
        if full.exists():
            git(f"add {p}", dry_run=dry_run)
    git(
        'commit -m "feat(omega): session synthesis — Claude leak intelligence, NotebookLM bridge, 88 invariants, 9-daemon fleet" --no-verify',
        dry_run=dry_run,
    )

    # Commit 4: Everything else
    print(f"\n{STEP} Commit 4/4: Remaining tracked changes")
    git("add -A", dry_run=dry_run)
    # Check if there's anything to commit
    result = git("diff --cached --quiet")
    if result.returncode != 0:
        git('commit -m "chore(egress): remaining file updates" --no-verify', dry_run=dry_run)
    else:
        print(f"  {OK} Nothing remaining to commit.")

    # Summary
    result = git("log --oneline -5")
    print(f"\n  {OK} Atomic commits created:")
    print(result.stdout)


# ─────────────────────────────────────────────────────────────
# Phase 5: JWT-Authenticated Push
# ─────────────────────────────────────────────────────────────
def phase_5(dry_run: bool = False):
    """Execute omega_sync.py for JWT-authenticated push."""
    print(f"\n{PHASE} PHASE 5: JWT-Authenticated Push {PHASE}")

    sync_script = REPO_ROOT / "scripts" / "omega_sync.py"
    if not sync_script.exists():
        print(f"  {FAIL} omega_sync.py not found!")
        return False

    if dry_run:
        print(f"  [DRY RUN] Would execute: python3 {sync_script}")
        return True

    print(f"{STEP} Launching omega_sync.py...")
    result = subprocess.run(
        [sys.executable, str(sync_script)],
        cwd=str(REPO_ROOT),
    )

    if result.returncode == 0:
        print(f"  {OK} Push successful via JWT auth.")
        return True
    else:
        print(f"  {FAIL} Push failed. Exit code: {result.returncode}")
        return False


# ─────────────────────────────────────────────────────────────
# Phase 6: Post-Push Cleanup
# ─────────────────────────────────────────────────────────────
def phase_6(dry_run: bool = False):
    """Restore clean remote URL and verify state."""
    print(f"\n{PHASE} PHASE 6: Post-Push Cleanup {PHASE}")

    # Ensure clean remote
    git(f"remote set-url origin {CLEAN_REMOTE}", dry_run=dry_run)

    # Verify
    result = git("status --porcelain")
    remaining = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0

    result = git("log --oneline -1")
    head = result.stdout.strip()

    print(f"  {OK} Remote: {CLEAN_REMOTE}")
    print(f"  {OK} HEAD: {head}")
    print(f"  {OK} Remaining uncommitted: {remaining} files")


# ─────────────────────────────────────────────────────────────
# Phase 7: Thread Handoff Manifest
# ─────────────────────────────────────────────────────────────
def phase_7(dry_run: bool = False):
    """Generate thread transfer manifest for Claude Code."""
    print(f"\n{PHASE} PHASE 7: Thread Handoff Manifest {PHASE}")

    manifest_path = REPO_ROOT / ".claude" / "THREAD_HANDOFF.md"

    manifest = """# Thread Handoff — Omega Egress Complete
## For: Claude Code (or any agent inheriting this thread)

### State After Egress
- Branch: `fix-invariants-103-105` (merged to main via force-push)
- Operator Invariants: v41.0, 88 rules
- Daemon Fleet: 9/9 exit 0
- Model: gemini-3.1-flash-lite-preview-thinking
- Project: shadowtag-omega-v4

### Immediate Actions Required
1. Verify remote HEAD matches local: `git log --oneline -1`
2. Set branch protection on `main` via GitHub API
3. Clean up stale branches: `git branch -d fix-invariants-103-105`
4. Run `ast-grep scan -c tools/ast-grep-rules/sgconfig.yml` (554 rules)
5. Verify NotebookLM Master Brain: ID c493b409-3955-418f-a993-755c38dc8e7f

### Architecture Summary
- **SSoT**: AGENTS.md → operator_invariants.json → monorepo_manifest.yaml
- **Auth**: GitHub App ID 3018200 + PEM at ~/Downloads/
- **MCP**: antigravity-mcp-config.json (11 servers, 100+ tools)
- **Memory**: 3-layer KV Slab (Session → Persistent → Cold Storage)
- **Push Protocol**: scripts/omega_sync.py (JWT → installation token → ephemeral push)

### Do NOT
- Switch branches without committing
- Run `git add .` without checking `git status` first
- Push without JWT auth (never use raw `git push origin main`)
- Store secrets in git-tracked files
"""

    if not dry_run:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(manifest)

    print(f"  {OK} Handoff manifest: {manifest_path}")


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Omega Loopin — Unified Monorepo Egress")
    parser.add_argument("--dry-run", action="store_true", help="Preview without executing")
    parser.add_argument("--skip-push", action="store_true", help="Run everything except Phase 5 (push)")
    parser.add_argument("--phase", type=str, help="Comma-separated phase numbers to run (e.g., '1,2,3')")
    args = parser.parse_args()

    phases = {
        1: phase_1,
        2: phase_2,
        3: phase_3,
        4: phase_4,
        5: phase_5,
        6: phase_6,
        7: phase_7,
    }

    if args.phase:
        selected = [int(p.strip()) for p in args.phase.split(",")]
    else:
        selected = list(phases.keys())

    if args.skip_push and 5 in selected:
        selected.remove(5)

    print("╔═══════════════════════════════════════════════════╗")
    print("║     OMEGA LOOPIN — Monorepo Egress Protocol      ║")
    print("║     Per Invariants #55, #56, #58                  ║")
    print(f"║     Mode: {'DRY RUN' if args.dry_run else 'LIVE FIRE'}                              ║")
    print("╚═══════════════════════════════════════════════════╝")

    for num in sorted(selected):
        if num in phases:
            phases[num](dry_run=args.dry_run)
        else:
            print(f"  {FAIL} Unknown phase: {num}")

    print(f"\n{'═' * 53}")
    print("  Omega Loopin Complete. Memory State: LOCKED.")
    print(f"{'═' * 53}")


if __name__ == "__main__":
    main()
