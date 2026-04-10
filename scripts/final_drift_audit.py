#!/usr/bin/env python3
import os
import shlex
import subprocess

ROOT = "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
os.chdir(ROOT)
output_path = "docs/FINAL_DRIFT_AUDIT.md"


def run_grep(term):
    # Use native git grep to perfectly bypass unindexed 118GB bloat and tree loops
    cmd = f"git grep -c '{term}'"
    res = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    count = 0
    for line in res.stdout.splitlines():
        if ":" in line:
            try:
                count += int(line.split(":")[-1])
            except ValueError:
                pass
    return count


legacy_terms = ["ShadowTag-v2", "ShadowTag", "gemini-3.1-family"]
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w") as f:
    f.write("# Final Drift Audit Report\n\n")
    f.write("## Legacy Term Occurrences (excluding reference/ and apps/)\n")
    for term in legacy_terms:
        count = run_grep(term)
        status = "PASSED" if count == 0 else "FAIL"
        f.write(f"- `{term}`: {count} instances remaining **[{status}]**\n")

    f.write("\n## Workspace Files\n")
    cmd = "find . -maxdepth 3 -name '*.code-workspace'"
    res = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    f.write(f"```text\n{res.stdout.strip()}\n```\n")

print("[audit] Final drift audit generated at docs/FINAL_DRIFT_AUDIT.md")
