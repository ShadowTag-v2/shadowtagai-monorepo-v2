# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import subprocess
import time


def run_command(command, check=True):
    try:
        # Use shell=True for complex commands, capture output
        result = subprocess.run(command, shell=True, check=check, text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Command failed: {command}")
        print(f"   Error: {e.stderr}")
        return None


def get_changed_files():
    # Only get Untracked (??) and Modified (M) and Added (A)
    output = run_command("git status --porcelain")
    if not output:
        return []

    files = []
    for line in output.split("\n"):
        if not line.strip():
            continue
        # Status code is first 2 chars
        code = line[:2]
        path = line[3:]
        # Remove quotes
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]

        # Skip if ignored (though porcelain shouldn't show ignored unless -u)
        if code == "!!":
            continue

        files.append(path)
    return files


def batch_push(batch_size=10):
    files = get_changed_files()
    total_files = len(files)
    print(f"🚀 Found {total_files} pending files.")

    if total_files == 0:
        print("✅ Clean working directory. Pushing any committed changes...")
        run_command("git push", check=False)
        return

    # Process in chunks
    for i in range(0, total_files, batch_size):
        batch = files[i : i + batch_size]
        print(f"\n📦 Batch {i // batch_size + 1}: Processing {len(batch)} files...")

        # 1. ADD (Robustly)
        # We add files one by one or in small groups to handle errors gracefully
        added_count = 0
        for f in batch:
            # Check if file exists (might be deleted 'D')
            if (
                not os.path.exists(f) and "->" not in f
            ):  # '->' check for renames just in case, though porcelain usually handles
                # If deleted, git add usually handles it if we pass the path
                pass

            # Try add
            safe_file = f'"{f}"'
            if run_command(f"git add {safe_file}", check=False) is not None:
                added_count += 1

        if added_count == 0:
            print("   ⚠️ No files added in this batch. Skipping commit.")
            continue

        # 2. COMMIT
        commit_msg = f"feat(core): Cloud Uplink Batch {i + 1}-{i + len(batch)}"
        print(f"   💾 Committing: {commit_msg}")
        run_command(f'git commit -m "{commit_msg}"', check=False)

        # 3. PUSH
        print("   ☁️ Pushing to GCloud...")
        if run_command("git push", check=False) is None:
            print("   ⚠️ Push failed. Waiting 5s...")
            time.sleep(5)
            # Try one more time
            run_command("git push", check=False)
        else:
            print("   ✅ Push successful.")


if __name__ == "__main__":
    # Ensure gcloud helper
    run_command("git config credential.helper gcloud.sh", check=False)
    batch_push(10)
