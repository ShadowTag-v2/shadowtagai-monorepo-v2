#!/usr/bin/env python3
"""GCA Batch PR Reviewer — Review and merge multiple PRs in sequence.

Usage:
    python3 scripts/run_gca_batch.py --prs 44,45,46,47,49,50,53,54,55
    python3 scripts/run_gca_batch.py --prs 44,45,46 --merge     # review + auto-merge clean PRs
    python3 scripts/run_gca_batch.py --prs 44,45 --dry-run       # review only, no GitHub posting
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

from auth_github_app import get_token  # type: ignore[import]


def _gh_api(method: str, path: str, token: str, body: dict | None = None) -> dict:
    """Make a GitHub API call."""
    import urllib.request

    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        method=method,
        data=data,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "message": e.read().decode()[:200]}


def review_pr(pr_num: int, token: str, dry_run: bool = False) -> dict:
    """Run GCA review on a single PR."""
    import subprocess

    print(f"\n{'='*60}")
    print(f"  Reviewing PR #{pr_num}")
    print(f"{'='*60}")

    cmd = [sys.executable, os.path.join(SCRIPTS_DIR, "run_gca_local.py"), "--pr", str(pr_num)]
    if dry_run:
        cmd.append("--dry-run")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    # Parse findings
    output = result.stdout + result.stderr
    findings = [l for l in output.splitlines() if "finding(s)" in l]
    total_findings = sum(int(l.split(":")[1].strip().split()[0]) for l in findings if ":" in l)

    print(f"  PR #{pr_num}: {total_findings} total findings")

    return {
        "pr": pr_num,
        "findings": total_findings,
        "output": output[-500:] if output else "",
        "returncode": result.returncode,
    }


def merge_pr(pr_num: int, token: str, title: str) -> dict:
    """Merge a PR via squash."""
    result = _gh_api(
        "PUT",
        f"/repos/ShadowTag-v2/Monorepo-Uphillsnowball/pulls/{pr_num}/merge",
        token,
        {"commit_title": title, "merge_method": "squash"},
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch GCA PR review + optional merge")
    parser.add_argument("--prs", required=True, help="Comma-separated PR numbers")
    parser.add_argument("--merge", action="store_true", help="Auto-merge PRs with 0 findings")
    parser.add_argument("--dry-run", action="store_true", help="Review only, no GitHub posting")
    args = parser.parse_args()

    pr_nums = [int(p.strip()) for p in args.prs.split(",") if p.strip()]
    print(f"\nGCA Batch Review — {len(pr_nums)} PRs: {pr_nums}")
    print(f"Merge: {args.merge} | Dry-run: {args.dry_run}\n")

    token = get_token()
    results = []

    for pr_num in pr_nums:
        try:
            # Get PR metadata
            pr_data = _gh_api("GET", f"/repos/ShadowTag-v2/Monorepo-Uphillsnowball/pulls/{pr_num}", token)
            if pr_data.get("state") != "open":
                print(f"  PR #{pr_num}: SKIP (state={pr_data.get('state', 'unknown')})")
                continue
            if pr_data.get("merged"):
                print(f"  PR #{pr_num}: SKIP (already merged)")
                continue

            title = pr_data.get("title", f"PR #{pr_num}")
            head_ref = pr_data.get("head", {}).get("ref", "")

            # Check if head branch exists
            if not head_ref:
                print(f"  PR #{pr_num}: SKIP (head branch deleted)")
                _gh_api("PATCH", f"/repos/ShadowTag-v2/Monorepo-Uphillsnowball/pulls/{pr_num}", token, {"state": "closed"})
                continue

            # Run review
            result = review_pr(pr_num, token, dry_run=args.dry_run)
            results.append(result)

            # Auto-merge if clean and --merge flag set
            if args.merge and not args.dry_run and result["findings"] == 0:
                print(f"  PR #{pr_num}: Auto-merging (0 findings)...")
                # Try update branch first
                _gh_api("PUT", f"/repos/ShadowTag-v2/Monorepo-Uphillsnowball/pulls/{pr_num}/update-branch", token, {"update_method": "merge"})
                time.sleep(3)
                merge_result = merge_pr(pr_num, token, f"{title} (#{pr_num})")
                print(f"  Merge result: {merge_result.get('message', merge_result.get('error', '?'))}")

        except Exception as e:
            print(f"  PR #{pr_num}: ERROR — {e}")
            results.append({"pr": pr_num, "findings": -1, "error": str(e)})

    # Summary
    print(f"\n{'='*60}")
    print(f"  BATCH SUMMARY — {len(results)} PRs reviewed")
    print(f"{'='*60}")
    for r in results:
        status = "✅ CLEAN" if r.get("findings", -1) == 0 else f"⚠️ {r.get('findings', '?')} findings"
        print(f"  PR #{r['pr']}: {status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
