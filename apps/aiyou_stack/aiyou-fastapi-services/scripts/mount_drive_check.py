# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import google.auth
from googleapiclient.discovery import build


def check_drive_access():
    print(">>> 🛰️  TESTING OMEGA DRIVE CONNECTION...")

    try:
        # Authenticate using the VM's Service Account
        creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/drive"])
        service = build("drive", "v3", credentials=creds)

        # List first 5 files to prove visibility
        results = (
            service.files().list(pageSize=5, fields="nextPageToken, files(id, name)").execute()
        )
        items = results.get("files", [])

        if not items:
            print("    ✅ Connection Successful (No files found in root).")
        else:
            print("    ✅ Connection Successful! Visible Assets:")
            for item in items:
                print(f"       - {item['name']} ({item['id']})")

    except Exception as e:
        print(f"    ❌ ACCESS DENIED: {e}")
        print("       Did you redeploy the VM with the new scopes?")


if __name__ == "__main__":
    check_drive_access()
