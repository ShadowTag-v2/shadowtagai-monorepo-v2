#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/drive.readonly",
]
CLIENT_SECRET_FILE = "/Users/pikeymickey/Downloads/client_secret_767252945109-g8e1bdmvl4u2ff4mkbvhcsbbduh6kv7v.apps.googleusercontent.com.json"


def main() -> None:
    if not os.path.exists(CLIENT_SECRET_FILE):
        return

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    with open("token.json", "w") as token:
        token.write(creds.to_json())


if __name__ == "__main__":
    main()
