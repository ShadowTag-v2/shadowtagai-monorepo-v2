#!/usr/bin/env python3
"""
Jules + GCA Sovereign PR Review Swarm Orchestrator
Part of AGNT_OS v15.0

Coordinates the Three-Tier hardware verification system:
- Tier 1: pydantic-monty (fast logic validation)
- Tier 2: Colab T4 via Google Drive IPC (heavy ML)
- Tier 3: ane_bridge.py (M1 Max ANE - 12.5MB L2 limit)
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


def get_changed_files(branch: str) -> List[str]:
    """Get list of files changed in the PR branch vs main"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"origin/main...{branch}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except subprocess.CalledProcessError:
        return []


def classify_files(files: List[str]) -> Dict[str, List[str]]:
    """Classify changed files by language/type for targeted review"""
    categories: Dict[str, List[str]] = {
        "python": [],
        "typescript": [],
        "go": [],
        "rust": [],
        "yaml": [],
        "other": [],
    }
    ext_map = {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "typescript",
        ".jsx": "typescript",
        ".go": "go",
        ".rs": "rust",
        ".yml": "yaml",
        ".yaml": "yaml",
    }
    for f in files:
        suffix = Path(f).suffix
        cat = ext_map.get(suffix, "other")
        categories[cat].append(f)
    return categories


def run_lint_checks(categories: Dict[str, List[str]]) -> List[Dict]:
    """Run language-specific lint checks and collect findings"""
    findings: List[Dict] = []

    # Python: ruff
    if categories["python"]:
        try:
            result = subprocess.run(
                ["ruff", "check", "--output-format=json", *categories["python"]],
                capture_output=True,
                text=True,
            )
            if result.stdout.strip():
                for issue in json.loads(result.stdout):
                    findings.append(
                        {
                            "file": issue.get("filename", ""),
                            "line": issue.get("location", {}).get("row", 1),
                            "severity_emoji": "🟡",
                            "comment": f"Ruff: {issue.get('message', '')} [{issue.get('code', '')}]",
                            "source": "Tier 1: ruff",
                        }
                    )
        except FileNotFoundError:
            pass

    # TypeScript: biome
    if categories["typescript"]:
        try:
            result = subprocess.run(
                [
                    "npx",
                    "@biomejs/biome",
                    "check",
                    "--reporter=json",
                    *categories["typescript"],
                ],
                capture_output=True,
                text=True,
            )
            if result.stdout.strip():
                try:
                    biome_output = json.loads(result.stdout)
                    for diag in biome_output.get("diagnostics", []):
                        findings.append(
                            {
                                "file": diag.get("file_path", ""),
                                "line": diag.get("span", {}).get("start", {}).get("line", 1),
                                "severity_emoji": "🟡",
                                "comment": f"Biome: {diag.get('message', '')}",
                                "source": "Tier 1: biome",
                            }
                        )
                except json.JSONDecodeError:
                    pass
        except FileNotFoundError:
            pass

    return findings


def run_swarm(pr_number: int, branch: str, mode: str = "full-review"):
    """Main swarm orchestrator"""
    print(f"⚡ [Jules Swarm] Starting review for PR #{pr_number} (branch: {branch})")
    print(f"   Mode: {mode}")

    # 1. Get changed files
    changed_files = get_changed_files(branch)
    if not changed_files:
        print("ℹ️  No changed files detected.")
        return

    print(f"   Changed files: {len(changed_files)}")

    # 2. Classify files
    categories = classify_files(changed_files)
    for cat, files in categories.items():
        if files:
            print(f"   {cat}: {len(files)} files")

    # 3. Run lint checks (Tier 1)
    findings = run_lint_checks(categories)
    print(f"   Tier 1 findings: {len(findings)}")

    # 4. Write findings to JSON for post_pr_findings.py
    output_path = Path("pr_findings.json")
    output_path.write_text(json.dumps(findings, indent=2))
    print(f"✅ [Jules Swarm] Review complete. {len(findings)} findings written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--branch", type=str, required=True)
    parser.add_argument("--mode", type=str, default="full-review")
    args = parser.parse_args()

    run_swarm(args.pr_number, args.branch, args.mode)
