import sys
import os
import json
import requests


def get_github_token():
    # Attempt to load from environment or typical .env location
    token = os.environ.get("GITHUB_PAT")
    if not token:
        # Fallback for agent execution
        try:
            with open(".env") as f:
                for line in f:
                    if line.startswith("GITHUB_PAT="):
                        return line.strip().split("=", 1)[1].strip("\"'")
        except FileNotFoundError:
            pass
    return token


def github_request(method, endpoint, payload=None):
    token = get_github_token()
    if not token:
        print("ERROR: GITHUB_PAT environment variable not found.")
        sys.exit(1)

    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    url = f"https://api.github.com{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=payload)
        else:
            print(f"ERROR: Unsupported method {method}")
            sys.exit(1)

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"GitHub API Error: {e}")
        if e.response is not None:
            print(e.response.text)
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 my_github.py --action <action> [options]")
        sys.exit(1)

    action = sys.argv[2]

    if action == "list_issues":
        # Usage: python3 my_github.py --action list_issues --repo owner/repo
        if len(sys.argv) >= 5 and sys.argv[3] == "--repo":
            repo = sys.argv[4]
            data = github_request("GET", f"/repos/{repo}/issues")
            print(
                json.dumps([{"number": i["number"], "title": i["title"]} for i in data], indent=2)
            )
        else:
            print("Missing --repo owner/repo")

    # Add more actions (create_pr, comment, etc.) as needed by the agent.
    else:
        print(f"Unknown action: {action}")


if __name__ == "__main__":
    main()
