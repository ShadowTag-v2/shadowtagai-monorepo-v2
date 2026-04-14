#!/usr/bin/env python3
import os
import subprocess
import sys
import time

# GOD MODE UNLOCK PROTOCOL
# Authority: ShadowTag Omega v2 User Command
# Timestamp: 2026-01-29

CONTRACT_PATH = os.path.join(
    os.path.dirname(__file__), "../src/governance/contracts/GOD_MODE_CONTRACT.md",
)
PASSPHRASE = "I AM OMEGA"


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


def configure_git():
    print("\n[*] Configuring Git for Silent Ops...")
    # Using 'store' to keep credentials on disk (warning: insecure but requested for autonomy)
    subprocess.run(["git", "config", "--global", "credential.helper", "store"])
    subprocess.run(["git", "config", "--global", "user.email", "redacted@shadowtag-v4.local"])
    subprocess.run(["git", "config", "--global", "user.name", "Wing Commander"])
    print("    -> Git configured.")


def patch_sudoers():
    print("\n[*] Attempting to patch sudoers for passwordless access...")
    try:
        user = os.getenv("USER")
        if not user:
            print("    [!] Could not determine USER environment variable.")
            return

        rule = f"{user} ALL=(ALL) NOPASSWD: ALL"
        sudoers_file = f"/etc/sudoers.d/god_mode_{user}"

        # Check if already patched to avoid redundant password prompts
        if os.path.exists(sudoers_file):
            print("    [i] Sudoers file seems to exist. Skipping re-patch.")
            return

        print(f"    [i] Will require SUDO password to write to {sudoers_file}")
        cmd = f"echo '{rule}' | sudo tee {sudoers_file}"
        subprocess.run(cmd, shell=True, check=True)
        print("    -> Sudoers patched successfully.")
    except subprocess.CalledProcessError:
        print("    [!] Sudo patch failed. You may need to run this manually:")
        print(f"        echo '{rule}' | sudo tee {sudoers_file}")
    except Exception as e:
        print(f"    [!] Unexpected error: {e}")


def set_autonomy_flags():
    print("\n[*] Setting Autonomy Environment Variables...")
    # In a persistent shell, these need to be exported in .zshrc or similar.
    # Here, we append them to the user's RC file if they aren't there.

    rc_file = os.path.expanduser("~/.zshrc")
    flags = [
        "export ANTIGRAVITY_GOD_MODE=true",
        "export ANTIGRAVITY_BROWSER_AUTO_APPROVE=true",
        "export ANTIGRAVITY_YOLO_MODE=true",
        "export GCA_AUTO_APPROVE_CHANGES=true",
    ]

    try:
        with open(rc_file, "a") as f:
            f.write("\n# GOD MODE AUTONOMY FLAGS\n")
            f.writelines(f"{flag}\n" for flag in flags)
        print(f"    -> Flags appended to {rc_file}. Please source it or restart shell.")
    except Exception as e:
        print(f"    [!] Failed to update {rc_file}: {e}")


def enable_god_mode():
    if not display_contract():
        return

    print("\n>>> TO PROCEED, YOU MUST SIGN THE CONTRACT ABOVE. <<<")
    try:
        signature = input(f"Type '{PASSPHRASE}' to authorize: ").strip()
    except KeyboardInterrupt:
        print("\n[!] Aborted.")
        sys.exit(1)

    if signature != PASSPHRASE:
        print("\n[!] ACCESS DENIED. Incorrect passphrase.")
        sys.exit(1)

    print("\n>>> SIGNATURE ACCEPTED. INITIATING UNLOCK SEQUENCE... <<<\n")
    time.sleep(1)

    # 1. GIT AUTOMATION
    configure_git()

    # 2. SUDO PERMISSIONS
    patch_sudoers()

    # 3. AUTONOMY FLAGS
    set_autonomy_flags()

    print("\n" + "=" * 60)
    print(">>> GOD MODE ENGAGED. <<<")
    print(">>> The 'gca_autopilot_finish.py' script is now available for auto-commits. <<<")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    enable_god_mode()
