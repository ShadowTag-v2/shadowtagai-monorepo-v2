# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
# meta-evolve.py — Agent-editable meta-layer
import subprocess
import time


def run_meta_experiment():
  print("Running 5-minute meta-evolution experiment...")
  start = time.time()

  # Agent can edit program.md or evolve.py here
  with open("program.md", "a") as f:
    f.write(f"\n# Meta-update {time.strftime('%Y-%m-%d %H:%M')}\n")

  try:
    subprocess.run(["python", "core/pnkln-evolve.py"], check=True)
  except subprocess.CalledProcessError:
    pass

  duration = time.time() - start
  print(f"Meta-experiment completed in {duration:.1f}s")

  # Judge-6 decides if the meta-change survives
  result = subprocess.run(
    ["./scripts/judge6.sh", "--full-audit"], capture_output=True, text=True
  )
  if "APPROVED" in result.stdout and "High" not in result.stdout:
    print("✓ Meta-improvement kept")
    subprocess.run(
      ["git", "add", "program.md", "core/pnkln-evolve.py", "core/meta-evolve.py"]
    )
    subprocess.run(["git", "commit", "-m", "pnkln-meta-evolve: improvement"])
    return True
  else:
    print("✗ Reverting meta-change")
    subprocess.run(["git", "reset", "--hard", "HEAD"])
    return False


if __name__ == "__main__":
  run_meta_experiment()
