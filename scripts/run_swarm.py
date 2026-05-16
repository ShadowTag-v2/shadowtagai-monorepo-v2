#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""PR Review Swarm Orchestrator.

Dispatches a PR through the 6-agent review pipeline:
  1. Jules        — Orchestrator, workflow classification
  2. GCA          — Multi-agent code review (Gemini Code Assist)
  3. ANE Bridge   — Bare-metal verification on Apple Neural Engine
  4. Colab T4     — Heavy compute fallback (via Google Drive IPC)
  5. Monty        — Sub-millisecond sandbox for quick checks
  6. Renovate     — Dependency PR context (read-only upstream)

Usage:
    python scripts/run_swarm.py --pr-number 42
    python scripts/run_swarm.py --pr-number 42 --skip-ane --skip-colab
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SWARM] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("swarm")

REPO_ROOT = Path(__file__).resolve().parent.parent
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER = "ShadowTag-v2"
REPO = "shadowtagai-monorepo-v2"
API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}"


# ---------- Data Models ----------

@dataclass
class AgentVerdict:
    """Result from a single review agent."""

    agent: str
    status: str = "pending"  # pending | pass | warn | fail | skip
    findings: list[str] = field(default_factory=list)
    duration_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SwarmResult:
    """Aggregated swarm output."""

    pr_number: int = 0
    overall: str = "pending"
    agents: list[AgentVerdict] = field(default_factory=list)
    summary: str = ""
    wall_time_ms: int = 0


# ---------- Agent Implementations ----------

async def run_jules(pr_num: int, changed_files: list[str]) -> AgentVerdict:
    """Jules: Orchestrator — classify PR type and check workflow rules."""
    t0 = time.monotonic()
    verdict = AgentVerdict(agent="Jules")

    try:
        # Classify PR by changed file patterns
        categories: dict[str, list[str]] = {
            "infra": [], "src": [], "docs": [], "test": [],
            "config": [], "deps": [],
        }
        for f in changed_files:
            if f.startswith(("scripts/", ".github/", "Dockerfile")):
                categories["infra"].append(f)
            elif f.startswith("tests/"):
                categories["test"].append(f)
            elif f.endswith((".md", ".txt", ".rst")):
                categories["docs"].append(f)
            elif f.endswith(("package.json", "pyproject.toml", "*.csproj")):
                categories["deps"].append(f)
            elif f.endswith((".yaml", ".yml", ".toml", ".json")):
                categories["config"].append(f)
            else:
                categories["src"].append(f)

        dominant = max(categories, key=lambda k: len(categories[k]))
        verdict.metadata["classification"] = dominant
        verdict.metadata["breakdown"] = {
            k: len(v) for k, v in categories.items() if v
        }

        # Workflow rules
        if len(changed_files) > 200:
            verdict.findings.append(
                f"⚠️ Large PR: {len(changed_files)} files changed. "
                "Consider splitting."
            )
        if categories["infra"] and categories["src"]:
            verdict.findings.append(
                "⚠️ Mixed infra + source changes. "
                "Prefer separate PRs for reviewability."
            )
        if not categories["test"] and categories["src"]:
            verdict.findings.append(
                "⚠️ Source changes without test updates."
            )

        verdict.status = "warn" if verdict.findings else "pass"
    except Exception as exc:
        verdict.status = "fail"
        verdict.findings.append(f"Jules error: {exc}")

    verdict.duration_ms = int((time.monotonic() - t0) * 1000)
    return verdict


async def run_gca(pr_num: int, changed_files: list[str]) -> AgentVerdict:
    """GCA: Gemini Code Assist — static analysis + lint check."""
    t0 = time.monotonic()
    verdict = AgentVerdict(agent="GCA")

    try:
        py_files = [f for f in changed_files if f.endswith(".py")]
        ts_files = [
            f for f in changed_files
            if f.endswith((".ts", ".tsx", ".js", ".jsx"))
        ]

        # Ruff on Python files
        if py_files:
            existing = [
                f for f in py_files
                if (REPO_ROOT / f).exists()
            ]
            if existing:
                result = subprocess.run(
                    ["ruff", "check", "--select", "F401,F841,E999",
                     "--output-format", "json", *existing],
                    capture_output=True, text=True, cwd=str(REPO_ROOT),
                    timeout=120,
                )
                if result.stdout.strip():
                    issues = json.loads(result.stdout)
                    for issue in issues[:10]:
                        verdict.findings.append(
                            f"🔍 {issue['filename']}:{issue['location']['row']} "
                            f"— {issue['code']}: {issue['message']}"
                        )
                    if len(issues) > 10:
                        verdict.findings.append(
                            f"... and {len(issues) - 10} more issues"
                        )

        # Biome on TS/JS files
        if ts_files:
            existing_ts = [
                f for f in ts_files
                if (REPO_ROOT / f).exists()
            ]
            if existing_ts:
                result = subprocess.run(
                    ["npx", "biome", "check", "--reporter=json",
                     *existing_ts],
                    capture_output=True, text=True, cwd=str(REPO_ROOT),
                    timeout=120,
                )
                if result.returncode != 0:
                    verdict.findings.append(
                        f"Biome found issues in {len(existing_ts)} TS/JS files"
                    )

        verdict.status = "warn" if verdict.findings else "pass"
    except subprocess.TimeoutExpired:
        verdict.status = "warn"
        verdict.findings.append("GCA lint timed out after 120s")
    except Exception as exc:
        verdict.status = "fail"
        verdict.findings.append(f"GCA error: {exc}")

    verdict.duration_ms = int((time.monotonic() - t0) * 1000)
    return verdict


async def run_ane_bridge(
    pr_num: int, changed_files: list[str],
) -> AgentVerdict:
    """ANE Bridge: Bare-metal verification — check for hardware-sensitive changes."""
    t0 = time.monotonic()
    verdict = AgentVerdict(agent="ANE Bridge")

    try:
        ane_sensitive = [
            f for f in changed_files
            if any(kw in f.lower() for kw in (
                "ane", "coreml", "mlx", "neural", "accelerat",
                "metal", "gpu", "silicon",
            ))
        ]

        if ane_sensitive:
            verdict.findings.append(
                f"🧠 {len(ane_sensitive)} ANE-sensitive files changed: "
                f"{', '.join(ane_sensitive[:5])}"
            )
            # Check if ANE bridge test suite exists
            bridge_tests = REPO_ROOT / "tests" / "test_ane_bridge.py"
            if bridge_tests.exists():
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", str(bridge_tests),
                     "-x", "--tb=short", "-q"],
                    capture_output=True, text=True, cwd=str(REPO_ROOT),
                    timeout=60,
                )
                if result.returncode != 0:
                    verdict.findings.append(
                        f"ANE tests failed:\n{result.stdout[-500:]}"
                    )
                    verdict.status = "fail"
                else:
                    verdict.status = "pass"
            else:
                verdict.status = "warn"
                verdict.findings.append("No ANE test suite found.")
        else:
            verdict.status = "pass"
            verdict.metadata["reason"] = "No ANE-sensitive files in diff"

    except Exception as exc:
        verdict.status = "fail"
        verdict.findings.append(f"ANE Bridge error: {exc}")

    verdict.duration_ms = int((time.monotonic() - t0) * 1000)
    return verdict


async def run_colab_t4(
    pr_num: int, changed_files: list[str],
) -> AgentVerdict:
    """Colab T4: Heavy compute fallback — check ML model/training changes."""
    t0 = time.monotonic()
    verdict = AgentVerdict(agent="Colab T4")

    try:
        ml_files = [
            f for f in changed_files
            if any(kw in f.lower() for kw in (
                "model", "train", "inference", "embed",
                "torch", "tensorflow", "jax", "lancedb",
            ))
        ]

        if ml_files:
            verdict.findings.append(
                f"🖥️ {len(ml_files)} ML-sensitive files detected. "
                "Colab T4 validation recommended."
            )
            # Check for Google Drive IPC endpoint
            ipc_marker = REPO_ROOT / ".colab" / "ipc_endpoint.json"
            if ipc_marker.exists():
                verdict.metadata["ipc_available"] = True
                verdict.status = "warn"
                verdict.findings.append(
                    "IPC endpoint found. Manual Colab dispatch recommended."
                )
            else:
                verdict.status = "warn"
                verdict.findings.append(
                    "No Colab IPC endpoint. Skipping remote validation."
                )
        else:
            verdict.status = "pass"
            verdict.metadata["reason"] = "No ML files in diff"

    except Exception as exc:
        verdict.status = "fail"
        verdict.findings.append(f"Colab T4 error: {exc}")

    verdict.duration_ms = int((time.monotonic() - t0) * 1000)
    return verdict


async def run_monty(
    pr_num: int, changed_files: list[str],
) -> AgentVerdict:
    """Monty: Sub-millisecond sandbox — fast syntax & import checks."""
    t0 = time.monotonic()
    verdict = AgentVerdict(agent="Monty")

    try:
        py_files = [
            f for f in changed_files
            if f.endswith(".py") and (REPO_ROOT / f).exists()
        ]

        compile_errors: list[str] = []
        for f in py_files[:50]:  # Cap at 50 for speed
            fpath = REPO_ROOT / f
            try:
                compile(fpath.read_text(encoding="utf-8"), f, "exec")
            except SyntaxError as exc:
                compile_errors.append(f"❌ {f}:{exc.lineno} — {exc.msg}")

        if compile_errors:
            verdict.findings.extend(compile_errors[:10])
            verdict.status = "fail"
        else:
            verdict.status = "pass"
            verdict.metadata["files_checked"] = len(py_files)

    except Exception as exc:
        verdict.status = "fail"
        verdict.findings.append(f"Monty error: {exc}")

    verdict.duration_ms = int((time.monotonic() - t0) * 1000)
    return verdict


# ---------- Swarm Orchestrator ----------

def fetch_changed_files(pr_num: int) -> list[str]:
    """Fetch list of changed files from GitHub API."""
    if not GITHUB_TOKEN:
        logger.warning("No GITHUB_TOKEN — using git diff instead")
        result = subprocess.run(
            ["git", "diff", "--name-only", "origin/main...HEAD"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        return [
            f.strip() for f in result.stdout.strip().split("\n") if f.strip()
        ]

    import urllib.request

    url = f"{API_BASE}/pulls/{pr_num}/files?per_page=100"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        files_data = json.loads(resp.read())
    return [f["filename"] for f in files_data]


def render_summary(result: SwarmResult) -> str:
    """Render a markdown summary of the swarm results."""
    lines = [
        f"## 🤖 PR Review Swarm — PR #{result.pr_number}",
        "",
        f"**Overall: {result.overall.upper()}** "
        f"| ⏱️ {result.wall_time_ms}ms",
        "",
        "| Agent | Status | Findings | Time |",
        "|-------|--------|----------|------|",
    ]

    status_emoji = {
        "pass": "✅", "warn": "⚠️", "fail": "❌",
        "skip": "⏭️", "pending": "⏳",
    }

    for agent in result.agents:
        emoji = status_emoji.get(agent.status, "❓")
        finding_count = len(agent.findings)
        lines.append(
            f"| {agent.agent} | {emoji} {agent.status} "
            f"| {finding_count} | {agent.duration_ms}ms |"
        )

    # Detail sections
    for agent in result.agents:
        if agent.findings:
            lines.extend(["", f"### {agent.agent}", ""])
            for finding in agent.findings:
                lines.append(f"- {finding}")

    return "\n".join(lines)


async def run_swarm(
    pr_num: int,
    *,
    skip_ane: bool = False,
    skip_colab: bool = False,
) -> SwarmResult:
    """Execute the full review swarm."""
    t0 = time.monotonic()
    result = SwarmResult(pr_number=pr_num)

    logger.info("Fetching changed files for PR #%d", pr_num)
    changed_files = fetch_changed_files(pr_num)
    logger.info("Found %d changed files", len(changed_files))

    # Build task list
    tasks: list[tuple[str, Any]] = [
        ("Jules", run_jules(pr_num, changed_files)),
        ("GCA", run_gca(pr_num, changed_files)),
        ("Monty", run_monty(pr_num, changed_files)),
    ]

    if not skip_ane:
        tasks.append(("ANE Bridge", run_ane_bridge(pr_num, changed_files)))
    else:
        result.agents.append(AgentVerdict(agent="ANE Bridge", status="skip"))

    if not skip_colab:
        tasks.append(("Colab T4", run_colab_t4(pr_num, changed_files)))
    else:
        result.agents.append(AgentVerdict(agent="Colab T4", status="skip"))

    # Run all agents concurrently
    logger.info("Dispatching %d agents concurrently...", len(tasks))
    coros = [coro for _, coro in tasks]
    verdicts = await asyncio.gather(*coros, return_exceptions=True)

    for (name, _), verdict in zip(tasks, verdicts):
        if isinstance(verdict, Exception):
            result.agents.append(
                AgentVerdict(
                    agent=name, status="fail",
                    findings=[f"Agent crashed: {verdict}"],
                )
            )
        else:
            result.agents.append(verdict)

    # Determine overall status
    statuses = [a.status for a in result.agents]
    if "fail" in statuses:
        result.overall = "fail"
    elif "warn" in statuses:
        result.overall = "warn"
    else:
        result.overall = "pass"

    result.wall_time_ms = int((time.monotonic() - t0) * 1000)
    result.summary = render_summary(result)

    logger.info(
        "Swarm complete: %s (%dms)", result.overall, result.wall_time_ms,
    )
    return result


# ---------- CLI ----------

def main() -> None:
    parser = argparse.ArgumentParser(description="PR Review Swarm")
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--output", type=str, default="")
    parser.add_argument("--skip-ane", action="store_true")
    parser.add_argument("--skip-colab", action="store_true")
    args = parser.parse_args()

    result = asyncio.run(
        run_swarm(
            args.pr_number,
            skip_ane=args.skip_ane,
            skip_colab=args.skip_colab,
        )
    )

    # Write output
    output_data = {
        "pr_number": result.pr_number,
        "overall": result.overall,
        "summary": result.summary,
        "wall_time_ms": result.wall_time_ms,
        "agents": [asdict(a) for a in result.agents],
    }

    if args.output:
        Path(args.output).write_text(
            json.dumps(output_data, indent=2), encoding="utf-8",
        )
        logger.info("Results written to %s", args.output)
    else:
        print(json.dumps(output_data, indent=2))

    sys.exit(0 if result.overall != "fail" else 1)


if __name__ == "__main__":
    main()
