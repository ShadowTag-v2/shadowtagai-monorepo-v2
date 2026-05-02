import argparse


def main():
    parser = argparse.ArgumentParser(description="Sonar API Client")
    parser.add_argument("command", choices=["check-gate", "fetch-issues"])
    parser.add_argument("--severity", type=str, default="BLOCKER,CRITICAL")
    args = parser.parse_args()

    if args.command == "check-gate":
        print("Checking Quality Gate status...")
        # Mock response
        print("Quality Gate: PASSED (mock)")

    elif args.command == "fetch-issues":
        print(f"Fetching issues with severity {args.severity}...")
        # Mock response
        print("No issues found (mock).")


if __name__ == "__main__":
    main()
