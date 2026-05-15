#!/usr/bin/env python3
import pexpect
import sys


def main():
  print("Starting skill ingestor with pexpect...")
  # Spawn the interactive command
  child = pexpect.spawn("npx skills add google/skills", encoding="utf-8")

  # Enable logging to stdout so we can see what's happening
  child.logfile = sys.stdout

  try:
    # Wait for the "Select skills to install" prompt
    child.expect(r"Select skills to install", timeout=30)

    # We assume the default behavior (or we can send space/enter to select/confirm)
    # Send 'a' to toggle all, or just Enter to proceed with defaults
    # Often these prompts use space to toggle, enter to submit.
    print("\n[pexpect] Reached selection prompt. Sending ENTER to accept defaults/all.")
    child.sendline("\r")  # send Enter

    # Wait for EOF
    child.expect(pexpect.EOF, timeout=120)
    print("\n[pexpect] Command completed.")
  except pexpect.TIMEOUT:
    print("\n[pexpect] Timed out waiting for prompt!")
    sys.exit(1)
  except Exception as e:
    print(f"\n[pexpect] Error: {e}")
    sys.exit(1)


if __name__ == "__main__":
  main()
