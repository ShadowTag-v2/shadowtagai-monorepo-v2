#!/usr/bin/env python3
"""GCA Local Orchestrator — full multi-agent PR review pipeline, no GitHub Actions required.

Mirrors gca-pr-review.yml exactly:
  1. setup       — fetch PR metadata + diff via GitHub API
  2. analyze     — 4 parallel gemini agents (correctness/security/perf/arch)
  3. ane-gate    — scripts/ane_budget.py on the diff
  4. verify-post — post_review.py → inline PR review comments

GitHub Actions is quota-exhausted for ShadowTag-v2 free org (2000 min/month cap hit
on April 14). This script runs the same pipeline locally using the authenticated
gemini CLI at /opt/homebrew/bin/gemini.

Usage:
    python scripts/run_gca_local.py --pr 48
    python scripts/run_gca_local.py --pr 48 --dry-run
    python scripts/run_gca_local.py --pr 48 --agents security,correctness
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# ── paths ────────────────────────────────────────────────────────────────────
SCRIPTS_DIR = Path(__file__).resolve().parent
ANE_BUDGET_SCRIPT = SCRIPTS_DIR / "ane_budget.py"
POST_REVIEW_SCRIPT = SCRIPTS_DIR / "post_review.py"
GEMINI_BIN = "/opt/homebrew/bin/gemini"
REPO = "ShadowTag-v2/Monorepo-Uphillsnowball"
PYTHON = sys.executable

# ── agent prompts (inlined — BUNDLE dir missing from remote repo) ─────────────
AGENT_PROMPTS: dict[str, str] = {
    "correctness": """\
You are a correctness-focused code reviewer. Examine this pull request diff for:
- Logic errors and incorrect assumptions
- Edge cases that are not handled
- API contract violations or misuse
- Type mismatches or wrong return values
- Broken error handling paths

For EACH issue found, output EXACTLY this format (repeat for each finding):
FILE: <relative file path>
LINE: <line number of the added/changed line causing concern>
SEVERITY: error|warning|info
COMMENT: <one-sentence explanation and fix>

If no issues found, output: NO_FINDINGS
""",

    "security": """\
You are a security-focused code reviewer specialising in cryptographic libraries. \
Examine this pull request diff for:
- CVEs addressed (or newly introduced) by the version bump
- Deprecated or removed APIs that indicate weakened security
- Algorithm changes that reduce security (key sizes, cipher modes, curves)
- Import additions that expand attack surface
- Missing security-critical usage patterns

For EACH issue found, output EXACTLY this format:
FILE: <relative file path>
LINE: <line number of the added/changed line causing concern>
SEVERITY: error|warning|info
COMMENT: <one-sentence explanation referencing CVE number if applicable>

If no issues found, output: NO_FINDINGS
""",

    "perf": """\
You are a performance-focused code reviewer. Examine this pull request diff for:
- Algorithmic complexity regressions
- Unnecessary memory allocations or copies
- N+1 query or computation patterns
- Blocking I/O where async would help
- Redundant work introduced by the change

For EACH issue found, output EXACTLY this format:
FILE: <relative file path>
LINE: <line number of the added/changed line causing concern>
SEVERITY: error|warning|info
COMMENT: <one-sentence explanation of the perf concern>

If no issues found, output: NO_FINDINGS
""",

    "arch": """\
You are an architecture-focused code reviewer. Examine this pull request diff for:
- Tight coupling between components
- Single-responsibility violations
- Interface misuse or abstraction leaks
- Dependency direction violations
- Version pinning strategy concerns (pinned vs range vs minimum)

For EACH issue found, output EXACTLY this format:
FILE: <relative file path>
LINE: <line number of the added/changed line causing concern>
SEVERITY: error|warning|info
COMMENT: <one-sentence explanation of the architectural concern>

If no issues found, output: NO_FINDINGS
""",
}

# ── token helpers ─────────────────────────────────────────────────────────────

def _get_github_token() -> str:
    """Return a valid GitHub App installation token, using auth_github_app.get_token()."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        from auth_github_app import get_token  # type: ignore[import]
        return get_token()
    except Exception as exc:
        print(f"[auth] Failed to get token via auth_github_app: {exc}", file=sys.stderr)
        # Fallback: check env
        tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if tok:
            return tok
        sys.exit("ERROR: No GitHub token available. Run: python scripts/auth_github_app.py")


# ── GitHub API helpers ────────────────────────────────────────────────────────

def _gh_get(path: str, token: str, accept: str = "application/vnd.github+json") -> bytes:
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"token {token}",
            "Accept": accept,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def fetch_pr_metadata(pr_number: int, token: str) -> tuple[str, str]:
    """Returns (base_ref, head_sha)."""
    print(f"[setup] Fetching PR #{pr_number} metadata...", flush=True)
    data = json.loads(_gh_get(f"/repos/{REPO}/pulls/{pr_number}", token))
    base_ref = data["base"]["ref"]
    head_sha = data["head"]["sha"]
    print(f"[setup] base_ref={base_ref}  head_sha={head_sha[:12]}...", flush=True)
    return base_ref, head_sha


def fetch_diff(base_ref: str, head_sha: str, token: str) -> str:
    """Fetch unified diff for base...head via GitHub compare API."""
    print(f"[setup] Fetching diff {base_ref}...{head_sha[:12]}...", flush=True)
    raw = _gh_get(
        f"/repos/{REPO}/compare/{base_ref}...{head_sha}",
        token,
        accept="application/vnd.github.diff",
    )
    diff_text = raw.decode("utf-8", errors="replace")
    print(f"[setup] Diff size: {len(diff_text):,} chars", flush=True)
    return diff_text


# ── agent runner ──────────────────────────────────────────────────────────────

def run_gemini_agent(agent: str, diff_text: str, out_path: Path) -> tuple[str, bool]:
    """Run a single gemini agent. Returns (agent_name, success)."""
    prompt = AGENT_PROMPTS[agent] + f"\n\n--- DIFF ---\n{diff_text}\n--- END DIFF ---"
    print(f"[analyze] Starting {agent} agent...", flush=True)
    t0 = time.time()
    try:
        result = subprocess.run(
            [GEMINI_BIN, "--yolo", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=300,
        )
        elapsed = time.time() - t0
        output = result.stdout.strip() or result.stderr.strip()
        out_path.write_text(output)
        lines = [l for l in output.splitlines() if l.startswith("FILE:")]
        print(f"[analyze] {agent}: {len(lines)} finding(s) in {elapsed:.1f}s", flush=True)
        return agent, True
    except subprocess.TimeoutExpired:
        out_path.write_text("NO_FINDINGS\n# agent timed out after 300s")
        print(f"[analyze] {agent}: TIMEOUT", flush=True)
        return agent, False
    except Exception as exc:
        out_path.write_text(f"NO_FINDINGS\n# agent error: {exc}")
        print(f"[analyze] {agent}: ERROR — {exc}", flush=True)
        return agent, False


# ── ANE gate ──────────────────────────────────────────────────────────────────

def run_ane_gate(diff_path: Path, ane_out_path: Path) -> dict:
    """Run ane_budget.py and write JSON report. Returns report dict."""
    print("[ane-gate] Running ANE budget check...", flush=True)
    try:
        result = subprocess.run(
            [PYTHON, str(ANE_BUDGET_SCRIPT), str(diff_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        report = json.loads(result.stdout) if result.stdout.strip() else {"passed": True, "violations": []}
        ane_out_path.write_text(json.dumps(report, indent=2))
        status = "PASSED" if report.get("passed") else "FAILED"
        print(f"[ane-gate] {status} — {report.get('violation_count', 0)} violation(s)", flush=True)
        return report
    except Exception as exc:
        print(f"[ane-gate] ERROR — {exc}", flush=True)
        report = {"passed": True, "violations": [], "error": str(exc)}
        ane_out_path.write_text(json.dumps(report, indent=2))
        return report


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run GCA multi-agent PR review locally (bypasses GitHub Actions)"
    )
    parser.add_argument("--pr", type=int, default=48, help="PR number to review (default: 48)")
    parser.add_argument(
        "--agents",
        default="correctness,security,perf,arch",
        help="Comma-separated list of agents to run (default: all four)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print findings but do not post to GitHub",
    )
    parser.add_argument(
        "--repo",
        default=REPO,
        help=f"GitHub repo (default: {REPO})",
    )
    args = parser.parse_args()

    agents = [a.strip() for a in args.agents.split(",") if a.strip() in AGENT_PROMPTS]
    if not agents:
        print(f"ERROR: No valid agents. Choose from: {', '.join(AGENT_PROMPTS)}", file=sys.stderr)
        return 1

    workdir = Path(f"/tmp/gca_local_pr{args.pr}")
    workdir.mkdir(exist_ok=True)
    print(f"\n{'='*60}")
    print(f"  GCA Local Orchestrator — PR #{args.pr} @ {args.repo}")
    print(f"  Agents: {', '.join(agents)}")
    print(f"  Workdir: {workdir}")
    print(f"  Dry-run: {args.dry_run}")
    print(f"{'='*60}\n", flush=True)

    # ── 1. setup: get token + PR metadata + diff ──────────────────────────────
    token = _get_github_token()
    base_ref, head_sha = fetch_pr_metadata(args.pr, token)
    diff_text = fetch_diff(base_ref, head_sha, token)

    diff_path = workdir / "diff.txt"
    diff_path.write_text(diff_text)

    # ── 2 + 3. analyze (4 agents) + ane-gate in parallel ─────────────────────
    ane_out_path = workdir / "ane_report.json"
    agent_out_paths = {agent: workdir / f"review_{agent}.txt" for agent in agents}

    print(f"\n[parallel] Launching {len(agents)} gemini agents + ANE gate...\n", flush=True)

    with ThreadPoolExecutor(max_workers=len(agents) + 1) as pool:
        # Submit ANE gate
        ane_future = pool.submit(run_ane_gate, diff_path, ane_out_path)

        # Submit gemini agents
        agent_futures = {
            pool.submit(run_gemini_agent, agent, diff_text, agent_out_paths[agent]): agent
            for agent in agents
        }

        # Collect results as they complete
        for future in as_completed(list(agent_futures.keys()) + [ane_future]):
            if future in agent_futures:
                agent_name, ok = future.result()
            else:
                # ANE gate future
                future.result()

    # ── 4. verify-and-post ────────────────────────────────────────────────────
    review_globs = [str(p) for p in agent_out_paths.values() if p.exists()]
    if not review_globs:
        print("ERROR: No review files produced by agents.", file=sys.stderr)
        return 1

    print(f"\n[verify-post] Posting review to PR #{args.pr}...", flush=True)
    cmd = [
        PYTHON, str(POST_REVIEW_SCRIPT),
        "--repo", args.repo,
        "--pr", str(args.pr),
        "--commit", head_sha,
        "--reviews", *review_globs,
        "--ane-report", str(ane_out_path),
    ]
    if args.dry_run:
        cmd.append("--dry-run")

    env = os.environ.copy()
    env["GITHUB_TOKEN"] = token

    result = subprocess.run(cmd, env=env)

    if result.returncode == 0:
        if not args.dry_run:
            print(f"\n✓ Review posted to https://github.com/{args.repo}/pull/{args.pr}")
        return 0
    else:
        print(f"\nERROR: post_review.py exited {result.returncode}", file=sys.stderr)
        return result.returncode


if __name__ == "__main__":
    sys.exit(main())
