# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import sys
import os
import requests


def get_slack_token():
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        try:
            with open(".env") as f:
                for line in f:
                    if line.startswith("SLACK_BOT_TOKEN="):
                        return line.strip().split("=", 1)[1].strip("\"'")
        except FileNotFoundError:
            pass
    return token


def send_message(channel, message):
    token = get_slack_token()
    if not token:
        print("ERROR: SLACK_BOT_TOKEN environment variable not found.")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {"channel": channel, "text": message}

    try:
        response = requests.post("https://slack.com/api/chat.postMessage", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        if data.get("ok"):
            print(f"SUCCESS: Message sent to {channel}")
        else:
            print(f"SLACK ERROR: {data.get('error')}")
            sys.exit(1)
    except Exception as e:
        print(f"API Error: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 4:
        print("Usage: python3 my_slack.py --send <channel> <message>")
        sys.exit(1)

    action = sys.argv[1]

    if action == "--send":
        channel = sys.argv[2]
        message = sys.argv[3]
        send_message(channel, message)
    else:
        print(f"Unknown action: {action}")


if __name__ == "__main__":
    main()
