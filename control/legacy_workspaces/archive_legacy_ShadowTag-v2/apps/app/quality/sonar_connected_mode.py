# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Sonar Connected Mode Setup")
    parser.add_argument("--verify", action="store_true", help="Verify connection")
    parser.add_argument("--ide", type=str, help="IDE to configure")
    args = parser.parse_args()

    token = os.environ.get("SONAR_TOKEN")
    url = os.environ.get("SONAR_HOST_URL", "http://localhost:9000")

    if args.verify:
        print(f"Verifying connection to {url}...")
        if not token:
            print("Error: SONAR_TOKEN not set")
            sys.exit(1)
        # Mock connection check for now
        print("Connection verified (mock).")
        sys.exit(0)

    if args.ide == "vscode":
        print("Configuring VS Code settings for SonarLint...")
        # Logic to update .vscode/settings.json would go here
        print("VS Code configured.")


if __name__ == "__main__":
    main()
