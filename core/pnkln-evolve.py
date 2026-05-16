# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
# pnkln-evolve.py — Agent-editable core
import subprocess
import time


def run_judge6_experiment():
    print("Running 5-minute Judge-6 evolution experiment...")
    start = time.time()

    # Example evolution: tweak cinematic prompt or add skill
    try:
        subprocess.run(["./scripts/judge6.sh", "--evolve"], check=True)
    except subprocess.CalledProcessError:
        pass  # Allow script to proceed to checking report

    duration = time.time() - start
    print(f"Experiment completed in {duration:.1f}s")

    # Fitness from Judge-6 report
    try:
        with open("judge6-report.md") as f:
            report = f.read()
        if "APPROVED" in report and "High" not in report:
            print("✓ Improvement kept")
            subprocess.run(["git", "add", "."])
            subprocess.run(["git", "commit", "-m", "pnkln-evolve: improvement"])
            return True
        else:
            print("✗ Reverting")
            subprocess.run(["git", "reset", "--hard", "HEAD"])
            return False
    except FileNotFoundError:
        print("✗ Report missing, reverting")
        subprocess.run(["git", "reset", "--hard", "HEAD"])
        return False


if __name__ == "__main__":
    run_judge6_experiment()
