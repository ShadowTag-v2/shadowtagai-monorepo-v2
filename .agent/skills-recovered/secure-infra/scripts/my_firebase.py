# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import sys
import subprocess


def run_firebase_cmd(args):
    """
    Executes the native firebase-tools CLI.
    Requires firebase-tools to be installed globally (`npm install -g firebase-tools`).
    """
    cmd = ["npx", "firebase"] + args
    print(f"Executing: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("--- FIREBASE OUTPUT ---")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("--- FIREBASE ERROR ---")
        print(e.stderr)
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 my_firebase.py <firebase_cli_args...>")
        print("Example: python3 my_firebase.py deploy --only hosting")
        sys.exit(1)

    args = sys.argv[1:]
    success = run_firebase_cmd(args)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
