# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import subprocess
import time


def run(cmd):
    print(f"Running: {cmd}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"Command failed: {cmd}")


targets = ["shared", "external_sdks"]

for target in targets:
    if os.path.exists(target):
        dirs = sorted([d for d in os.listdir(target) if os.path.isdir(os.path.join(target, d)) and not d.startswith(".")])
        if not dirs:
            run(f"git add {target}")
            run(f'git commit -m "chore(sync): monorepo chunk {target}"')
            run("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv/bin/python scripts/push_monorepo.py")
            continue

        batch_size = 5
        for i in range(0, len(dirs), batch_size):
            batch = dirs[i : i + batch_size]
            for d in batch:
                run(f"git add {target}/{d}")

            res = subprocess.run("git diff --cached --quiet", shell=True)
            if res.returncode != 0:
                msg = f"chore(sync): monorepo chunk {target} batch {i // batch_size} ({batch[0]} to {batch[-1]})"
                run(f'git commit -m "{msg}"')
                # Using standard git push because gh_app_auth.py ensures the token is alive
                run("git push origin HEAD")
                time.sleep(2)
            else:
                print(f"No changes for batch {i // batch_size}")
