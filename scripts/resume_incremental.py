import os
import subprocess
import time


def run(cmd) -> None:
    res = subprocess.run(cmd, shell=True)  # nosec B602 — intentional shell for git/system ops
    if res.returncode != 0:
        pass


# Define all the chunks we want to push
dirs_libs = sorted([d for d in os.listdir("libs") if os.path.isdir(os.path.join("libs", d)) and not d.startswith(".")])
dirs_apps = sorted([d for d in os.listdir("apps") if os.path.isdir(os.path.join("apps", d)) and not d.startswith(".")])
dirs_external = sorted([d for d in os.listdir("external_sdks") if os.path.isdir(os.path.join("external_sdks", d)) and not d.startswith(".")])


def process_batch(parent, dirs, batch_size=2) -> None:
    for i in range(0, len(dirs), batch_size):
        batch = dirs[i : i + batch_size]
        for d in batch:
            run(f"git add {parent}/{d}")

        # Check if there's actually anything staged
        res = subprocess.run("git diff --cached --quiet", shell=True)  # nosec B602 — intentional shell for git/system ops
        if res.returncode != 0:
            # Changes exist!
            msg = f"chore(sync): monorepo chunk {parent} batch {i // batch_size} ({batch[0]} to {batch[-1]})"
            run(f'git commit -m "{msg}"')
            run(".venv/bin/python scripts/push_monorepo.py")
            time.sleep(1)
        else:
            pass


process_batch("libs", dirs_libs)

process_batch("external_sdks", dirs_external)

process_batch("apps", dirs_apps)

# Then add the rest of the workspace (scripts, root files, docs)
run("git add .")
res = subprocess.run("git diff --cached --quiet", shell=True)  # nosec B602 — intentional shell for git/system ops
if res.returncode != 0:
    run('git commit -m "chore(sync): monorepo chunk FINAL (root, docs, scripts)"')
    run(".venv/bin/python scripts/push_monorepo.py")
