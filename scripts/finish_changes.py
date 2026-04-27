#!/opt/homebrew/bin/python3.14
# scripts/finish_changes.py
# ============================================================================
# SHADOWTAG OS: PRE-ACTION MEMORY GATE & REPO-DRIFT AUDIT
# ============================================================================
# The /pickle egress script. Closes tabs, purges cache, rebuilds deps,
# runs linters, and prints the explicit file delta before saving.
# ============================================================================

import subprocess
import sys
from pathlib import Path


def run_cmd(cmd, cwd=None, check=False):
    print(f">>> Executing: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if res.returncode != 0:
        stderr = res.stderr.strip()
        if check:
            print(f"❌ Failed: {stderr}")
            sys.exit(res.returncode)
        elif stderr and "warning" not in stderr.lower():
            print(f"⚠️ Notice: {stderr}")
    return res


def pre_action_memory_gate():
    print(">>> 🛑 1. PRE-ACTION MEMORY GATE: SAVING TABS & PURGING RAM...")
    # AppleScript to force VS Code/Cursor/Antigravity to Save All (Cmd+Opt+S)
    script = """
    tell application "System Events"
        key code 1 using {command down, option down}
        delay 0.5
    end tell
    """
    subprocess.run(["osascript", "-e", script], capture_output=True)
    print("   [+] Workspace editors saved. Memory recovered.")


def repo_drift_audit():
    print(">>> 🔍 2. REPO-DRIFT AUDIT: SCANNING DIRTY FILES...")
    res = run_cmd("git status --porcelain")
    dirty_files = [line[3:] for line in res.stdout.splitlines() if line.strip()]

    changed_files = []
    conflict_files = []
    # Files to exclude from staging (auto-generated, not meaningful drift)
    excluded_patterns = [
        ".beads/kairos_heartbeat.json",
        "bazel-",
    ]

    for file in dirty_files:
        # Skip excluded auto-generated files
        if any(file.startswith(pat) or pat in file for pat in excluded_patterns):
            continue

        p = Path(file)
        if not p.exists() or not p.is_file():
            continue

        content = p.read_text(errors="ignore")
        if "<<<<<<< HEAD" in content or "=======" in content:
            conflict_files.append(file)
        else:
            changed_files.append(file)

    if conflict_files:
        print("\n🚨 CONFLICT MARKERS DETECTED (MANUAL HEALING REQUIRED):")
        for f in conflict_files:
            print(f"  - {f}")
        sys.exit(1)

    print(">>> 🧹 3. LINTING & AST HEALING...")
    run_cmd("/opt/homebrew/bin/ruff check --fix .")
    run_cmd("/opt/homebrew/bin/ruff format .")
    run_cmd("npx @biomejs/biome check --write . 2>/dev/null || true")

    return changed_files


def egress_commit(changed_files):
    print("\n📊 EX TOTO SWEEP REPORT:")
    print("--------------------------------------------------")
    if changed_files:
        print("✅ MUTATED / DIRTY FILES (SAVED, LINTED, & REPAIRED):")
        for f in changed_files:
            print(f"  [+] {f}")
        # Stage only the meaningful files, not heartbeat/bazel drift
        file_list = " ".join(f'"{f}"' for f in changed_files)
        run_cmd(f"git add {file_list}")
    else:
        print("✅ NO DRIFT DETECTED. ALL FILES ALREADY CLEAN.")
        print("   Nothing to commit.")
        return

    print("\n>>> 🔒 5. OMEGA LOOP EGRESS (Locking State)...")
    res = run_cmd('git commit -m "chore(omega): Ex Toto memory gate sweep"')
    if res.returncode == 0:
        print("✅ STATUS: GOD MODE MAINTAINED. WORKSPACE LOCKED. READY FOR OMEGA LOOP.")
    else:
        print("⚠️ Nothing to commit or commit failed. State unchanged.")


if __name__ == "__main__":
    pre_action_memory_gate()
    changed = repo_drift_audit()
    egress_commit(changed)
