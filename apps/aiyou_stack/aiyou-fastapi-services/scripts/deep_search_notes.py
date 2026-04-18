import base64
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE = "credentials/gmail_token.json"


def get_service():
    if not os.path.exists(TOKEN_FILE):
        print("❌ No token file found.")
        return None
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return build("gmail", "v1", credentials=creds)


def list_labels(service):
    print("\n🏷️  Active Labels:")
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])
    notes_id = None
    for label in labels:
        print(f" - {label['name']} (ID: {label['id']})")
        if label["name"].lower() == "notes":
            notes_id = label["id"]
    return notes_id


def search_deep(service):
    # Queries derived from User Screenshot
    queries = [
        "subject:Cor.26",
        "subject:Mega",
        "subject:Roll-Up",
        "subject:Rollup",
        "subject:Rollups",
        'subject:"Roll ups"',
        "rollup",
        "rollups",
        "label:Notes",  # Broad pull if specific fail
    ]

    unique_msgs = {}

    for q in queries:
        print(f"\n🔍 Searching query: '{q}'...")
        try:
            results = (
                service.users()
                .messages()
                .list(
                    userId="me",
                    q=q,
                    maxResults=10,  # Sample top 10 for each
                )
                .execute()
            )
            messages = results.get("messages", [])
            print(f"   found {len(messages)} messages.")

            for msg in messages:
                unique_msgs[msg["id"]] = msg
        except Exception as e:
            print(f"⚠️ Error querying '{q}': {e}")

    print(f"\n✅ Total Unique Candidates: {len(unique_msgs)}")

    output_file = "ingested_deep_rollup.md"
    with open(output_file, "w") as f:
        f.write("# Deep Retrieval: Rollup Intelligence\n\n")

        for msg_id in unique_msgs:
            try:
                txt = service.users().messages().get(userId="me", id=msg_id).execute()
                payload = txt["payload"]
                headers = payload.get("headers", [])
                subject = next(
                    (h["value"] for h in headers if h["name"] == "Subject"),
                    "No Subject",
                )
                date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")
                txt.get("snippet", "")

                print(f"   Processing: {subject}")

                # Filter strictly for "Roll" or "Cor" to reduce noise from generic searches
                if (
                    "roll" not in subject.lower()
                    and "cor" not in subject.lower()
                    and "mega" not in subject.lower()
                ):
                    continue

                body = ""
                if "parts" in payload:
                    for part in payload["parts"]:
                        if part["mimeType"] == "text/plain":
                            data = part["body"].get("data")
                            if data:
                                body += base64.urlsafe_b64decode(data).decode("utf-8")
                elif "body" in payload:
                    data = payload["body"].get("data")
                    if data:
                        body = base64.urlsafe_b64decode(data).decode("utf-8")

                f.write(f"## {subject}\n")
                f.write(f"**Date**: {date}\n")
                f.write(f"### Content\n{body}\n")
                f.write("---\n")
            except Exception as e:
                print(f"❌ Error processing {msg_id}: {e}")

    print(f"\n💾 Saved matches to {output_file}")


if __name__ == "__main__":
    service = get_service()
    if service:
        list_labels(service)
        search_deep(service)
