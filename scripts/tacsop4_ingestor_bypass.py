#!/usr/bin/env python3
"""
TACSOP 4 Skill Ingestor Bypass
Programmatically bypasses interactive prompts when ingesting skills.
"""

import pexpect
import sys


def run_ingestor(command):
  print(f"Running ingestor: {command}")

  # We use pexpect to spawn the process
  # Adjust the timeout based on expected network latency
  child = pexpect.spawn(command, encoding="utf-8", timeout=30)

  try:
    # We want to log the interaction to stdout
    child.logfile = sys.stdout

    # Loop to handle interactive prompts
    while True:
      # Add patterns here based on the exact prompts given by the CLI
      # e.g., "Proceed?", "Select an option:", etc.
      index = child.expect(
        [
          r"(?i)proceed\?.*\[y/N\]",
          r"(?i)select a skill",
          r"(?i)overwrite\?.*\[y/N\]",
          pexpect.EOF,
          pexpect.TIMEOUT,
        ]
      )

      if index == 0:
        child.sendline("y")
      elif index == 1:
        # Provide the default selection or type
        child.sendline("")  # Press enter
      elif index == 2:
        child.sendline("y")
      elif index == 3:
        print("\nIngestor completed.")
        break
      elif index == 4:
        print("\nTimeout waiting for ingestor.")
        break

  except Exception as e:
    print(f"Error occurred: {e}")
  finally:
    child.close()
    sys.exit(child.exitstatus if child.exitstatus is not None else 1)


if __name__ == "__main__":
  # Example command from Motor Cortex reflexes
  # npx skills add google/skills
  cmd = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "npx skills add google/skills"

  # Ensure CI=true is NOT set if it completely disables the tool instead of using default,
  # but generally we are trying to bypass what can't be handled by CI=true.
  # We'll pass the current environment.
  run_ingestor(cmd)
