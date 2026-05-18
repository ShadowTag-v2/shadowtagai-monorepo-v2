import os
import subprocess

def main():
    """
    Initializes the environment and synchronizes epistemic targets.
    """
    print("Initializing Cognitive Architecture...")
    # OBSIDIAN V45: Mandatory sync via bun script
    subprocess.run(["bun", "run", "scripts/omni_epistemic_sync.ts", "SESSION_EVENT", "Python environment initialized and Untitled-1.py created.", "none"], check=True)
    print("Epistemic sync complete. State A active.")

if __name__ == "__main__":
    main()
