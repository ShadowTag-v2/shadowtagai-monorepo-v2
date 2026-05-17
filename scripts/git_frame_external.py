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


def frame_git_repo(path_str):
  if path_str in DANGER_ZONES:
    print(
      f"⏭️ HARD SKIP: {path_str} (Danger zone - Prevents committing OS root secrets)"
    )
    return

  if not os.path.exists(path_str):
    print(f"❌ NOT FOUND: {path_str}")
    return

  if not os.path.isdir(path_str):
    print(f"⏭️ SKIPPED: {path_str} is a file, not a directory.")
    return

  print(f"\n--- Framing: {path_str} ---")
  git_dir = os.path.join(path_str, ".git")

  try:
    if not os.path.exists(git_dir):
      print("📦 Initializing local git repository...")
      subprocess.run(["git", "init"], cwd=path_str, check=True)

    subprocess.run(["git", "add", "-A"], cwd=path_str, check=False)

    status = subprocess.getoutput(f"cd '{path_str}' && git status --porcelain")
    if status.strip():
      print("💾 Committing snapshot locally...")
      subprocess.run(
        ["git", "commit", "-m", "chore: autonomous local repository framing"],
        cwd=path_str,
        check=False,
      )
    else:
      print("✅ Already tracked and clean. No new local changes.")

    print("✅ Local framing sequence complete.")

  except Exception as e:
    print(f"⚠️ Error framing {path_str}: {e}")


def main():
  print("Initiating Local Git Framing Sequence...")

  # Parse and dedup
  lines = RAW_PATHS.splitlines()
  targets = list(set([line.strip().rstrip(",") for line in lines if line.strip()]))

  for t in targets:
    # Resolve 'ast-grep-mcp' typo organically if present
    if t.endswith(
      "ast-grep-mcp/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep-mcp"
    ):
      t = (
        "/Users/pikeymickey/.gemini/antigravity/playground/molten-universe/ast-grep-mcp"
      )

    frame_git_repo(t)


if __name__ == "__main__":
  main()
