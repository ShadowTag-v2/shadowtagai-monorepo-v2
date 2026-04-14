"""Gmail Sent Folder Ingestor
Target: redacted@shadowtag-v4.local
Purpose: Extract business & tech plans from Sent Items.
"""

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = "credentials/client_secret.json"
TOKEN_FILE = "credentials/gmail_token.json"
OUTPUT_FILE = "ingested_gmail_sent.md"


def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Missing {CREDENTIALS_FILE}. Please download OAuth 2.0 Client ID from GCP Console.",
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            # Reverting to local server (Desktop App flow)
            # User must ensure Client ID is 'Desktop App' type in GCP Console
            # FORCE PORT 8080 for Web Client Whitelisting
            creds = flow.run_local_server(port=8080)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def ingest_sent_folder():
    service = get_service()
    print("🔍 Scanning SENT folder...")

    # query for sent messages
    results = service.users().messages().list(userId="me", q="label:SENT", maxResults=50).execute()
    messages = results.get("messages", [])

    if not messages:
        print("No messages found.")
        return

    with open(OUTPUT_FILE, "w") as f:
        f.write("# Gmail Sent Folder Ingestion\n")
        f.write("Account: redacted@shadowtag-v4.local\n\n")

        for msg in messages:
            txt = service.users().messages().get(userId="me", id=msg["id"]).execute()
            payload = txt["payload"]
            headers = payload["headers"]
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")

            print(f"Processing: {subject}")

            snippet = txt.get("snippet", "")

            # Simple heuristic for "Biz or Tech Plans"
            keywords = [
                "plan",
                "strategy",
                "architecture",
                "budget",
                "proposal",
                "draft",
                "roadmap",
                "tech",
                "stack",
            ]
            if any(k in subject.lower() or k in snippet.lower() for k in keywords):
                f.write(f"## {subject}\n")
                f.write(f"**Date**: {date}\n")
                f.write(f"**Snippet**: {snippet}\n")
                f.write("---\n")

    print(f"✅ Ingestion Complete. Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    # Ensure credentials dir exists
    os.makedirs("credentials", exist_ok=True)
    try:
        ingest_sent_folder()
    except Exception as e:
        print(f"❌ Error: {e}")
