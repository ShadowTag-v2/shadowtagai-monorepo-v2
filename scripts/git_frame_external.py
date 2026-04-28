# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import subprocess

# The raw multiline string provided by the user
RAW_PATHS = """
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/.vscode
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep-mcp
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep-vscode
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep.github.io
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/grep-ast
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/heavy_lift
/Users/pikeymickey/.gemini/antigravity/playground/cosmic-crab/scripts/__pycache__
/Users/pikeymickey/.gemini/antigravity/playground/cosmic-crab/.agent
/Users/pikeymickey/.gemini/antigravity/playground/cosmic-crab/.antigravity
/Users/pikeymickey/.gemini/antigravity/playground/cosmic-crab
/Users/pikeymickey/.gemini/antigravity-demo-archive/antigravity-demo-2026-3-7-25
/Users/pikeymickey/.gemini/antigravity-demo-archive/antigravity-demo-2026-3-7-25/playground
/Users/pikeymickey/.gemini/antigravity/playground
/Users/pikeymickey/.gemini/antigravity-backup-recovered/playground
/Users/pikeymickey
/Users/Deleted Users/pikeymickey
/Users/pikeymickey/antigravity-knowledge
/Users/pikeymickey/Library/Application Support/Claude
/Users/pikeymickey/.antigravity/nascent-apollo
/Users/pikeymickey/.gemini/antigravity-demo-archive/antigravity-demo-2026-3-7-25/brain
/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/
/Users/pikeymickey/.gemini/antigravity-demo-archive/antigravity-demo-2026-3-7-25/code_tracker/active/ShadowTag-v2_bea43616e508f85cade1de6fdee33ec72b5e65b1
/Users/pikeymickey/.gemini/history
"""

DANGER_ZONES = [
    "/Users/pikeymickey",
    "/Users/Deleted Users/pikeymickey",
    "/Users/pikeymickey/Library/Application Support/Claude",
    "/Users/pikeymickey/.gemini/history",
    "",
]


def frame_git_repo(path_str) -> None:
    if path_str in DANGER_ZONES:
        return

    if not os.path.exists(path_str):
        return

    if not os.path.isdir(path_str):
        return

    git_dir = os.path.join(path_str, ".git")

    try:
        if not os.path.exists(git_dir):
            subprocess.run(["git", "init"], cwd=path_str, check=True)

        subprocess.run(["git", "add", "-A"], cwd=path_str, check=False)

        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=path_str,
            capture_output=True,
            text=True,
            check=False,
        )
        status = result.stdout
        if status.strip():
            subprocess.run(
                ["git", "commit", "-m", "chore: autonomous local repository framing"],
                cwd=path_str,
                check=False,
            )
        else:
            pass

    except Exception:
        pass


def main() -> None:
    # Parse and dedup
    lines = RAW_PATHS.splitlines()
    targets = list({line.strip().rstrip(",") for line in lines if line.strip()})

    for t in targets:
        # Resolve 'ast-grep-mcp' typo organically if present
        if t.endswith("ast-grep-mcp/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep-mcp"):
            t = "/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep-mcp"

        frame_git_repo(t)


if __name__ == "__main__":
    main()
