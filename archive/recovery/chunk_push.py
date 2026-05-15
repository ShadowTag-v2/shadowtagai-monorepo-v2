import subprocess
import time

BATCH_SIZE = 15

# Read commits in chronological order (oldest first)
with open("commits.txt") as f:
    commits = [line.strip() for line in f if line.strip()]

total = len(commits)
print(f"Total commits to push: {total}")

chunks = commits[BATCH_SIZE - 1 :: BATCH_SIZE]
if not chunks or commits[-1] != chunks[-1]:
    chunks.append(commits[-1])

for i, commit in enumerate(chunks):
    print(f"Pushing chunk {i + 1}/{len(chunks)} at commit {commit[:8]}")
    cmd = ["git", "push", "origin", f"{commit}:refs/heads/fix-invariants-103-105"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        if "up-to-date" in result.stderr:
            print(" Already up to date.")
            continue
        print(f"Failed to push chunk: {result.stderr}")
        break
    else:
        print(" Success.")
    time.sleep(2)  # Give remote a short pause

print("Chunk push sequence complete.")
