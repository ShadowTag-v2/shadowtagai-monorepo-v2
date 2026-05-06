#!/usr/bin/env python3
import os
import subprocess
import sys
import time

# GOVERNED AUTOMATION UNLOCK PROTOCOL
# Authority: ShadowTag Omega v2 User Command
# Timestamp: 2026-01-29

CONTRACT_PATH = os.path.join(
    os.path.dirname(__file__),
    "../src/governance/contracts/GOD_MODE_CONTRACT.md",
)
PASSPHRASE = "I AGREE TO GOVERNED AUTOMATION"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_slow(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def display_contract():
    clear_screen()
    if not os.path.exists(CONTRACT_PATH):
        print(f"[!] Contract not found at {CONTRACT_PATH}")
        return False

    with open(CONTRACT_PATH) as f:
        content = f.read()

    print("-" * 60)
    print(content)
    print("-" * 60)
    return True


def set_autonomy_flags():
    print("\n[*] Setting Automation Environment Variables...")
    
    rc_file = os.path.expanduser("~/.zshrc")
    flags = [
        "export ANTIGRAVITY_AUTOMATION_ENABLED=true",
    ]

    try:
        with open(rc_file, "a") as f:
            f.write("\n# AUTOMATION FLAGS\n")
            f.writelines(f"{flag}\n" for flag in flags)
        print(f"    -> Flags appended to {rc_file}. Please source it or restart shell.")
    except Exception as e:
        print(f"    [!] Failed to update {rc_file}: {e}")


def enable_automation():
    if not display_contract():
        return

    print("\n>>> TO PROCEED, YOU MUST SIGN THE CONTRACT ABOVE. <<<")
    try:
        signature = input(f"Type '{PASSPHRASE}' to authorize: ").strip()
    except KeyboardInterrupt:
        print("\n[!] Aborted.")
        raise SystemExit(1)

    if signature != PASSPHRASE:
        print("\n[!] ACCESS DENIED. Incorrect passphrase.")
        raise SystemExit(1)

    print("\n>>> SIGNATURE ACCEPTED. INITIATING GOVERNED UNLOCK SEQUENCE... <<<\n")
    time.sleep(1)

    # 1. AUTONOMY FLAGS
    set_autonomy_flags()

    print("\n" + "=" * 60)
    print(">>> GOVERNED AUTOMATION ENGAGED. <<<")
    print(">>> Standard review processes remain active. <<<")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    enable_automation()
