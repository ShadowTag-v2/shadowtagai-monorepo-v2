# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import subprocess
import time


def run(cmd):
    print(f"Running: {cmd}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"Command failed: {cmd}")


dirs = sorted([d for d in os.listdir("libs") if os.path.isdir(os.path.join("libs", d)) and not d.startswith(".")])
batch_size = 5

for i in range(0, len(dirs), batch_size):
    batch = dirs[i : i + batch_size]
    for d in batch:
        run(f"git add libs/{d}")

    # Check if there's actually anything staged
    res = subprocess.run("git diff --cached --quiet", shell=True)
    if res.returncode != 0:
        # Changes exist!
        msg = f"chore(sync): monorepo chunk libs batch {i // batch_size} ({batch[0]} to {batch[-1]})"
        run(f'git commit -m "{msg}"')
        run("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv/bin/python scripts/push_monorepo.py")
        time.sleep(2)
    else:
        print(f"No changes for batch {i // batch_size}")
