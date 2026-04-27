"""GCA God Mode Bridge — gca_god_mode_bridge.py

Bridge between 'f1 gca' finish alias and god_mode_admin.py.
Orchestrates: save all → build C# → stage → commit → close.

Workflow:
  1. Run step_zero_cleanup.sh (dead code pruning)
  2. Build C# projects (dotnet build)
  3. Run ruff + vulture on Python
  4. git add -A
  5. git commit (conventional commit message)
  6. Report status
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
BEADS_DIR = REPO_ROOT / ".beads"
GCA_LOG = BEADS_DIR / "gca_log.jsonl"

# C# project paths
CSHARP_PROJECTS = [
    REPO_ROOT / "apps" / "AiYou.Kernel" / "ShadowTagV4.Kernel.csproj",
]


def run_cmd(
    cmd: list[str],
    cwd: Path | None = None,
    timeout: int = 120,
) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return 1, "", f"Command not found: {cmd[0]}"


def step_zero() -> dict[str, Any]:
    """Phase 1: Dead code pruning."""
    script = REPO_ROOT / "scripts" / "step_zero_cleanup.sh"
    if script.exists():
        rc, out, err = run_cmd(["bash", str(script)])
        return {"phase": "step_zero", "success": rc == 0, "output": out[:500]}
    return {"phase": "step_zero", "success": True, "output": "Script not found — skipped"}


def build_csharp() -> dict[str, Any]:
    """Phase 2: Build C# projects."""
    results: list[dict[str, Any]] = []
    for proj in CSHARP_PROJECTS:
        if not proj.exists():
            results.append({"project": str(proj), "status": "skipped (not found)"})
            continue
        rc, out, err = run_cmd(
            ["dotnet", "build", str(proj), "--nologo", "-v", "quiet"],
            timeout=180,
        )
        results.append(
            {
                "project": proj.name,
                "status": "success" if rc == 0 else "failed",
                "errors": err[:300] if rc != 0 else None,
            }
        )
    all_ok = all(r["status"] != "failed" for r in results)
    return {"phase": "build_csharp", "success": all_ok, "projects": results}


def lint_python() -> dict[str, Any]:
    """Phase 3: ruff + vulture on Python."""
    rc, out, err = run_cmd(
        ["ruff", "check", "--fix", "--unsafe-fixes", "."],
    )
    ruff_ok = rc == 0

    rc2, out2, err2 = run_cmd(
        ["vulture", ".", "--min-confidence", "90"],
    )
    vulture_findings = len(out2.strip().splitlines()) if out2.strip() else 0

    return {
        "phase": "lint_python",
        "ruff_clean": ruff_ok,
        "vulture_findings": vulture_findings,
        "success": ruff_ok,
    }


def stage_and_commit(message: str | None = None) -> dict[str, Any]:
    """Phase 4-5: git add -A && git commit."""
    rc, _, err = run_cmd(["git", "add", "-A"])
    if rc != 0:
        return {"phase": "git", "success": False, "error": err[:200]}

    if message is None:
        message = f"chore: f1 gca finish ({datetime.now(UTC).strftime('%Y-%m-%d %H:%M')})"

    rc, out, err = run_cmd(["git", "commit", "-m", message])
    committed = rc == 0 or "nothing to commit" in (out + err)

    return {
        "phase": "git",
        "success": committed,
        "message": message,
        "output": out[:200] if out else err[:200],
    }


def run_gca(commit_message: str | None = None) -> dict[str, Any]:
    """Full GCA pipeline: step_zero → build → lint → commit."""
    BEADS_DIR.mkdir(parents=True, exist_ok=True)

    phases = [
        step_zero(),
        build_csharp(),
        lint_python(),
        stage_and_commit(commit_message),
    ]

    all_ok = all(p["success"] for p in phases)
    summary = {
        "gca_run": datetime.now(UTC).isoformat(),
        "all_phases_passed": all_ok,
        "phases": phases,
    }

    # Log to JSONL
    with GCA_LOG.open("a") as f:
        f.write(json.dumps(summary, default=str) + "\n")

    return summary


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else None
    result = run_gca(commit_message=msg)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["all_phases_passed"] else 1)
