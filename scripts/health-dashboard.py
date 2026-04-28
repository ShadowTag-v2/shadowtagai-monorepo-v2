#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Monorepo Health Dashboard — generates a terminal-friendly status report.

V22 Pruned Singularity: vulture replaced with ruff F401/F841 dead-code pass.

Usage:
    python3 scripts/health-dashboard.py
    python3 scripts/health-dashboard.py --json  # Machine-readable output
"""

import pathlib
import subprocess
import sys
from datetime import datetime


def run(cmd: str, cwd: str = ".") -> tuple[int, str]:
    """Run a command and return (exit_code, stdout)."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=30)  # nosec B602 — intentional shell for git/system ops
    return result.returncode, result.stdout.strip()


def check_tests() -> dict:
    code, out = run("python3 -m pytest tests/ -q --tb=no 2>/dev/null")
    lines = out.strip().split("\n")
    last = lines[-1] if lines else ""
    return {"status": "✅" if code == 0 else "❌", "detail": last, "code": code}


def check_ruff() -> dict:
    code, out = run("python3 -m ruff check control/pnkln/ scripts/ 2>/dev/null")
    return {"status": "✅" if code == 0 else "❌", "detail": out or "All checks passed", "code": code}


def check_ruff_dead_code() -> dict:
    """Dead-code detection via ruff F401/F841 (replaces vulture, V22 Pruned Singularity)."""
    code, out = run("python3 -m ruff check --select F401,F841 scripts/ apps/counselconduit/ --statistics 2>/dev/null")
    return {"status": "✅" if code == 0 else "⚠️", "detail": out or "No dead code", "code": code}


def check_git() -> dict:
    _, branch = run("git branch --show-current")
    _, status = run("git status --porcelain")
    _, last_commit = run("git log -1 --format='%h %s' 2>/dev/null")
    dirty_count = len([l for l in status.split("\n") if l.strip()]) if status else 0  # noqa: E741
    return {
        "branch": branch,
        "dirty_files": dirty_count,
        "last_commit": last_commit,
        "status": "✅" if dirty_count == 0 else f"⚠️ {dirty_count} uncommitted",
    }


def check_workflows() -> dict:
    wf_dir = pathlib.Path(".github/workflows")
    if not wf_dir.exists():
        return {"count": 0, "status": "❌ No workflows directory"}
    files = list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml"))
    return {"count": len(files), "status": f"✅ {len(files)} workflows"}


def check_daemons() -> dict:
    _code, out = run("launchctl list 2>/dev/null | grep pnkln")
    daemons = [l.split("\t") for l in out.split("\n") if l.strip()] if out else []  # noqa: E741
    active = sum(1 for d in daemons if d[0] != "-")
    return {
        "total": len(daemons),
        "active": active,
        "status": f"✅ {active}/{len(daemons)} running",
    }


def check_disk() -> dict:
    _, out = run("df -h / | tail -1")
    parts = out.split()
    return {
        "total": parts[1] if len(parts) > 1 else "?",
        "used": parts[2] if len(parts) > 2 else "?",
        "free": parts[3] if len(parts) > 3 else "?",
        "pct": parts[4] if len(parts) > 4 else "?",
        "status": f"✅ {parts[3]} free" if len(parts) > 3 else "?",
    }


def check_git_pack() -> dict:
    pack_dir = pathlib.Path(".git/objects/pack")
    if not pack_dir.exists():
        return {"size": "?", "status": "❌"}
    total = sum(f.stat().st_size for f in pack_dir.glob("*.pack"))
    size_gb = total / (1024**3)
    return {"size_gb": round(size_gb, 1), "status": f"{'⚠️' if size_gb > 5 else '✅'} {size_gb:.1f} GB"}


def main() -> None:
    as_json = "--json" in sys.argv

    checks = {
        "timestamp": datetime.now().isoformat(),
        "tests": check_tests(),
        "lint": check_ruff(),
        "dead_code": check_ruff_dead_code(),
        "git": check_git(),
        "workflows": check_workflows(),
        "daemons": check_daemons(),
        "disk": check_disk(),
        "git_pack": check_git_pack(),
    }

    if as_json:
        return

    all(c.get("code", 0) == 0 if "code" in c else True for c in [checks["tests"], checks["lint"]])


if __name__ == "__main__":
    main()
