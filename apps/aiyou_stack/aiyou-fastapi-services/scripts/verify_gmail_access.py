import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE = "credentials/gmail_token.json"


def verify_access():
    if not os.path.exists(TOKEN_FILE):
        print("❌ No token file found.")
        return

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build("gmail", "v1", credentials=creds)

    print("🔍 Listing last 5 messages in INBOX...")
    try:
        results = (
            service.users().messages().list(userId="me", q="label:INBOX", maxResults=5).execute()
        )
        messages = results.get("messages", [])

        if not messages:
            print("⚠️ No messages found in INBOX.")
        else:
            print(f"✅ Found {len(messages)} messages. Access confirmed.")
            for msg in messages:
                txt = service.users().messages().get(userId="me", id=msg["id"]).execute()
                snippet = txt.get("snippet", "")[0:50]
                print(f" - {msg['id']}: {snippet}...")

    except Exception as e:
        print(f"❌ API Error: {e}")


if __name__ == "__main__":
    verify_access()
